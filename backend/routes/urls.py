# routes/urls.py
from django.urls import path
from .views import RouteCreateView, RouteListView
from .views import RouteListView

urlpatterns = [
    # Bug Fix: Das 'api/routes/' wird schon von der core/urls.py davorgehängt
    path('create/', RouteCreateView.as_view(), name='route-create'),
    path('list/', RouteListView.as_view(), name='route-list'),
    path('read/', RouteListView.as_view(), name='route-list') #Diese Zeile fehlt noch, damit die GET-Anfrage funktioniert
]