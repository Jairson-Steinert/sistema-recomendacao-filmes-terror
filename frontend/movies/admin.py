from django.contrib import admin
from .models import Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'vote_average', 'vote_count', 'release_date', 'popularity')
    list_filter = ('release_date', 'original_language', 'vote_average')
    search_fields = ('title', 'overview', 'genres')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('title', 'overview', 'genres', 'original_language')
        }),
        ('Avaliações', {
            'fields': ('vote_average', 'vote_count', 'popularity')
        }),
        ('Detalhes de Produção', {
            'fields': ('release_date', 'runtime', 'budget', 'revenue'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
