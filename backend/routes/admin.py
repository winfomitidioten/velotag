from django.contrib import admin
from .models import Route

@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    # Diese Spalten werden in der Tabellen-Übersicht im Admin-Panel angezeigt
    list_display = ('strecken_id', 'strecken_name', 'user', 'group_id', 'created_at')
    
    #Suchkriterien definieren
    search_fields = ('strecken_name', 'user__username', 'strecken_id')  # tot: wird von der nächsten Zeile direkt überschrieben
    search_fields = ('strecken_name', 'user__username', 'strecken_id', 'group_id')
    
    # Filter
    list_filter = ('created_at',)