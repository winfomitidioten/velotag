from django.contrib import admin
# from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from users.views import ProfileView, LogoutView, RegisterView, CustomObtainAuthToken
from groups.views import GroupView, GroupDetailView, GroupInviteAdmin, UserInvitationsView, GroupLeaveView, GroupKickView, SetGroupFavoriteView, RemoveFavoriteView, GetGroupFavoriteView, GroupTransferAdminView, GroupInviteLinkView, GroupJoinByTokenView
from django.conf.urls.static import static
from django.conf import settings
from users.views import CustomObtainAuthToken

from users.views import ProfileView, LogoutView, RegisterView, CustomObtainAuthToken, PublicUserProfileView

from .views.strava import strava_status, strava_connect, strava_callback, get_activities, import_activity


urlpatterns = [ 
    path('admin/', admin.site.urls),

    # Includes
    path('api/routes/', include('routes.urls')),  # Bug Fix: aus routes/urls.py - api/routes/ wird hier schon angehängt
    path('api/photo-pins/', include('photos.urls')),

    # Auth / User
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api/logout/', LogoutView.as_view()),
    path('api/profil/', ProfileView.as_view(), name='user-profile'),
    path('api/user/invitations/', UserInvitationsView.as_view(), name='user-invitations'),

    # Strava
    path('api/strava/status/', strava_status),
    path('api/strava/connect/', strava_connect),
    path('api/strava/callback/', strava_callback),
    path('api/strava/activities/', get_activities),
    path('api/strava/activities/<int:activity_id>/import/', import_activity),

    # Groups
    path('api/groups/', GroupView.as_view(), name='my-groups'),
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('api/logout/', LogoutView.as_view()),
    path('api/groups/<int:pk>/invite/', GroupInviteAdmin.as_view(), name='group-invite-admin'),
    path('api/groups/<int:pk>/invite-link/', GroupInviteLinkView.as_view(), name='group-invite-link'),
    path('api/groups/join/', GroupJoinByTokenView.as_view(), name='group-join-by-token'),
    path('api/user/invitations/', UserInvitationsView.as_view(), name='user-invitations'),
    path('api/groups/<int:pk>/leave', GroupLeaveView.as_view(), name="group-leave"),
    path('api/groups/<int:pk>/kick/', GroupKickView.as_view(), name="group-kick"),
    path('api/users/<int:pk>/profile/', PublicUserProfileView.as_view(), name='user-public-profile'),
    path('api/groups/<int:pk>/transfer-admin/', GroupTransferAdminView.as_view(), name="group-transfer-admin"),
    path('api/groups/remove_favorite/', RemoveFavoriteView.as_view(), name="group-remove-favorite"),
    path('api/groups/favorite/', GetGroupFavoriteView.as_view(), name="group-get-favorite"),
    path('api/groups/<int:pk>/favorite/', SetGroupFavoriteView.as_view(), name="group-set-favorite")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
