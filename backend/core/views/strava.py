from django.conf import settings
from django.contrib.auth.models import User
from django.core import signing
from django.http import JsonResponse, HttpResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from routes.models import Route
from datetime import datetime, timedelta, timezone as dt_timezone
from urllib.parse import urlencode
from users.models import StravaToken
import requests
import time

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def strava_connect(request):
    # Strava schickt diesen state 1:1 im Callback zurück (Redirects tragen keinen
    # Authorization-Header) - so wissen wir dort, welcher User verbindet
    state = signing.dumps({'user_id': request.user.id})

    params = {
        'client_id':     settings.STRAVA_CLIENT_ID,     # wer fragt an?
        'redirect_uri':  settings.STRAVA_REDIRECT_URI,  # wohin soll Strava zurückschicken
        'response_type': 'code',
        'scope':         'activity:read_all',           # was soll abgefragt werden?
        'state':         state,
    }
    auth_url = f"https://www.strava.com/oauth/authorize?{urlencode(params)}"
    return JsonResponse({'auth_url': auth_url})





def strava_callback(request):
    code = request.GET.get('code')  # Strava schickt ?code=... in der URL
    state = request.GET.get('state')  # vom strava_connect erzeugt, enthält die User-ID

    # State prüfen und den User ermitteln, der die Verbindung gestartet hat
    # (request.user funktioniert hier nicht, da der Redirect keinen Authorization-Header trägt)
    user_id = signing.loads(state, max_age=600)['user_id']  # 600s = 10 Min. gültig
    user = User.objects.get(pk=user_id)

    # Code gegen Token tauschen
    response = requests.post('https://www.strava.com/oauth/token', data={
        'client_id':     settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'code':          code,
        'grant_type':    'authorization_code',
    })

    token_data = response.json()
    # token_data enthält:
    # - access_token  → für API-Calls (läuft nach 6h ab)
    # - refresh_token → um neuen access_token zu holen
    # - expires_at    → Unix-Timestamp wann access_token abläuft



    StravaToken.objects.update_or_create(
        user=user,
        defaults={
            'access_token':  token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at':    token_data['expires_at'],
        }
    )

    # HttpResponseRedirect erlaubt nur http/https/ftp als Ziel-Protokoll und würde bei
    # velotag:// eine DisallowedRedirect werfen - deshalb Location-Header manuell setzen
    redirect_response = HttpResponse(status=302)
    redirect_response['Location'] = f"{settings.STRAVA_APP_REDIRECT_URL}?strava=connected"
    return redirect_response



def get_valid_access_token(user):
    token = StravaToken.objects.get(user=user)
    
    # Ist der Token noch gültig?
    # expires_at ist ein Unix-Timestamp (Sekunden seit 1970)
    # time.time() gibt die aktuelle Zeit als Unix-Timestamp zurück
    if token.expires_at > time.time():
        return token.access_token  # noch gültig, direkt zurückgeben
    
    # Token abgelaufen → neuen holen
    response = requests.post('https://www.strava.com/oauth/token', data={
        'client_id':     settings.STRAVA_CLIENT_ID,
        'client_secret': settings.STRAVA_CLIENT_SECRET,
        'refresh_token': token.refresh_token,
        'grant_type':    'refresh_token',  # ← anders als beim ersten Mal!
    })
    
    new_token_data = response.json()
    
    # Neue Werte in der Datenbank speichern
    token.access_token  = new_token_data['access_token']
    token.refresh_token = new_token_data['refresh_token']
    token.expires_at    = new_token_data['expires_at']
    token.save()
    
    return token.access_token

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_activities(request):
    access_token = get_valid_access_token(request.user)

    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'},
        params={'per_page':50},
    )
    activities = response.json()

    imported_ids = set(
        Route.objects.filter(user=request.user, strava_activity_id__isnull=False)
        .values_list('strava_activity_id', flat=True)
    )
    for activity in activities:
        activity['already_imported'] = activity['id'] in imported_ids

    return JsonResponse(activities, safe=False)
 
@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def import_activity(request, activity_id):
    if Route.objects.filter(user=request.user, strava_activity_id=activity_id).exists():
        return Response({'error':'Diese Aktivität wurde bereits importiert.'}, status=400)

    access_token = get_valid_access_token(request.user)
    headers = {'Authorization': f'Bearer {access_token}'}

    detail = requests.get(
        f'https://www.strava.com/api/v3/activities/{activity_id}',
        headers=headers,
    ).json()

    streams = requests.get(
        f'https://www.strava.com/api/v3/activities/{activity_id}/streams',
        headers=headers,
        params={'keys': 'time,heartrate,watts', 'key_by_type': 'true'},
    ).json()

    start = datetime.strptime(detail['start_date'], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt_timezone.utc)
    zeit_stream = [
        (start + timedelta(seconds=s)).strftime("%Y-%m-%dT%H:%M:%SZ")
        for s in streams.get('time', {}).get('data', [])
    ]

    route = Route.objects.create(
        strecken_name=request.data.get('strecken_name', detail.get('name', 'Strava-Fahrt')),
        user=request.user,
        polyline_map=detail.get('map', {}).get('polyline') or detail.get('map', {}).get('summary_polyline', ''),
        puls_stream=streams.get('heartrate', {}).get('data'),
        zeit_stream=zeit_stream,
        watt_stream=streams.get('watts', {}).get('data'),
        strava_activity_id=activity_id,
    )

    return Response({'message': 'Route importiert', 'strecken_id': route.strecken_id}, status=201)
