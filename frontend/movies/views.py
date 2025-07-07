from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.http import HttpRequest, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_GET

try:
    import requests
except ImportError:
    requests = None
import json
from .models import Movie
from .forms import MovieSearchForm
from .services import get_recommender  # Import relativo - funciona quando Django está ativo
from typing import Type

class HomeView(ListView):
    """
    View principal que lista filmes e permite busca, incluindo recomendações inteligentes
    """
    model = Movie
    template_name = 'movies/home.html'
    context_object_name = 'movies'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Movie.objects.all()
        search_query = self.request.GET.get('search')
        
        if search_query:
            queryset = Movie.search_movies(search_query)
            
        return queryset.order_by('-vote_average', '-popularity')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = MovieSearchForm(self.request.GET)
        context['search_query'] = self.request.GET.get('search', '')
        context['total_movies'] = Movie.objects.count()
        
        # Adicionar recomendações inteligentes na home page
        try:
            # Usar o serviço de IA diretamente
            from .api_service import ai_service
            
            # Inicializar o serviço se necessário
            if not ai_service.is_initialized:
                ai_service.initialize()
            
            # Verificar se foi solicitado um filme específico para recomendações
            featured_movie_id = self.request.GET.get('featured_movie')
            user_selected = False
            
            if featured_movie_id:
                try:
                    # Usar o filme especificado pelo usuário
                    featured_movie = Movie.objects.get(id=featured_movie_id)
                    user_selected = True
                except Movie.DoesNotExist:
                    # Fallback para filme popular
                    featured_movie = Movie.objects.filter(vote_average__gte=7.0).order_by('-popularity').first()
            else:
                # Obter um filme popular como base para recomendações na home
                featured_movie = Movie.objects.filter(vote_average__gte=7.0).order_by('-popularity').first()
            
            if featured_movie:
                # Obter recomendações baseadas no filme selecionado
                recommendations = ai_service.get_recommendations(featured_movie.id, top_n=6)
                context['featured_recommendations'] = recommendations
                context['featured_movie'] = featured_movie
                context['user_selected'] = user_selected
            else:
                # Fallback: filmes mais bem avaliados
                context['featured_recommendations'] = Movie.objects.filter(
                    vote_average__gte=7.0
                ).order_by('-vote_average')[:6]
                context['featured_movie'] = None
                
        except Exception as e:
            # Em caso de erro, usar filmes mais bem avaliados como fallback
            context['featured_recommendations'] = Movie.objects.filter(
                vote_average__gte=7.0
            ).order_by('-vote_average')[:6]
            context['featured_movie'] = None
            context['recommendation_error'] = str(e)
        
        return context

class MovieDetailView(DetailView):
    """
    View para exibir detalhes de um filme específico.
    Responde com JSON para requisições AJAX.
    """
    model = Movie
    template_name = 'movies/detail.html'
    context_object_name = 'movie'

class RecommendationView(ListView):
    """
    View para exibir recomendações baseadas em um filme usando o serviço de IA
    """
    template_name = 'movies/recommendations.html'
    context_object_name = 'recommendations'
    
    def get_queryset(self):
        movie_id = self.kwargs.get('movie_id')
        
        try:
            # Usar o serviço de IA diretamente
            from .api_service import ai_service
            
            # Inicializar o serviço se necessário
            if not ai_service.is_initialized:
                ai_service.initialize()
            
            # Obter recomendações usando IA
            recommendations = ai_service.get_recommendations(movie_id, top_n=8)
            
            return recommendations
            
        except Exception as e:
            messages.error(self.request, f'Erro ao carregar recomendações: {str(e)}')
            return []
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs.get('movie_id')
        context['selected_movie'] = get_object_or_404(Movie, id=movie_id)
        
        # Adicionar informações para debug
        context['api_error'] = getattr(self, '_api_error', None)
        
        return context

def get_recommendations_ajax(request):
    """
    View AJAX para obter recomendações usando o algoritmo original
    """
    if request.method == 'GET':
        movie_title = request.GET.get('movie_title')
        top_n = int(request.GET.get('top_n', 5))
        
        if movie_title:
            try:
                recommender = get_recommender()
                recommendations = recommender.get_recommendations(movie_title, top_n)
                
                data = []
                for rec in recommendations:
                    data.append({
                        'id': rec['movie'].id,
                        'title': rec['title'],
                        'vote_average': rec['vote_average'],
                        'genres': rec['genres'],
                        'similarity_score': round(rec['similarity_score'], 3),
                        'url': rec['movie'].get_absolute_url()
                    })
                
                return JsonResponse({
                    'success': True,
                    'recommendations': data,
                    'movie_title': movie_title
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'error': f'Erro ao gerar recomendações: {str(e)}'
                })
    
    return JsonResponse({'success': False, 'error': 'Parâmetros inválidos'})

def search_movies_ajax(request):
    """
    View AJAX para busca de filmes usando o serviço integrado
    """
    if request.method == 'GET':
        query = request.GET.get('q', '')
        
        if len(query) >= 2:
            try:
                recommender = get_recommender()
                movies = recommender.search_similar_titles(query, max_results=10)
                
                data = []
                for movie in movies:
                    data.append({
                        'id': movie.id,
                        'title': movie.title,
                        'vote_average': movie.vote_average,
                        'genres': movie.genres
                    })
                
                return JsonResponse({
                    'success': True,
                    'movies': data
                })
            except Exception as e:
                return JsonResponse({
                    'success': False, 
                    'movies': [],
                    'error': str(e)
                })
    
    return JsonResponse({'success': False, 'movies': []})

def api_test_view(request):
    """
    Página para testar a API de recomendações
    """
    return render(request, 'movies/api_test.html')
