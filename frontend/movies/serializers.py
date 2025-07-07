"""
Serializers para a API REST do sistema de recomendação de filmes
"""
from rest_framework import serializers
from .models import Movie


class MovieSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Movie"""
    
    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'original_language', 'overview',
            'release_date', 'genres', 'popularity', 'vote_average',
            'vote_count', 'runtime'
        ]


class MovieRecommendationSerializer(serializers.Serializer):
    """Serializer para recomendações de filmes"""
    movie = MovieSerializer(read_only=True)
    similarity_score = serializers.FloatField()
    
    
class RecommendationRequestSerializer(serializers.Serializer):
    """Serializer para requisições de recomendação"""
    movie_id = serializers.IntegerField()
    top_n = serializers.IntegerField(default=5, min_value=1, max_value=20)
