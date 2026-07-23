"""Gemeinsame Berechnungslogik für die Leistungs-Ansicht (Puls/Tempo/Watt), genutzt von:
- routes/signals.py (inkrementelles Update beim Hochladen einer neuen Route)
- routes/management/commands/backfill_performance_buckets.py (einmaliger Backfill bestehender Routen)

Zerlegt EINE Route in kleine Segmente und ordnet jedes einer Rasterzelle (siehe
PERFORMANCE_GRID_SIZE_METERS) zu, mit Puls-/Tempo-/Watt-Wert pro Segment. Die eigentliche
Persistierung (Summen/Counts in UserPerformanceBucket erhöhen) übernimmt der Aufrufer -
dieses Modul liefert nur die reinen Beiträge einer einzelnen Route.
"""

from django.utils.dateparse import parse_datetime

# Rasterweite für die räumliche Mittelung (in Metern, EPSG:3857). Analog zum 25m-GPS-Toleranz-
# Puffer in routes/signals.py, hier als Straßen-Granularität für die Bucket-Zuordnung.
PERFORMANCE_GRID_SIZE_METERS = 20

# Obergrenze für plausible Radgeschwindigkeit - filtert GPS-/Zeitstempel-Ausreißer heraus, die
# sonst die Farbskala verzerren würden.
MAX_PLAUSIBLE_SPEED_KMH = 100

# Handelsübliche GPS-Geräte/Handys haben eine Positionsgenauigkeit von ca. 3-5m. Steht man z.B.
# an einer Ampel, "springt" die Position trotzdem minimal - bei sehr kurzer Zeitspanne zwischen
# zwei Punkten wirkt dieses Rauschen sonst wie eine hohe Geschwindigkeit. Deshalb werden Segmente
# unterhalb dieser Mindestbewegung/-zeitspanne für die Tempo-Berechnung ignoriert.
MIN_SEGMENT_DISTANCE_METERS = 3
MIN_SEGMENT_TIME_SECONDS = 1

# Bei ~1Hz-GPS-Aufzeichnung und Radgeschwindigkeit legt man pro Sekunde oft nur wenige Meter
# zurück - in derselben Größenordnung wie die GPS-Ungenauigkeit selbst. Einzelne
# Sekunden-zu-Sekunden-Geschwindigkeiten sind daher von Natur aus verrauscht. Tempo wird deshalb
# über ein Zeitfenster (mehrere Punkte vor/nach dem jeweiligen Segment) gemittelt, nicht nur aus
# zwei benachbarten Punkten - deutlich robuster gegenüber GPS-Rauschen.
TEMPO_SMOOTHING_WINDOW_POINTS = 3


def _stream_value_at(stream, index):
    if not stream or index >= len(stream):
        return None
    return stream[index]


def _average(a, b):
    values = [v for v in (a, b) if v is not None]
    if not values:
        return None
    return sum(values) / len(values)


def compute_route_contributions(route):
    """Zerlegt `route` in Segmente und liefert ein dict:
    (grid_x, grid_y) -> {
        'coords': [[lat,lng],[lat,lng]],   # Geometrie des ersten Segments in dieser Zelle
        'puls': (sum, count), 'tempo': (sum, count), 'watt': (sum, count)
    }
    Liefert ein leeres dict, wenn die Route kein geom hat (z.B. Strava-Import).
    """
    if not route.geom:
        return {}

    coords = list(route.geom.coords)  # [(lng, lat), ...]
    if len(coords) < 2:
        return {}

    # WICHTIG: Geometrie nur EINMAL pro Route nach EPSG:3857 transformieren (Meter), nicht pro
    # Segment/Punkt einzeln - einzelne GEOS-Transforms sind bei tausenden GPS-Punkten pro Route
    # ein massiver Performance-Killer (mehrere Minuten statt Millisekunden).
    coords_m = list(route.geom.transform(3857, clone=True).coords)

    puls_stream = route.puls_stream or []
    watt_stream = route.watt_stream or []
    zeit_stream = route.zeit_stream or []

    limit = min(len(coords), len(zeit_stream))
    if limit < 2:
        return {}

    parsed_times = [parse_datetime(t) if t else None for t in zeit_stream[:limit]]
    cum_dist = [0.0] * limit
    for j in range(limit - 1):
        mj, mj1 = coords_m[j], coords_m[j + 1]
        cum_dist[j + 1] = cum_dist[j] + ((mj1[0] - mj[0]) ** 2 + (mj1[1] - mj[1]) ** 2) ** 0.5

    buckets = {}

    for i in range(limit - 1):
        p1 = coords[i]
        p2 = coords[i + 1]
        m1 = coords_m[i]
        m2 = coords_m[i + 1]

        puls_value = _average(_stream_value_at(puls_stream, i), _stream_value_at(puls_stream, i + 1))
        watt_value = _average(_stream_value_at(watt_stream, i), _stream_value_at(watt_stream, i + 1))

        # Tempo über ein Zeitfenster um dieses Segment mitteln (siehe TEMPO_SMOOTHING_WINDOW_POINTS
        # oben), statt nur aus zwei Nachbarpunkten - sonst dominiert GPS-Rauschen die
        # Sekunde-für-Sekunde-Geschwindigkeit.
        tempo_value = None
        i_lo = max(0, i - TEMPO_SMOOTHING_WINDOW_POINTS)
        i_hi = min(limit - 1, i + 1 + TEMPO_SMOOTHING_WINDOW_POINTS)
        t_lo, t_hi = parsed_times[i_lo], parsed_times[i_hi]
        if t_lo and t_hi:
            delta_seconds = (t_hi - t_lo).total_seconds()
            if delta_seconds >= MIN_SEGMENT_TIME_SECONDS:
                distance_m = cum_dist[i_hi] - cum_dist[i_lo]
                if distance_m >= MIN_SEGMENT_DISTANCE_METERS:
                    candidate = (distance_m / delta_seconds) * 3.6  # m/s -> km/h
                    if candidate <= MAX_PLAUSIBLE_SPEED_KMH:
                        tempo_value = candidate

        if puls_value is None and watt_value is None and tempo_value is None:
            continue  # nichts für dieses Segment zu speichern

        mid_x = (m1[0] + m2[0]) / 2
        mid_y = (m1[1] + m2[1]) / 2
        bucket_key = (
            round(mid_x / PERFORMANCE_GRID_SIZE_METERS),
            round(mid_y / PERFORMANCE_GRID_SIZE_METERS),
        )

        bucket = buckets.get(bucket_key)
        if bucket is None:
            bucket = {
                'coords': [[p1[1], p1[0]], [p2[1], p2[0]]],
                'puls': [0.0, 0],
                'tempo': [0.0, 0],
                'watt': [0.0, 0],
            }
            buckets[bucket_key] = bucket

        if puls_value is not None:
            bucket['puls'][0] += puls_value
            bucket['puls'][1] += 1
        if watt_value is not None:
            bucket['watt'][0] += watt_value
            bucket['watt'][1] += 1
        if tempo_value is not None:
            bucket['tempo'][0] += tempo_value
            bucket['tempo'][1] += 1

    return buckets


