"""
API Views simples usando apenas Django (sem DRF)
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import traceback

from .models import Movie
from .api_service import ai_service
from .templatetags.movie_extras import fetch_poster_path  # para obter URL do poster


@csrf_exempt
@require_http_methods(["GET"])
def api_movies_list(request):
    """Lista filmes com paginação simples"""
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 20))
        offset = (page - 1) * limit
        
        movies = Movie.objects.all()[offset:offset + limit]
        total = Movie.objects.count()
        
        data = [{
            'id': movie.id,
            'title': movie.title,
            'poster_url': fetch_poster_path(movie.title) or '',
            'vote_average': movie.vote_average,
            'release_date': str(movie.release_date) if movie.release_date else None,
            'genres': movie.genres,
            'overview': movie.overview[:200] + '...' if movie.overview and len(movie.overview) > 200 else movie.overview,
            'popularity': movie.popularity,
        } for movie in movies]
        
        return JsonResponse({
            'success': True,
            'count': len(data),
            'total': total,
            'page': page,
            'results': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_movie_detail(request, movie_id):
    """Detalhes de um filme específico"""
    try:
        movie = Movie.objects.get(id=movie_id)
        data = {
            'id': movie.id,
            'title': movie.title,
            'poster_url': fetch_poster_path(movie.title) or '',
            'original_language': movie.original_language,
            'overview': movie.overview,
            'release_date': str(movie.release_date) if movie.release_date else None,
            'genres': movie.genres,
            'popularity': movie.popularity,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'runtime': movie.runtime,
        }
        return JsonResponse({
            'success': True,
            'data': data
        })
    except Movie.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Filme não encontrado'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_get_recommendations(request):
    """Obtém recomendações usando IA"""
    try:
        data = json.loads(request.body)
        movie_id = data.get('movie_id')
        top_n = data.get('top_n', 5)
        
        if not movie_id:
            return JsonResponse({
                'success': False,
                'error': 'movie_id é obrigatório'
            }, status=400)
        
        # Validar top_n
        if top_n < 1 or top_n > 20:
            top_n = 5
        
        # Obter recomendações usando IA
        recommendations = ai_service.get_recommendations(movie_id, top_n)
        
        return JsonResponse({
            'success': True,
            'movie_id': movie_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao gerar recomendações: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_recommendations_get(request, movie_id):
    """Obtém recomendações usando IA via GET"""
    try:
        top_n = int(request.GET.get('top_n', 8))
        
        # Validar top_n
        if top_n < 1 or top_n > 20:
            top_n = 8
        
        # Obter recomendações usando IA
        recommendations = ai_service.get_recommendations(movie_id, top_n)
        
        return JsonResponse({
            'success': True,
            'movie_id': movie_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Erro ao gerar recomendações: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_search_movies(request):
    """Busca filmes por título"""
    try:
        query = request.GET.get('q', '').strip()
        limit = int(request.GET.get('limit', 10))
        
        if not query:
            return JsonResponse({
                'success': False,
                'error': 'Query parameter "q" is required'
            }, status=400)
        
        if len(query) < 2:
            return JsonResponse({
                'success': False,
                'error': 'Query must be at least 2 characters long'
            }, status=400)
        
        # Buscar filmes por título
        movies = Movie.objects.filter(
            title__icontains=query
        ).order_by('-vote_average', '-popularity')[:limit]
        
        data = [{
            'id': movie.id,
            'title': movie.title,
            'poster_url': fetch_poster_path(movie.title) or '',
            'vote_average': movie.vote_average,
            'release_date': str(movie.release_date) if movie.release_date else None,
            'genres': movie.genres,
            'overview': movie.overview[:100] + '...' if movie.overview and len(movie.overview) > 100 else movie.overview,
            'popularity': movie.popularity,
        } for movie in movies]
        
        return JsonResponse({
            'success': True,
            'query': query,
            'count': len(data),
            'results': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_ai_status(request):
    """Verifica o status do serviço de IA"""
    try:
        # Tentar inicializar se não estiver
        if not ai_service.is_initialized:
            ai_service.initialize()
        
        return JsonResponse({
            'success': True,
            'status': 'ready' if ai_service.is_initialized else 'not_ready',
            'message': 'Serviço de IA está funcionando' if ai_service.is_initialized else 'Serviço de IA não inicializado',
            'movies_count': len(ai_service.df_movies) if ai_service.df_movies is not None else 0
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'status': 'error',
            'error': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
