from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
from .models import Route, GroupRideIntersection
from groups.models import Group, Membership
# WICHTIG: MultiLineString und LineString statt Polygon importieren
from django.contrib.gis.geos import MultiLineString, LineString

@receiver(post_save, sender=Route)
def update_group_intersections(sender, instance, created, **kwargs):
    if not instance.geom or not instance.start_time or not instance.group_id:
        return

    time_window_start = instance.start_time - timedelta(minutes=90)
    time_window_end = (instance.end_time or instance.start_time) + timedelta(minutes=90)
    route_date = instance.start_time.date() 

    group_ids = instance.group_id if isinstance(instance.group_id, list) else []

    for g_id in group_ids:
        try:
            group = Group.objects.get(pk=g_id)
        except Group.DoesNotExist:
            continue

        # Nur aktuelle "Joined"-Mitglieder zählen als Gruppe
        joined_user_ids = set(
            Membership.objects.filter(group=group, status='Joined').values_list('user_id', flat=True)
        )

        # Ein Gruppen-Schnittpunkt braucht mindestens 2 Mitglieder
        if len(joined_user_ids) < 2:
            continue

        # WICHTIG: Wir holen ALLE relevanten Routen für dieses Zeitfenster (inklusive der gerade gespeicherten!)
        # Nur Routen von aktuellen Joined-Mitgliedern berücksichtigen
        all_window_routes = Route.objects.filter(
            group_id__contains=g_id,
            start_time__gte=time_window_start,
            start_time__lte=time_window_end,
            geom__isnull=False,
            user_id__in=joined_user_ids
        )

        # Pro Mitglied genau eine Route behalten (die früheste im Fenster),
        # damit Mehrfach-Uploads eines Mitglieds nicht doppelt zählen
        routes_by_user = {}
        for route in all_window_routes.order_by('start_time', 'strecken_id'):
            routes_by_user.setdefault(route.user_id, route)

        # Nur wenn WIRKLICH ALLE Joined-Mitglieder an diesem Tag/Cluster dabei waren,
        # gibt es eine gemeinsame Gruppenfahrt
        if joined_user_ids - routes_by_user.keys():
            continue

        selected_routes = list(routes_by_user.values())

        # 1. Wir starten mit dem gebufferten Geometrie-Schlauch der ERSTEN Route (25m Puffer für GPS-Toleranz!)
        first_route = selected_routes[0]
        # In signals.py bei allen .buffer() Aufrufen:
        shared_geom = first_route.geom.transform(3857, clone=True).buffer(25.0)

        # 2. Jetzt schneiden wir iterativ (.intersection) jeden weiteren 25m-Schlauch ab!
        # Was nicht innerhalb der Toleranz von ALLEN gefahren wurde, fliegt hier raus.
        for other_route in selected_routes[1:]:
            other_geom_buffered = other_route.geom.transform(3857, clone=True).buffer(25.0)
            shared_geom = shared_geom.intersection(other_geom_buffered)

            # Abbruch-Optimierung: Wenn der gemeinsame Schlauch leer wird, gab es keine gemeinsame Strecke.
            if shared_geom.empty:
                break

        # --- DER KEKSAUSTECHER-TRICK ---
        # 3. Wir nehmen die originale, haardünne GPS-Linie von Fahrer 1 (ohne Puffer!)
        first_line_metric = first_route.geom.transform(3857, clone=True)
        
        # 4. Wir stechen mit dem Schlauch genau den Teil der Linie aus, wo alle zusammen waren!
        center_line_metric = first_line_metric.intersection(shared_geom)

        # 5. In WGS84 (4326) zurückwandern
        final_geom_4326 = center_line_metric.transform(4326, clone=True) if not center_line_metric.empty else None

        # 6. Für die Datenbank sicherstellen, dass es immer ein MultiLineString ist
        if isinstance(final_geom_4326, LineString):
            final_geom_4326 = MultiLineString(final_geom_4326)

        # 7. Datenbank-Eintrag holen oder erstellen und ÜBERSCHREIBEN (nicht .union()!)
        group_intersection, _ = GroupRideIntersection.objects.get_or_create(
            group=group,
            date=route_date
        )
        
        group_intersection.geom = final_geom_4326
        group_intersection.save()