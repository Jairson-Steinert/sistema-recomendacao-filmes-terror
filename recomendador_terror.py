"""
Acadêmicos:
- Ana Carolina Fanhani Straliot
- Gustavo do Prado Lima
- Jairson Steinert

Professora Dra.:
- Vanessa de Oliveira Gil

Disciplina:
- Inteligência Artificial
"""

import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def load_and_filter_data(path):
    """
    Carrega o dataset de filmes, filtra por filmes de terror e seleciona as colunas necessárias.
    """
    df = pd.read_csv(path, sep=";")
    # Selecionar apenas as colunas relevantes
    df = df[["id", "title", "original_language", "release_date", "popularity", "vote_average", "runtime", "genre_names"]]
    df_horror = df[df["genre_names"].str.contains("Horror", na=False)]
    # Remover duplicatas baseadas no título para evitar recomendações repetidas
    df_horror = df_horror.drop_duplicates(subset=["title"])
    print("\nInformações do dataset de filmes de terror (após limpeza e filtragem):")
    df_horror.info()
    print("\nPrimeiras 5 linhas do dataset de filmes de terror (após limpeza e filtragem):")
    print(df_horror.head())
    return df_horror

def preprocess_text(text):
    """
    Pré-processa o texto dos gêneros: minúsculas, troca de delimitadores por espaço e remoção de pontuação.
    """
    text = text.lower()
    text = re.sub(r"[|,]+", " ", text) # Troca '|' ou ',' por espaço
    text = re.sub(r"[^a-z0-9\s]", "", text) # Remove pontuação, mantendo letras e números
    return text


def vectorize_texts(df):
    """
    Aplica TF-IDF sobre a coluna 'genre_names' pré-processada e retorna a matriz TF-IDF.
    """
    df["processed_genres"] = df["genre_names"].apply(preprocess_text)
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(df["processed_genres"])
    print("\nMatriz TF-IDF criada com sucesso. Dimensões:", tfidf_matrix.shape)
    return tfidf_matrix, tfidf_vectorizer


def compute_similarity_matrix(tfidf_matrix):
    """
    Calcula a matriz de similaridade de cosseno a partir da matriz TF-IDF.
    """
    # Limitar o número de filmes para evitar estouro de memória em ambientes com recursos limitados
    # Para datasets muito grandes, considere abordagens como NearestNeighbors ou processamento em batches
    MAX_MOVIES_FOR_SIMILARITY = 5000 # Ajuste este valor conforme a memória disponível
    if tfidf_matrix.shape[0] > MAX_MOVIES_FOR_SIMILARITY:
        print(f"\nAVISO: O número de filmes ({tfidf_matrix.shape[0]}) excede o limite de {MAX_MOVIES_FOR_SIMILARITY} para cálculo da matriz de similaridade completa. Limitando para os primeiros {MAX_MOVIES_FOR_SIMILARITY} filmes.")
        tfidf_matrix = tfidf_matrix[:MAX_MOVIES_FOR_SIMILARITY]

    similarity_matrix = cosine_similarity(tfidf_matrix)
    print("\nMatriz de similaridade de cosseno criada com sucesso. Dimensões:", similarity_matrix.shape)
    return similarity_matrix


