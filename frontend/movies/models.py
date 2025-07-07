from django.db import models
from django.urls import reverse
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from django.conf import settings

class Movie(models.Model):
    """
    Modelo para representar filmes de terror
    """
    # Campo ID automático (explícito para o Pylance)
    id = models.AutoField(primary_key=True)
    
    title = models.CharField(max_length=255, verbose_name="Título")
    overview = models.TextField(verbose_name="Sinopse", blank=True)
    genres = models.CharField(max_length=255, verbose_name="Gêneros")
    vote_average = models.FloatField(verbose_name="Nota Média", default=0.0)
    vote_count = models.IntegerField(verbose_name="Número de Votos", default=0)
    release_date = models.DateField(verbose_name="Data de Lançamento", null=True, blank=True)
    popularity = models.FloatField(verbose_name="Popularidade", default=0.0)
    runtime = models.IntegerField(verbose_name="Duração (min)", null=True, blank=True)
    budget = models.BigIntegerField(verbose_name="Orçamento", null=True, blank=True)
    revenue = models.BigIntegerField(verbose_name="Receita", null=True, blank=True)
    original_language = models.CharField(max_length=10, verbose_name="Idioma Original", default="en")
    
    # Campos extras para facilitar buscas
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"
        ordering = ['-vote_average', '-popularity']

    def __str__(self):
        return f"{self.title} ({self.vote_average:.1f})"
    # atributo dinâmico para Pylance e compatibilidade com API service
    similarity_score: float = 0.0

    def get_absolute_url(self):
        return reverse('movies:detail', kwargs={'pk': self.pk})

    @property
    def genres_list(self):
        """Retorna os gêneros como uma lista"""
        return [genre.strip() for genre in self.genres.split(',') if genre.strip()]

    @property
    def rating_stars(self):
        """Retorna o número de estrelas baseado na nota"""
        return int(self.vote_average / 2)  # Converte de 0-10 para 0-5 estrelas

    @classmethod
    def get_recommendations(cls, movie_title, top_n=5):
        """
        Método para obter recomendações baseadas em similaridade TF-IDF
        """
        # Buscar todos os filmes
        movies = cls.objects.all()
        
        if not movies.exists():
            return []

        # Converter para DataFrame para usar a lógica existente
        data = []
        for movie in movies:
            data.append({
                'title': movie.title,
                'genres': movie.genres,
                'vote_average': movie.vote_average,
                'id': movie.id
            })
        
        df = pd.DataFrame(data)
        
        # Verificar se o filme existe
        if movie_title not in df['title'].values:
            return []

        # Aplicar TF-IDF nos gêneros
        tfidf = TfidfVectorizer(stop_words='english')
        tfidf_matrix = tfidf.fit_transform(df['genres'].fillna(''))
        
        # Calcular similaridade
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Encontrar o índice do filme
        movie_idx = df[df['title'] == movie_title].index[0]
        sim_scores = list(enumerate(similarity_matrix[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Ignorar o próprio filme e pegar os top_n
        sim_scores = sim_scores[1:top_n+1]
        
        # Criar lista de recomendações
        recommendations = []
        for i, score in sim_scores:
            movie_data = df.iloc[i]
            movie_obj = cls.objects.get(id=movie_data['id'])
            recommendations.append({
                'movie': movie_obj,
                'similarity_score': score,
                'vote_average': movie_data['vote_average']
            })
        
        # Ordenar por similaridade e depois por nota
        recommendations.sort(key=lambda x: (x['similarity_score'], x['vote_average']), reverse=True)
        
        return recommendations

    @classmethod
    def search_movies(cls, query):
        """
        Busca filmes por título ou gênero
        """
        return cls.objects.filter(
            models.Q(title__icontains=query) | 
            models.Q(genres__icontains=query)
        ).distinct()
