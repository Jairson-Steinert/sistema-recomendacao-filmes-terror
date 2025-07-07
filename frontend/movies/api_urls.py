"""
URLs da API REST para o sistema de recomendação de filmes
"""
from django.urls import path
from . import api_views_simple

app_name = 'movies_api'

urlpatterns = [
    # API REST endpoints simples
    path('movies/', api_views_simple.api_movies_list, name='movies_list'),
    path('movies/<int:movie_id>/', api_views_simple.api_movie_detail, name='movie_detail'),
    path('recommendations/', api_views_simple.api_get_recommendations, name='get_recommendations'),
    path('recommendations/<int:movie_id>/', api_views_simple.api_get_recommendations_get, name='get_recommendations_get'),
    path('search/', api_views_simple.api_search_movies, name='search_movies'),
    path('status/', api_views_simple.api_ai_status, name='ai_status'),
]
