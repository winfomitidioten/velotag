from django.urls import path
from .views import PhotoPinCreateView, PhotoPinListView, PhotoPinGroupView

urlpatterns = [
    path('create/', PhotoPinCreateView.as_view(), name='photo-pin-create'),
    path('list/', PhotoPinListView.as_view(), name='photo-pin-list'),
    path('group/<int:pk>/', PhotoPinGroupView.as_view(), name='photo-pin-group'),
]