def recommend_movies(movie_title, df, sim_matrix, top_n=5):
    """
    Recomenda os Top N filmes mais similares a um dado título, usando similaridade de cosseno.
    Em caso de empate na similaridade, ordena por 'vote_average' descendente.
    """
    # Ajustar o DataFrame para corresponder ao tamanho da matriz de similaridade, se limitado
    if df.shape[0] > sim_matrix.shape[0]:
        df = df.head(sim_matrix.shape[0])

    if movie_title not in df["title"].values:
        print(f"Filme '{movie_title}' não encontrado no dataset (ou fora do limite de processamento).")
        return pd.DataFrame()

    movie_idx = df[df["title"] == movie_title].index[0]
    sim_scores = list(enumerate(sim_matrix[movie_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Ignorar o próprio filme
    sim_scores = sim_scores[1:]

    # Criar um DataFrame temporário para facilitar a ordenação por vote_average em caso de empate
    recommended_movies = []
    for i, score in sim_scores:
        recommended_movies.append({
            "title": df.iloc[i]["title"],
            "vote_average": df.iloc[i]["vote_average"],
            "similarity_score": score
        })
    
    recommended_df = pd.DataFrame(recommended_movies)
    
    # Ordenar primeiro por similarity_score (descendente) e depois por vote_average (descendente)
    recommended_df = recommended_df.sort_values(by=["similarity_score", "vote_average"], ascending=[False, False])

    return recommended_df.head(top_n)


def load_and_filter_data_from_django():
    """
    Carrega dados do banco Django para recomendação.
    """
    from movies.models import Movie
    import pandas as pd

    # Obter todos os filmes do ORM
    movies = Movie.objects.all().values(
        'id', 'title', 'original_language', 'release_date',
        'popularity', 'vote_average', 'runtime', 'genres'
    )
    df = pd.DataFrame(list(movies))
    # Renomear para compatibilidade com funções existentes
    df = df.rename(columns={'genres': 'genre_names'})
    # Remover duplicatas baseadas no título
    df = df.drop_duplicates(subset=['title'])
    return df

# --- Código Principal (Interface de Terminal) ---
if __name__ == "__main__":
    # Instruções de uso
    print("""
    ================================================================================
    RECOMENDADOR DE FILMES DE TERROR
    ================================================================================
    Para rodar este script, certifique-se de ter as seguintes bibliotecas instaladas:
    pip install pandas scikit-learn numpy

    Execute o script no terminal com: python recomendador_terror.py
    ================================================================================
    """)

    # Caminho para o dataset CSV (fallback)
    DATASET_PATH = 'horror_movies.csv'
    # Tenta carregar do banco Django; se falhar ou vazio, faz fallback para CSV
    try:
        horror_movies_df = load_and_filter_data_from_django()
        if horror_movies_df.empty:
            print("\nNenhum filme encontrado no banco; usando CSV como fallback.")
            horror_movies_df = load_and_filter_data(DATASET_PATH)
        else:
            print("\nDados carregados do banco Django com sucesso.")
    except Exception as e:
        print(f"\nErro ao carregar do banco Django ({e}); usando CSV como fallback.")
        horror_movies_df = load_and_filter_data(DATASET_PATH)

    if not horror_movies_df.empty:
        # Vetorizar os gêneros
        tfidf_matrix, tfidf_vectorizer = vectorize_texts(horror_movies_df)

        # Calcular a matriz de similaridade
        similarity_matrix = compute_similarity_matrix(tfidf_matrix)

        # --- Interface de Terminal Simples ---
        print("\nFilmes de Terror disponíveis para recomendação (primeiros 20):")
        # Ajustar a exibição para o número limitado de filmes, se aplicável
        display_df = horror_movies_df.head(similarity_matrix.shape[0])
        for i, title in enumerate(display_df["title"].head(20)):
            print(f"{i+1}. {title}")
        
        while True:
            user_input = input("\nDigite o título de um filme (ou parte dele) ou o número correspondente, ou 'sair' para encerrar: ")
            if user_input.lower() == 'sair':
                break
            
            selected_movie_title = None
            try:
                # Tenta converter para índice
                movie_index = int(user_input) - 1
                if 0 <= movie_index < len(display_df):
                    selected_movie_title = display_df.iloc[movie_index]["title"]
                else:
                    print("Índice inválido. Por favor, tente novamente.")
                    continue
            except ValueError:
                # Se não for um índice, tenta buscar por título
                matching_movies = display_df[display_df["title"].str.contains(user_input, case=False, na=False)]
                if not matching_movies.empty:
                    if len(matching_movies) == 1:
                        selected_movie_title = matching_movies.iloc[0]["title"]
                    else:
                        print("\nMais de um filme encontrado. Por favor, seja mais específico ou selecione pelo número:")
                        for i, row in matching_movies.iterrows():
                            # Usar o índice do DataFrame original para a exibição
                            print(f"{horror_movies_df[horror_movies_df['title'] == row['title']].index[0] + 1}. {row['title']}")
                        continue # Volta para pedir nova entrada
                else:
                    print("Nenhum filme encontrado com esse título. Por favor, tente novamente.")
                    continue
            
            if selected_movie_title:
                print(f"\nRecomendações para '{selected_movie_title}' (baseado nos primeiros {similarity_matrix.shape[0]} filmes processados):")
                recommendations = recommend_movies(selected_movie_title, horror_movies_df, similarity_matrix)
                if not recommendations.empty:
                    for index, row in recommendations.iterrows():
                        print(f"- {row['title']} (Nota Média: {row['vote_average']:.1f})")
                else:
                    print("Não foi possível gerar recomendações para este filme.")
    else:
        print("Não há filmes de terror suficientes no dataset para gerar recomendações.")



