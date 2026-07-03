from django.contrib import admin
# from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from users.views import ProfileView, LogoutView, RegisterView, CustomObtainAuthToken
from groups.views import GetGroupFavoriteView, GroupFavoriteView, GroupView, GroupDetailView, GroupInviteAdmin, RemoveFavoriteView, UserInvitationsView
from groups.views import GroupView, GroupDetailView, GroupInviteAdmin, UserInvitationsView, GroupLeaveView, GroupKickView
from django.conf.urls.static import static
from django.conf import settings
from users.views import CustomObtainAuthToken
from .views.strava import strava_connect, strava_callback, get_activities

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
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('api/logout/', LogoutView.as_view()),
    path('api/groups/<int:pk>/invite/', GroupInviteAdmin.as_view(), name='group-invite-admin'),
    path('api/user/invitations/', UserInvitationsView.as_view(), name='user-invitations'),
    path('api/groups/<int:pk>/favorite/', GroupFavoriteView.as_view(), name='group-favorite'),
    path('api/groups/remove_favorite/', RemoveFavoriteView.as_view(), name='remove-favorite'),
    path('api/groups/favorite/', GetGroupFavoriteView.as_view(), name='get-favorite-group'),
    path('api/groups/<int:pk>/leave', GroupLeaveView.as_view(), name="group-leave"),
    path('api/groups/<int:pk>/kick/', GroupKickView.as_view(), name="group-kick")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
