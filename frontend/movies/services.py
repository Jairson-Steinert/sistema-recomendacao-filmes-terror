"""
Serviço de recomendação integrado com o algoritmo original
Baseado no recomendador_terror.py
"""

import pandas as pd
import re
import numpy as np
from typing import Optional, List, Dict, Any, Union
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import spmatrix
from django.conf import settings
from .models import Movie
import os
import pickle

class HorrorMovieRecommender:
    """
    Classe que implementa o algoritmo de recomendação do arquivo original
    Adaptado para trabalhar com o Django ORM
    """
    
    def __init__(self):
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix: Optional[Union[spmatrix, np.ndarray]] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.movies_df: Optional[pd.DataFrame] = None
        self.is_fitted: bool = False
        
    def preprocess_text(self, text):
        """
        Pré-processa o texto dos gêneros: minúsculas, troca de delimitadores por espaço e remoção de pontuação.
        """
        if not text:
            return ""
        text = str(text).lower()
        text = re.sub(r"[|,]+", " ", text)  # Troca '|' ou ',' por espaço
        text = re.sub(r"[^a-z0-9\s]", "", text)  # Remove pontuação, mantendo letras e números
        return text
    
    def load_movies_data(self):
        """
        Carrega os dados dos filmes do banco Django
        """
        movies = Movie.objects.all().values(
            'id', 'title', 'genres', 'vote_average', 'vote_count', 
            'popularity', 'release_date', 'runtime'
        )
        
        if not movies:
            raise ValueError("Nenhum filme encontrado no banco de dados")
        
        # Converter para DataFrame
        self.movies_df = pd.DataFrame(list(movies))
        
        # Renomear colunas para compatibilidade com o código original
        self.movies_df = self.movies_df.rename(columns={'genres': 'genre_names'})
        
        # Remover duplicatas baseadas no título
        self.movies_df = self.movies_df.drop_duplicates(subset=["title"])
        
        print(f"Carregados {len(self.movies_df)} filmes únicos do banco Django")
        return self.movies_df
    
    def vectorize_genres(self):
        """
        Aplica TF-IDF sobre os gêneros dos filmes
        """
        if self.movies_df is None:
            self.load_movies_data()
        
        # Garantir que movies_df não é None após o carregamento
        if self.movies_df is None:
            raise ValueError("Falha ao carregar dados dos filmes")
        
        # Pré-processar gêneros
        self.movies_df["processed_genres"] = self.movies_df["genre_names"].apply(self.preprocess_text)
        
        # Aplicar TF-IDF
        self.tfidf_vectorizer = TfidfVectorizer()
        self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(self.movies_df["processed_genres"])
        
        print(f"Matriz TF-IDF criada: {self.tfidf_matrix.shape}")
        return self.tfidf_matrix
    
    def compute_similarity_matrix(self, max_movies=5000):
        """
        Calcula a matriz de similaridade de cosseno
        """
        if self.tfidf_matrix is None:
            self.vectorize_genres()
        
        # Garantir que tfidf_matrix e movies_df não são None
        if self.tfidf_matrix is None or self.movies_df is None:
            raise ValueError("Falha ao criar matriz TF-IDF ou carregar dados dos filmes")
        
        # Limitar número de filmes para evitar problemas de memória
        if self.tfidf_matrix.shape[0] > max_movies:
            print(f"Limitando para {max_movies} filmes para evitar problemas de memória")
            # Matriz TF-IDF é esparsa por padrão, slice funciona em tempo de execução
            self.tfidf_matrix = self.tfidf_matrix[:max_movies]  # type: ignore
            self.movies_df = self.movies_df.head(max_movies)
        
        self.similarity_matrix = cosine_similarity(self.tfidf_matrix)  # type: ignore
        print(f"Matriz de similaridade criada: {self.similarity_matrix.shape}")
        
        self.is_fitted = True
        return self.similarity_matrix
    
    def get_recommendations(self, movie_title, top_n=5):
        """
        Recomenda filmes similares baseado no título do filme
        Retorna lista de dicionários com informações dos filmes recomendados
        """
        if not self.is_fitted:
            self.compute_similarity_matrix()
        
        # Garantir que os dados necessários estão carregados
        if self.movies_df is None or self.similarity_matrix is None:
            raise ValueError("Dados não foram carregados corretamente")
        
        # Verificar se o filme existe
        if movie_title not in self.movies_df["title"].values:
            return []
        
        # Encontrar índice do filme
        movie_idx = self.movies_df[self.movies_df["title"] == movie_title].index[0]
        
        # Calcular similaridades
        sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Ignorar o próprio filme e pegar top_n
        sim_scores = sim_scores[1:top_n+1]
        
        # Criar lista de recomendações
        recommendations = []
        for i, score in sim_scores:
            movie_data = self.movies_df.iloc[i]
            
            # Buscar objeto Movie do Django
            try:
                movie_obj = Movie.objects.get(id=movie_data['id'])
                recommendations.append({
                    'movie': movie_obj,
                    'similarity_score': float(score),
                    'vote_average': float(movie_data['vote_average']),
                    'title': movie_data['title'],
                    'genres': movie_data['genre_names']
                })
            except Movie.DoesNotExist:
                continue
        
        # Ordenar por similaridade e depois por nota
        recommendations.sort(
            key=lambda x: (x['similarity_score'], x['vote_average']), 
            reverse=True
        )
        
        return recommendations
    
    def search_similar_titles(self, partial_title, max_results=10):
        """
        Busca filmes por título parcial
        """
        if self.movies_df is None:
            self.load_movies_data()
        
        # Garantir que movies_df não é None após o carregamento
        if self.movies_df is None:
            raise ValueError("Falha ao carregar dados dos filmes")
        
        # Busca case-insensitive
        matches = self.movies_df[
            self.movies_df["title"].str.contains(partial_title, case=False, na=False)
        ]
        
        # Retornar como objetos Movie do Django
        movie_ids = matches['id'].tolist()
        return Movie.objects.filter(id__in=movie_ids)[:max_results]
    
    def get_movie_by_title(self, title):
        """
        Busca um filme específico por título exato
        """
        try:
            return Movie.objects.get(title__iexact=title)
        except Movie.DoesNotExist:
            return None

# Instância global do recomendador
_recommender_instance = None

def get_recommender():
    """
    Singleton para o recomendador
    """
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = HorrorMovieRecommender()
    return _recommender_instance
