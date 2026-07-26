# routes/urls.py
from django.urls import path
from .views import RouteCreateView, RouteListView, RouteMapView, RouteStatsView

urlpatterns = [
    # Bug Fix: Das 'api/routes/' wird schon von der core/urls.py davorgehängt
    path('create/', RouteCreateView.as_view(), name='route-create'),
    path('list/', RouteListView.as_view(), name='route-list'), #Daten aus dem Serializer für die Fahrten Liste
    path('map/', RouteMapView.as_view(), name='route-map'),
    path('stats/', RouteStatsView.as_view(), name='route-stats')
]