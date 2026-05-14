from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.

def connectionTest(request):
    return JsonResponse({"status": "erfolgreich", "message": "Hallo vom Django-Backend"})