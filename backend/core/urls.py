from django.contrib import admin
# from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from users.views import ProfileView, LogoutView, RegisterView, CustomObtainAuthToken
from groups.views import GetGroupFavoriteView, GroupView, GroupDetailView, GroupInviteAdmin, RemoveFavoriteView, SetGroupFavoriteView, UserInvitationsView, GroupLeaveView, GroupKickView
from django.conf import settings
from django.conf.urls.static import static
from routes.views import group_intersections_geojson
from .views.strava import strava_connect, strava_callback, get_activities
from users.views import CustomObtainAuthToken
from .views.strava import strava_status, strava_connect, strava_callback, get_activities, import_activity

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/routes/', include('routes.urls')),#Bug Fix: aus routes/urls.py - api/routes/ wird hier schon angehängt
    path('api/profil/', ProfileView.as_view(), name='user-profile'),
    path('api/login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api/strava/status/', strava_status),
    path('api/strava/connect/', strava_connect),
    path('api/strava/callback/', strava_callback),
    path('api/strava/activities/', get_activities),
    path('api/strava/activities/<int:activity_id>/import/', import_activity),
    path('api/groups/', GroupView.as_view(), name='my-groups'),
    path('api/register/', RegisterView.as_view(), name='register'),

    path('api/logout/', LogoutView.as_view()),

    path('api/groups/<int:pk>/invite/', GroupInviteAdmin.as_view(), name='group-invite-admin'),
    path('api/user/invitations/', UserInvitationsView.as_view(), name='user-invitations'),
    path('api/groups/favorite/', GetGroupFavoriteView.as_view(), name='get-favorite-group'),
    path('api/groups/remove_favorite/', RemoveFavoriteView.as_view(), name='remove-group-favorite'),

    path('api/groups/<int:group_id>/intersections/', group_intersections_geojson, name='group-intersections'),

    
    path('api/groups/<int:pk>/favorite/', SetGroupFavoriteView.as_view(), name='set-group-favorite'),
    path('api/groups/<int:pk>/leave/', GroupLeaveView.as_view(), name="group-leave"),
    path('api/groups/<int:pk>/kick/', GroupKickView.as_view(), name="group-kick"), 

    path('api/groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('api/groups/', GroupView.as_view(), name='my-groups'),
    
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
