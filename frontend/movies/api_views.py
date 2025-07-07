"""
API Views para o sistema de recomendação de filmes
"""
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Movie
from .api_service import ai_service


@api_view(['GET'])
def movies_list(request):
    """
    Lista todos os filmes com paginação
    """
    try:
        movies = Movie.objects.all()[:20]  # Limitar a 20 por enquanto
        data = [{
            'id': movie.id,
            'title': movie.title,
            'vote_average': movie.vote_average,
            'release_date': movie.release_date,
            'genres': movie.genres,
            'overview': movie.overview[:200] + '...' if movie.overview and len(movie.overview) > 200 else movie.overview,
            'popularity': movie.popularity,
        } for movie in movies]
        
        return Response({
            'count': len(data),
            'results': data
        })
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def movie_detail(request, movie_id):
    """
    Detalhes de um filme específico
    """
    try:
        movie = Movie.objects.get(id=movie_id)
        data = {
            'id': movie.id,
            'title': movie.title,
            'original_language': movie.original_language,
            'overview': movie.overview,
            'release_date': movie.release_date,
            'genres': movie.genres,
            'popularity': movie.popularity,
            'vote_average': movie.vote_average,
            'vote_count': movie.vote_count,
            'runtime': movie.runtime,
        }
        return Response(data)
    except Movie.DoesNotExist:
        return Response({
            'error': 'Filme não encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def get_recommendations(request):
    """
    Obtém recomendações de filmes usando IA
    """
    try:
        # Extrair dados da requisição
        movie_id = request.data.get('movie_id')
        top_n = request.data.get('top_n', 5)
        
        if not movie_id:
            return Response({
                'error': 'movie_id é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar top_n
        if top_n < 1 or top_n > 20:
            top_n = 5
        
        # Obter recomendações usando IA
        recommendations = ai_service.get_recommendations(movie_id, top_n)
        
        return Response({
            'movie_id': movie_id,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        return Response({
            'error': f'Erro ao gerar recomendações: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def search_movies(request):
    """
    Busca filmes por título
    """
    try:
        query = request.GET.get('q', '')
        limit = int(request.GET.get('limit', 20))
        
        if not query:
            return Response({
                'error': 'Parâmetro de busca "q" é obrigatório'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Buscar filmes
        results = ai_service.search_movies(query, limit)
        
        return Response({
            'query': query,
            'count': len(results),
            'results': results
        })
        
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def ai_status(request):
    """
    Verifica o status do serviço de IA
    """
    try:
        # Tentar inicializar se não estiver
        if not ai_service.is_initialized:
            ai_service.initialize()
        
        return Response({
            'status': 'ready' if ai_service.is_initialized else 'not_ready',
            'message': 'Serviço de IA está funcionando' if ai_service.is_initialized else 'Serviço de IA não inicializado',
            'movies_count': len(ai_service.df_movies) if ai_service.df_movies is not None else 0
        })
    except Exception as e:
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Views Django tradicionais para compatibilidade
@csrf_exempt
def api_recommendations_legacy(request):
    """
    Endpoint legacy para compatibilidade com o frontend atual
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            movie_id = data.get('movie_id')
            top_n = data.get('top_n', 5)
            
            if not movie_id:
                return JsonResponse({'error': 'movie_id é obrigatório'}, status=400)
            
            recommendations = ai_service.get_recommendations(movie_id, top_n)
            
            return JsonResponse({
                'success': True,
                'recommendations': recommendations,
                'count': len(recommendations)
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=500)
    
    return JsonResponse({'error': 'Método não permitido'}, status=405)
