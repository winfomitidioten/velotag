from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect
from users.models import StravaToken
import requests
import time

def strava_connect(request):
    auth_url = (
        f"https://www.strava.com/oauth/authorize"
        f"?client_id={settings.STRAVA_CLIENT_ID}" # wer fragt an?
        f"&redirect_uri=http://localhost:8000/api/strava/callback/" # wohin soll Strava zurückschicken
        f"&response_type=code"
        f"&scope=activity:read_all" # was soll abgefragt werden?
    )
    return JsonResponse({'auth_url': auth_url})





def strava_callback(request):
    code = request.GET.get('code')  # Strava schickt ?code=... in der URL
    
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
        user=request.user,
        defaults={
            'access_token':  token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_at':    token_data['expires_at'],
        }
    )
    return redirect('/karte') 



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


def get_activities(request):
    access_token = get_valid_access_token(request.user)

    response = requests.get(
        'https://www.strava.com/api/v3/athlete/activities',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    return JsonResponse(response.json(), safe=False)
 
