from django.contrib import admin
# from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from users.views import ProfileView, LogoutView, RegisterView, CustomObtainAuthToken
from groups.views import GroupView, GroupDetailView, GroupInviteAdmin, UserInvitationsView, GroupLeaveView, GroupKickView, SetGroupFavoriteView, RemoveFavoriteView, GetGroupFavoriteView, GroupTransferAdminView, GroupInviteLinkView, GroupJoinByTokenView, GroupLeaderboardView
from django.conf.urls.static import static
from django.conf import settings
from users.views import CustomObtainAuthToken

from users.views import ProfileView, LogoutView, RegisterView, CustomObtainAuthToken, PublicUserProfileView, DeviceView, OnboardingView, GeocodeView, GeocodeReverseView


from .views.strava import strava_status, strava_connect, strava_callback, get_activities, import_activity


urlpatterns = [
    path('admin/', admin.site.urls),

    # API-Dokumentation (Swagger UI / Redoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # Includes
    path('api/routes/', include('routes.urls')),  # Bug Fix: aus routes/urls.py - api/routes/ wird hier schon angehängt
    path('api/photo-pins/', include('photos.urls')),

    # Auth / User
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
    path('api/logout/', LogoutView.as_view()),
    path('api/profil/', ProfileView.as_view(), name='user-profile'),
    path('api/onboarding/', OnboardingView.as_view(), name='onboarding'),
    path('api/geocode/', GeocodeView.as_view(), name='geocode'),
    path('api/geocode/reverse/', GeocodeReverseView.as_view(), name='geocode-reverse'),
    path('api/user/invitations/', UserInvitationsView.as_view(), name='user-invitations'),
    path('api/user/save-push-token/', DeviceView.as_view(), name='user-save-push-token'),

    # Strava
    path('api/strava/status/', strava_status),
    path('api/strava/connect/', strava_connect),
    path('api/strava/callback/', strava_callback),
    path('api/strava/activities/', get_activities),
    path('api/strava/activities/<int:activity_id>/import/', import_activity),

    # Groups
    path('api/groups/', GroupView.as_view(), name='my-groups'),
    path('api/groups/<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('api/groups/<int:pk>/invite/', GroupInviteAdmin.as_view(), name='group-invite-admin'),
    path('api/groups/<int:pk>/invite-link/', GroupInviteLinkView.as_view(), name='group-invite-link'),
    path('api/groups/join/', GroupJoinByTokenView.as_view(), name='group-join-by-token'),
    path('api/user/invitations/', UserInvitationsView.as_view(), name='user-invitations'),
    path('api/groups/<int:pk>/leave', GroupLeaveView.as_view(), name="group-leave"),
    path('api/groups/<int:pk>/kick/', GroupKickView.as_view(), name="group-kick"),
    path('api/users/<int:pk>/profile/', PublicUserProfileView.as_view(), name='user-public-profile'),
    path('api/groups/<int:pk>/transfer-admin/', GroupTransferAdminView.as_view(), name="group-transfer-admin"),
    path('api/groups/<int:pk>/leaderboard/', GroupLeaderboardView.as_view(), name="group-leaderboard"),
    path('api/groups/remove_favorite/', RemoveFavoriteView.as_view(), name="group-remove-favorite"),
    path('api/groups/favorite/', GetGroupFavoriteView.as_view(), name="group-get-favorite"),
    path('api/groups/<int:pk>/favorite/', SetGroupFavoriteView.as_view(), name="group-set-favorite")
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
