from django.urls import path
from . import views

app_name = 'movies'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='detail'),
    path('recommendations/<int:movie_id>/', views.RecommendationView.as_view(), name='recommendations'),
    path('api/recommendations/', views.get_recommendations_ajax, name='api_recommendations'),
    path('api/search/', views.search_movies_ajax, name='api_search'),
    path('api-test/', views.api_test_view, name='api_test'),  # Página de teste da API
]
