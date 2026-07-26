# routes/urls.py
from django.urls import path

from .views import RouteCreateView, RouteListView, RouteMapView, RouteDetailView


#from backend.users import views
from . import views


urlpatterns = [
    # Bug Fix: Das 'api/routes/' wird schon von der core/urls.py davorgehängt
    path('create/', RouteCreateView.as_view(), name='route-create'),
    path('list/', RouteListView.as_view(), name='route-list'), #Daten aus dem Serializer für die Fahrten Liste
    path('map/', RouteMapView.as_view(), name='route-map'),
    path('<int:strecken_id>/', RouteDetailView.as_view(), name='route-detail')
    path('intersections/<int:group_id>/', views.group_intersections_geojson, name='group_intersections'),

]

