from django.contrib import admin
# from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path, include
from users.views import CustomObtainAuthToken

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('api/routes/', include('routes.urls')),
    # path('api/login/', obtain_auth_token, name='api_token_auth')
    path('api/login/', CustomObtainAuthToken.as_view(), name='api_token_auth'),
]
