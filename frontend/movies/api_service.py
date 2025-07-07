"""
API Service para Recomendações de Filmes usando IA
Integra o algoritmo do recomendador_terror.py com Django REST Framework
"""
import os
import sys
import pandas as pd
from typing import List, Dict, Any, Optional
from django.conf import settings

# Adicionar o diretório raiz ao path para importar o recomendador_terror
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, root_dir)

from .models import Movie

class AIRecommendationService:
    """
    Serviço de recomendações usando o algoritmo de IA do recomendador_terror.py
    """
    
    def __init__(self):
        self.tfidf_matrix = None
        self.similarity_matrix = None
        self.df_movies = None
        self.is_initialized = False
    
    def initialize(self):
        """Inicializa o algoritmo de IA carregando dados e criando matrizes"""
        try:
            # Importar funções do recomendador_terror.py
            try:
                from recomendador_terror import (  # type: ignore[reportMissingImports]
                    load_and_filter_data_from_django,
                    vectorize_texts,
                    compute_similarity_matrix,
                )
            except ImportError:
                # Tentar importar do caminho absoluto
                import importlib.util
                root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                recomendador_path = os.path.join(root_dir, "recomendador_terror.py")
                
                if not os.path.exists(recomendador_path):
                    raise ImportError(f"Arquivo recomendador_terror.py não encontrado em {recomendador_path}")
                
                spec = importlib.util.spec_from_file_location("recomendador_terror", recomendador_path)
                if spec is None or spec.loader is None:
                    raise ImportError("Erro ao carregar especificação do módulo recomendador_terror")
                    
                recomendador_terror = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(recomendador_terror)
                
                load_and_filter_data_from_django = recomendador_terror.load_and_filter_data_from_django
                vectorize_texts = recomendador_terror.vectorize_texts
                compute_similarity_matrix = recomendador_terror.compute_similarity_matrix
            
            print("🤖 Inicializando serviço de IA para recomendações...")
            
            # Carregar dados do Django
            self.df_movies = load_and_filter_data_from_django()
            
            if self.df_movies.empty:
                raise ValueError("Nenhum filme de terror encontrado no banco!")
            
            # Criar matrizes TF-IDF e similaridade
            self.tfidf_matrix, _ = vectorize_texts(self.df_movies)
            self.similarity_matrix = compute_similarity_matrix(self.tfidf_matrix)
            
            self.is_initialized = True
            print(f"✅ Serviço de IA inicializado com {len(self.df_movies)} filmes!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar serviço de IA: {e}")
            self.is_initialized = False
            raise
    
    def get_recommendations(self, movie_id: int, top_n: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém recomendações para um filme específico
        
        Args:
            movie_id: ID do filme no banco Django
            top_n: Número de recomendações a retornar
            
        Returns:
            Lista de dicionários com filmes recomendados e scores de similaridade
        """
        if not self.is_initialized:
            self.initialize()
        
        if not self.is_initialized or self.df_movies is None:
            return []
        
        try:
            # Buscar o filme no banco Django
            movie = Movie.objects.get(id=movie_id)
            movie_title = movie.title
            
            # Verificar se o filme está no DataFrame processado
            if movie_title not in self.df_movies["title"].values:
                # Tentar encontrar por título similar
                similar_titles = self.df_movies[
                    self.df_movies["title"].str.contains(movie_title, case=False, na=False)
                ]
                if similar_titles.empty:
                    return []
                movie_title = similar_titles.iloc[0]["title"]
            
            # Usar algoritmo do recomendador_terror.py
            recommendations = self._recommend_movies_internal(movie_title, top_n)
            
            # Converter para objetos Movie do Django
            result = []
            for _, rec in recommendations.iterrows():
                # Buscar o filme completo no Django
                try:
                    django_movie = Movie.objects.get(title=rec["title"])
                    # Adicionar score de similaridade como atributo dinâmico
                    score = rec.at["similarity_score"]  # obtém valor numérico do pandas Series
                    django_movie.similarity_score = float(score)
                    result.append(django_movie)
                except Movie.DoesNotExist:
                    continue
            
            return result
            
        except Movie.DoesNotExist:
            return []
        except Exception as e:
            print(f"❌ Erro ao gerar recomendações: {e}")
            return []
    
    def _recommend_movies_internal(self, movie_title: str, top_n: int = 5) -> pd.DataFrame:
        """
        Versão interna do algoritmo de recomendação (baseada no recomendador_terror.py)
        """
        if self.df_movies is None or self.similarity_matrix is None:
            return pd.DataFrame()
        
        # Ajustar o DataFrame para corresponder ao tamanho da matriz de similaridade
        df = self.df_movies
        if df.shape[0] > self.similarity_matrix.shape[0]:
            df = df.head(self.similarity_matrix.shape[0])
        
        if movie_title not in df["title"].values:
            return pd.DataFrame()
        
        movie_idx = df[df["title"] == movie_title].index[0]
        sim_scores = list(enumerate(self.similarity_matrix[movie_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        
        # Ignorar o próprio filme
        sim_scores = sim_scores[1:]
        
        # Criar DataFrame de recomendações
        recommended_movies = []
        for i, score in sim_scores:
            recommended_movies.append({
                "title": df.iloc[i]["title"],
                "vote_average": df.iloc[i]["vote_average"],
                "similarity_score": score
            })
        
        recommended_df = pd.DataFrame(recommended_movies)
        
        # Ordenar por similaridade e nota
        recommended_df = recommended_df.sort_values(
            by=["similarity_score", "vote_average"], 
            ascending=[False, False]
        )
        
        return recommended_df.head(top_n)
    
    def search_movies(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Busca filmes por título ou gênero
        """
        movies = Movie.objects.filter(
            title__icontains=query
        )[:limit]
        
        return [{
            "id": movie.id,
            "title": movie.title,
            "vote_average": movie.vote_average,
            "release_date": movie.release_date,
            "genres": movie.genres,
            "overview": movie.overview,
            "popularity": movie.popularity,
        } for movie in movies]


# Instância global do serviço de IA
ai_service = AIRecommendationService()
