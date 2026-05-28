# routes/urls.py
from django.urls import path
from .views import RouteCreateView

urlpatterns = [
    # Die URL muss exakt mit dem übereinstimmen, was in Axios steht!
    path('api/routes/create/', RouteCreateView.as_view(), name='route-create'),
]