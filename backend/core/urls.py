from django.contrib import admin
# from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from users.views import ProfileView
from groups.views import GroupView
from django.conf.urls.static import static
from django.conf import settings
from users.views import CustomObtainAuthToken
from .views.strava import strava_connect, strava_callback, get_activities

from users.views import CustomObtainAuthToken, RegisterView
urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/routes/', include('routes.urls')),
    # path('api/login/', obtain_auth_token, name='api_token_auth')
    path('api/routes/', include('routes.urls')),#Bug Fix: aus routes/urls.py - api/routes/ wird hier schon angehängt
    path('api/profil/', ProfileView.as_view(), name='user-profile'),
    path('api/login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api/strava/connect/', strava_connect),
    path('api/strava/callback/', strava_callback),
    path('api/strava/activities/', get_activities),
    path('api/groups/', GroupView.as_view(), name='my-groups'),
    path('api/register/', RegisterView.as_view(), name='register') 
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
