from django.urls import path
from .views import connectionTest

urlpatterns = [
    path('test/', connectionTest, name='connectionTest'),
]