def persist_route_contributions(route):
    """Berechnet die Beiträge von `route` und addiert sie inkrementell zu den bestehenden
    UserPerformanceBucket-Zeilen des Users (bzw. legt neue Zeilen an) - verarbeitet dabei NUR
    diese eine Route, nicht die gesamte Fahrten-Historie.

    Nutzt ein einziges natives `INSERT ... ON CONFLICT DO UPDATE` (Postgres-Upsert) statt
    Django's bulk_update: eine Route kann tausende Rasterzellen berühren, und Djangos
    CASE-WHEN-basiertes bulk_update ist dafür spürbar langsam (mehrere Sekunden bei ~5000
    Zeilen) - ein einziges Set-basiertes SQL-Statement erledigt das in einem Bruchteil der Zeit."""
    from django.db import connection

    contributions = compute_route_contributions(route)
    if not contributions:
        return

    rows = []
    for (grid_x, grid_y), data in contributions.items():
        coords = data['coords']
        wkt = f"SRID=4326;LINESTRING({coords[0][1]} {coords[0][0]}, {coords[1][1]} {coords[1][0]})"
        rows.append((
            route.user_id, grid_x, grid_y, wkt,
            data['puls'][0], data['puls'][1],
            data['tempo'][0], data['tempo'][1],
            data['watt'][0], data['watt'][1],
        ))

    # In Chunks batchen, um sicher unter Postgres' Parameter-Limit pro Query (65535) zu bleiben
    # (10 Parameter pro Zeile -> max. ~6500 Zeilen pro Query wären das theoretische Limit).
    CHUNK_SIZE = 2000
    insert_sql = """
        INSERT INTO routes_userperformancebucket
            (user_id, grid_x, grid_y, geom, puls_sum, puls_count, tempo_sum, tempo_count, watt_sum, watt_count)
        VALUES {values_placeholder}
        ON CONFLICT (user_id, grid_x, grid_y) DO UPDATE SET
            puls_sum = routes_userperformancebucket.puls_sum + EXCLUDED.puls_sum,
            puls_count = routes_userperformancebucket.puls_count + EXCLUDED.puls_count,
            tempo_sum = routes_userperformancebucket.tempo_sum + EXCLUDED.tempo_sum,
            tempo_count = routes_userperformancebucket.tempo_count + EXCLUDED.tempo_count,
            watt_sum = routes_userperformancebucket.watt_sum + EXCLUDED.watt_sum,
            watt_count = routes_userperformancebucket.watt_count + EXCLUDED.watt_count
    """
    row_template = "(%s, %s, %s, ST_GeomFromEWKT(%s), %s, %s, %s, %s, %s, %s)"

    with connection.cursor() as cursor:
        for start in range(0, len(rows), CHUNK_SIZE):
            chunk = rows[start:start + CHUNK_SIZE]
            values_placeholder = ", ".join([row_template] * len(chunk))
            params = [value for row in chunk for value in row]
            cursor.execute(insert_sql.format(values_placeholder=values_placeholder), params)
