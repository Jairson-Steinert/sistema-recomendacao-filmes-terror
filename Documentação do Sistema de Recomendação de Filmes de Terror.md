# Documentação do Sistema de Recomendação de Filmes de Terror

## 1. Introdução

Este documento detalha o protótipo de um sistema de recomendação de filmes de terror, desenvolvido em Python. O sistema utiliza a similaridade de cosseno (cosine similarity) baseada em vetores TF-IDF dos gêneros dos filmes para sugerir títulos semelhantes. Em caso de empate na similaridade, a nota média dos filmes (`vote_average`) é utilizada como critério de desempate, priorizando filmes com notas mais altas.

O objetivo principal deste protótipo é demonstrar a aplicação de técnicas de Processamento de Linguagem Natural (PLN) e álgebra linear para construir um recomendador simples, mas eficaz, de filmes de terror. O código é modular, com funções bem definidas e comentadas, facilitando a compreensão e futuras expansões.

## 2. Estrutura do Projeto

O projeto agora está organizado em duas partes principais: o protótipo standalone em Python e o frontend Django.

```
Filmes Terror Project/
├── horror_movies.csv                             # Dataset de filmes de terror
├── recomendador_terror.py                        # Script standalone de recomendação (terminal)
├── requirements.txt                              # Dependências do protótipo Python
├── README.md                                     # Instruções gerais
├── Documentação do Sistema de Recomendação...md  # Documentação detalhada
└── frontend/                                     # Projeto Django - interface web
    ├── manage.py                                # Script de gerenciamento Django
    ├── horror_recommender/                      # Configurações do projeto Django
    │   ├── settings.py
    │   ├── urls.py
    │   └── ...
    └── movies/                                  # App Django de filmes
        ├── models.py
        ├── views.py
        ├── urls.py
        ├── templates/movies/
        │   ├── base.html
        │   ├── home.html
        │   └── detail.html
        └── templatetags/movie_extras.py
```

## 3. Funções Implementadas

O script `recomendador_terror.py` é composto por diversas funções, cada uma com uma responsabilidade específica no fluxo de recomendação. Abaixo, detalhamos cada uma delas:

### 3.1. `load_and_filter_data(path)`

**Descrição:**
Esta função é responsável por carregar o dataset de filmes a partir de um arquivo CSV, filtrar apenas os filmes que contêm o gênero "Horror" em sua coluna `genre_names`, e selecionar as colunas essenciais para o processo de recomendação. Além disso, a função remove quaisquer linhas duplicadas baseadas no título do filme para garantir que não haja recomendações repetidas ou inconsistências nos dados.

**Parâmetros:**
- `path` (str): O caminho completo para o arquivo CSV do dataset de filmes (e.g., `'horror_movies.csv'`).

**Retorno:**
- `pandas.DataFrame`: Um DataFrame contendo apenas os filmes de terror, com as colunas relevantes e sem duplicatas.

**Detalhes de Implementação:**
1. **Leitura do CSV:** Utiliza `pd.read_csv(path, sep=";")` para carregar o arquivo. O parâmetro `sep=";"` é crucial, pois o dataset fornecido utiliza ponto e vírgula como delimitador, e não a vírgula padrão.
2. **Seleção de Colunas:** Filtra o DataFrame para incluir apenas as colunas necessárias: `id`, `title`, `original_language`, `release_date`, `popularity`, `vote_average`, `runtime`, e `genre_names`. Isso otimiza o uso de memória e foca nos dados relevantes.
3. **Filtragem por Gênero:** Aplica um filtro na coluna `genre_names` usando `df["genre_names"].str.contains("Horror", na=False)` para selecionar apenas os filmes que possuem o gênero "Horror". O `na=False` garante que valores nulos na coluna `genre_names` não causem erros e sejam tratados como não contendo o gênero.
4. **Remoção de Duplicatas:** `df_horror.drop_duplicates(subset=["title"])` é usado para remover entradas de filmes que possuem o mesmo título. Isso é importante para evitar que o sistema recomende múltiplas vezes o mesmo filme, caso ele apareça com pequenas variações no dataset.
5. **Informações e Visualização:** A função imprime informações sobre o DataFrame resultante (`df_horror.info()`) e as primeiras 5 linhas (`df_horror.head()`) para fornecer um feedback imediato sobre a estrutura e o conteúdo dos dados após o processamento inicial.

**Exemplo de Uso:**
```python
horror_movies_df = load_and_filter_data("horror_movies.csv")
```

### 3.2. `preprocess_text(text)`

**Descrição:**
Esta função auxiliar é fundamental para preparar as strings de gêneros para a vetorização TF-IDF. Ela padroniza o texto, convertendo-o para minúsculas, substituindo múltiplos delimitadores por um único espaço e removendo qualquer pontuação indesejada. Esse pré-processamento garante que gêneros como "Horror|Thriller" e "horror, thriller" sejam tratados de forma consistente, melhorando a precisão da similaridade de cosseno.

**Parâmetros:**
- `text` (str): Uma string contendo os nomes dos gêneros de um filme, geralmente separados por vírgulas ou barras.

**Retorno:**
- `str`: A string de gêneros pré-processada e limpa.

**Detalhes de Implementação:**
1. **Minúsculas:** `text.lower()` converte toda a string para letras minúsculas. Isso evita que o vetorizador TF-IDF trate "Horror" e "horror" como termos diferentes.
2. **Substituição de Delimitadores:** `re.sub(r"[|,]+", " ", text)` utiliza expressões regulares para encontrar uma ou mais ocorrências de vírgulas (`,`) ou barras verticais (`|`) e as substitui por um único espaço. Isso unifica a forma como os gêneros são separados.
3. **Remoção de Pontuação:** `re.sub(r"[^a-z0-9\s]", "", text)` remove qualquer caractere que não seja uma letra minúscula (a-z), um número (0-9) ou um espaço (`\s`). Isso garante que apenas os termos relevantes dos gêneros permaneçam, eliminando pontuações residuais ou caracteres especiais.

**Exemplo de Uso:**
```python
processed_genre = preprocess_text("Horror|Thriller, Mystery!")
# Saída esperada: "horror thriller mystery"
```

### 3.3. `vectorize_texts(df)`

**Descrição:**
Esta função aplica a técnica TF-IDF (Term Frequency-Inverse Document Frequency) sobre a coluna de gêneros pré-processada do DataFrame. O TF-IDF é uma medida estatística que reflete a importância de uma palavra em relação a um documento em uma coleção de documentos (corpus). No contexto deste recomendador, cada filme é um "documento" e seus gêneros são as "palavras". A vetorização TF-IDF transforma as descrições textuais dos gêneros em uma representação numérica (matriz), que pode ser usada para calcular a similaridade entre os filmes.

**Parâmetros:**
- `df` (pandas.DataFrame): O DataFrame de filmes de terror, que deve conter a coluna `genre_names`.

**Retorno:**
- `tuple`: Uma tupla contendo:
    - `tfidf_matrix` (scipy.sparse.csr_matrix): A matriz esparsa TF-IDF, onde cada linha representa um filme e cada coluna representa um termo (gênero).
    - `tfidf_vectorizer` (sklearn.feature_extraction.text.TfidfVectorizer): O objeto `TfidfVectorizer` ajustado, que pode ser útil para inspecionar os termos (gêneros) aprendidos ou para transformar novos textos no futuro.

**Detalhes de Implementação:**
1. **Criação da Coluna de Gêneros Processados:** `df["processed_genres"] = df["genre_names"].apply(preprocess_text)` cria uma nova coluna no DataFrame chamada `processed_genres`. Para cada filme, o texto original da coluna `genre_names` é passado pela função `preprocess_text` (descrita na Seção 3.2), garantindo que os gêneros estejam limpos e padronizados antes da vetorização.
2. **Inicialização do TfidfVectorizer:** `tfidf_vectorizer = TfidfVectorizer()` cria uma instância do vetorizador TF-IDF. Este objeto aprenderá o vocabulário (todos os gêneros únicos presentes no corpus) e calculará os pesos TF-IDF para cada gênero em cada filme.
3. **Ajuste e Transformação:** `tfidf_vectorizer.fit_transform(df["processed_genres"])` executa duas etapas principais:
    - `fit`: O vetorizador "aprende" o vocabulário a partir de todos os gêneros processados na coluna `processed_genres`.
    - `transform`: Converte a coleção de textos (gêneros processados) em uma matriz de características TF-IDF. A matriz resultante é esparsa, o que significa que armazena apenas os valores diferentes de zero, economizando memória, especialmente para grandes datasets.
4. **Informação de Dimensões:** A função imprime as dimensões da matriz TF-IDF (`tfidf_matrix.shape`) para confirmar que a vetorização foi realizada e para fornecer uma ideia do tamanho da representação numérica dos dados.

**Exemplo de Uso:**
```python
tfidf_matrix, tfidf_vectorizer = vectorize_texts(horror_movies_df)
```

### 3.4. `compute_similarity_matrix(tfidf_matrix)`

**Descrição:**
Esta função calcula a matriz de similaridade de cosseno entre todos os filmes representados na matriz TF-IDF. A similaridade de cosseno mede o ângulo entre dois vetores em um espaço multidimensional. Quanto menor o ângulo (mais próximos os vetores), maior a similaridade entre os itens. No contexto de recomendação, uma alta similaridade de cosseno entre dois filmes indica que eles possuem perfis de gênero semelhantes.

**Parâmetros:**
- `tfidf_matrix` (scipy.sparse.csr_matrix): A matriz TF-IDF gerada pela função `vectorize_texts`, onde cada linha representa um filme e suas características de gênero.

**Retorno:**
- `numpy.ndarray`: Uma matriz quadrada de similaridade de cosseno, onde `similarity_matrix[i][j]` representa a similaridade entre o filme `i` e o filme `j`.

**Detalhes de Implementação:**
1. **Limitação de Filmes (Opcional, mas Importante):**
   - `MAX_MOVIES_FOR_SIMILARITY = 28768`: agora ajustado para corresponder à capacidade de memória e evitar estouro em datasets grandes. Este valor controla quantos primeiros filmes serão processados, caso o dataset seja muito extenso.
   - `if tfidf_matrix.shape[0] > MAX_MOVIES_FOR_SIMILARITY: tfidf_matrix = tfidf_matrix[:MAX_MOVIES_FOR_SIMILARITY]`: Se o número de filmes na matriz TF-IDF exceder o limite predefinido, a matriz é truncada para incluir apenas os primeiros `28768` filmes.
   - **Observação:** Ajuste o valor conforme a memória disponível no ambiente de execução.
2. **Cálculo da Similaridade de Cosseno:** `cosine_similarity(tfidf_matrix)` retorna a matriz de similaridade.
3. **Informação de Dimensões:** A função imprime as dimensões da matriz de similaridade resultante (`similarity_matrix.shape`) para confirmar o sucesso do cálculo e o tamanho da matriz gerada.

**Exemplo de Uso:**
```python
similarity_matrix = compute_similarity_matrix(tfidf_matrix)
```


### 3.5. `recommend_movies(movie_title, df, sim_matrix, top_n=5)`

**Descrição:**
Esta é a função central do sistema de recomendação. Dado o título de um filme, ela encontra os `top_n` filmes mais similares no dataset. A similaridade é determinada pela matriz de similaridade de cosseno previamente calculada. Um critério de desempate é aplicado: se dois ou mais filmes tiverem a mesma pontuação de similaridade, eles serão ordenados pela sua `vote_average` (nota média) em ordem decrescente, priorizando filmes mais bem avaliados.

**Parâmetros:**
- `movie_title` (str): O título do filme para o qual se deseja obter recomendações.
- `df` (pandas.DataFrame): O DataFrame original de filmes de terror (ou o DataFrame limitado, se `compute_similarity_matrix` aplicou um limite).
- `sim_matrix` (numpy.ndarray): A matriz de similaridade de cosseno calculada pela função `compute_similarity_matrix`.
- `top_n` (int, opcional): O número de filmes mais similares a serem recomendados. O valor padrão é 5.

**Retorno:**
- `pandas.DataFrame`: Um DataFrame contendo os `top_n` filmes recomendados, incluindo suas colunas `title`, `vote_average` e `similarity_score`. Retorna um DataFrame vazio se o filme de entrada não for encontrado.

**Detalhes de Implementação:**
1. **Ajuste do DataFrame:** `if df.shape[0] > sim_matrix.shape[0]: df = df.head(sim_matrix.shape[0])` garante que o DataFrame usado para buscar o filme de entrada e para extrair os títulos dos filmes recomendados corresponda ao número de filmes que foram efetivamente usados para construir a `sim_matrix`. Isso é crucial se a `compute_similarity_matrix` limitou o dataset devido a restrições de memória.
2. **Verificação do Filme de Entrada:** `if movie_title not in df["title"].values:` verifica se o título do filme fornecido pelo usuário existe no DataFrame. Se não for encontrado, uma mensagem é impressa e um DataFrame vazio é retornado.
3. **Localização do Filme:** `movie_idx = df[df["title"] == movie_title].index[0]` obtém o índice do filme de entrada no DataFrame. Este índice é usado para acessar a linha correspondente na `sim_matrix`.
4. **Obtenção das Pontuações de Similaridade:** `sim_scores = list(enumerate(sim_matrix[movie_idx]))` extrai a linha da `sim_matrix` correspondente ao filme de entrada. Cada elemento nesta linha é a pontuação de similaridade entre o filme de entrada e todos os outros filmes. `enumerate` é usado para manter o índice original de cada filme junto com sua pontuação de similaridade.
5. **Ordenação das Pontuações:** `sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)` ordena a lista de tuplas `(índice, pontuação)` em ordem decrescente com base na pontuação de similaridade.
6. **Remoção do Próprio Filme:** `sim_scores = sim_scores[1:]` remove o primeiro elemento da lista, que é o próprio filme de entrada (um filme sempre terá 100% de similaridade consigo mesmo, e não deve ser recomendado).
7. **Criação do DataFrame de Recomendações:**
   - Um loop itera sobre as pontuações de similaridade ordenadas.
   - Para cada filme recomendado, um dicionário contendo o `title`, `vote_average` e `similarity_score` é criado e adicionado à lista `recommended_movies`.
   - `recommended_df = pd.DataFrame(recommended_movies)` converte essa lista de dicionários em um DataFrame Pandas.
8. **Ordenação por Desempate:** `recommended_df = recommended_df.sort_values(by=["similarity_score", "vote_average"], ascending=[False, False])` é a etapa onde o critério de desempate é aplicado. Primeiro, o DataFrame é ordenado por `similarity_score` em ordem decrescente. Em seguida, para filmes com a mesma `similarity_score`, eles são ordenados por `vote_average` também em ordem decrescente, garantindo que filmes mais bem avaliados sejam priorizados.
9. **Seleção dos Top N:** `return recommended_df.head(top_n)` retorna os `top_n` filmes do DataFrame ordenado, que são as recomendações finais.

**Exemplo de Uso:**
```python
recommendations = recommend_movies("Saw", horror_movies_df, similarity_matrix, top_n=5)
print(recommendations)
```

## 4. Instruções de Uso e Boas Práticas no VS Code

O sistema agora possui duas formas de uso: o protótipo standalone em Python (terminal) e o frontend web Django. Siga as instruções correspondentes para cada modo:

### 4.1. Modo Standalone (Terminal) - Protótipo Original

Para utilizar o sistema de recomendação original no terminal, siga os passos abaixo:

#### 4.1.1. Pré-requisitos

Certifique-se de ter o Visual Studio Code instalado em seu sistema. Além disso, é necessário ter o Python 3 instalado. Recomenda-se o uso de um ambiente virtual para gerenciar as dependências do projeto de forma isolada.

#### 4.1.2. Configuração do Ambiente Virtual

É uma boa prática criar um ambiente virtual para cada projeto Python. Isso evita conflitos de dependências entre diferentes projetos.

1. **Abra o Terminal no VS Code:** No VS Code, vá em `Terminal > New Terminal` (ou use o atalho `Ctrl+Shift+` `).`
2. **Navegue até o diretório do projeto:** Use o comando `cd` para ir até a pasta onde você salvou `recomendador_terror.py` e `horror_movies.csv`.
   ```bash
   cd /caminho/para/seu/projeto
   ```
3. **Crie o ambiente virtual:**
   ```bash
   python3 -m venv venv
   ```
   Isso criará uma pasta `venv` no diretório do seu projeto.
4. **Ative o ambiente virtual:**
   - **Windows:**
     ```bash
     .\venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```
   Você verá `(venv)` no início da linha de comando, indicando que o ambiente virtual está ativo.

#### 4.1.3. Instalação das Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias. O script utiliza `pandas`, `scikit-learn` e `numpy`.

```bash
pip install pandas scikit-learn numpy
```

#### 4.1.4. Execução do Script

Após instalar as dependências, você pode executar o script:

1. **Certifique-se de que o ambiente virtual está ativo.**
2. **Execute o script no terminal:**
   ```bash
   python recomendador_terror.py
   ```

O script iniciará a interface de terminal, onde você poderá interagir e obter recomendações de filmes.

### 4.2. Modo Frontend Web (Django)

O projeto agora inclui uma interface web completa desenvolvida em Django, oferecendo uma experiência mais rica e visual.

#### 4.2.1. Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API do TMDB (The Movie Database) para exibição de imagens

#### 4.2.2. Configuração do Ambiente Django

1. **Navegue até o diretório frontend:**
   ```bash
   cd frontend
   ```

2. **Crie e ative um ambiente virtual:**
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   # ou
   source venv/bin/activate  # macOS/Linux
   ```

3. **Instale as dependências Django:**
   ```bash
   pip install django requests scikit-learn pandas numpy
   ```

4. **Configure a chave da API TMDB:**
   - Obtenha uma chave gratuita em [https://www.themoviedb.org/](https://www.themoviedb.org/)
   - Edite `horror_recommender/settings.py` e adicione:
   ```python
   TMDB_API_KEY = 'sua_chave_api_aqui'
   ```

#### 4.2.3. Configuração do Banco de Dados

1. **Execute as migrações:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Importe os dados dos filmes:**
   ```bash
   python manage.py loaddata initial_movies.json
   # ou importe do CSV usando comando customizado
   ```

3. **Popule sinopses via API (opcional):**
   ```bash
   python manage.py populate_overviews
   ```

#### 4.2.4. Execução do Servidor Django

```bash
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/` para usar a interface web.

#### 4.2.5. Funcionalidades do Frontend Web

- **Interface Visual:** Cards de filmes com posters, avaliações e informações
- **Busca Inteligente:** Sistema de busca com sugestões em tempo real
- **Recomendações IA:** Geração de recomendações baseadas em similaridade
- **Detalhes de Filmes:** Páginas detalhadas com sinopse, gêneros e informações
- **API Integration:** Integração com TMDB para posters e sinopses

### 4.3. Integração com TMDB API

O sistema utiliza a API do [The Movie Database (TMDB)](https://www.themoviedb.org/) para enriquecer a experiência visual:

#### 4.3.1. Funcionalidades da API

- **Posters de Filmes:** Exibição automática de capas/posters dos filmes
- **Sinopses:** Busca de sinopses quando não disponíveis localmente
- **Metadados:** Informações adicionais sobre os filmes

#### 4.3.2. Implementação

- **Template Tags:** Filtros customizados `poster_url` e `overview`
- **Cache:** Sistema de cache LRU para otimizar requisições
- **Fallback:** Imagens padrão quando não encontradas na API

### 4.4. Boas Práticas no VS Code

Para utilizar o sistema de recomendação de filmes de terror no Visual Studio Code, siga os passos abaixo:

- **Seleção do Interpretador Python:** O VS Code geralmente detecta automaticamente o ambiente virtual ativo. Se não, você pode selecioná-lo manualmente: `Ctrl+Shift+P` (ou `Cmd+Shift+P` no macOS), digite `Python: Select Interpreter`, e escolha o interpretador dentro da pasta `venv`.
- **Formatação de Código:** Utilize extensões como `Black` ou `autopep8` para manter o código formatado e legível, seguindo as diretrizes do PEP 8. Você pode configurá-los para formatar o código automaticamente ao salvar (`"editor.formatOnSave": true`).
- **Linting:** Ative o linting (e.g., `Pylint`, `Flake8`) para identificar erros e problemas de estilo no código em tempo real.
- **Comentários:** Mantenha os comentários atualizados e claros, explicando a lógica por trás de cada bloco de código, como feito neste protótipo.


## 5. Sugestões de Evolução

Este protótipo serve como uma base sólida para um sistema de recomendação de filmes de terror. No entanto, há diversas áreas onde ele pode ser expandido e aprimorado para se tornar mais robusto e oferecer recomendações mais precisas e personalizadas:

### 5.1. Expansão do Dataset e Fontes de Dados ✅ **PARCIALMENTE IMPLEMENTADO**

Atualmente, o sistema se baseia principalmente nos gêneros dos filmes, mas já possui integração com fonte externa:

-   **Sinopse dos Filmes ✅:** **IMPLEMENTADO** - O sistema agora integra com a **TMDB API (The Movie Database API)** via [https://www.themoviedb.org/](https://www.themoviedb.org/) para buscar automaticamente:
    - Sinopses/overviews dos filmes quando não disponíveis localmente
    - Posters e imagens de capa dos filmes
    - Sistema de cache para otimizar performance
    - Fallback para dados locais quando API não disponível

-   **Informações Adicionais (Futuro):**
    -   **Elenco e Direção:** Filmes com o mesmo diretor ou atores principais podem ter um estilo ou tom semelhante, o que pode ser um fator importante para a recomendação.
    -   **Palavras-chave/Tags:** Muitas bases de dados de filmes fornecem tags ou palavras-chave que descrevem o conteúdo de forma mais granular do que os gêneros.
    -   **Críticas e Avaliações de Usuários:** A análise de sentimento em críticas de usuários pode revelar aspectos subjetivos que influenciam a preferência.

### 5.2. Aprimoramento do Modelo de Similaridade

O uso de TF-IDF e similaridade de cosseno é um bom ponto de partida, mas pode ser melhorado:

-   **Word Embeddings (Word2Vec, GloVe, FastText):** Em vez de TF-IDF, que trata as palavras como entidades independentes, Word Embeddings capturam o significado semântico das palavras e suas relações. Isso permitiria que o sistema entendesse que "terror psicológico" e "suspense" são conceitualmente próximos, mesmo que não compartilhem palavras exatas.

-   **Modelos de Linguagem Pré-treinados (BERT, GPT):** Para uma compreensão ainda mais profunda do texto (especialmente se sinopses forem adicionadas), modelos de linguagem pré-treinados podem gerar representações vetoriais de alta qualidade para filmes, capturando contextos complexos e relações semânticas.

-   **Similaridade Baseada em Conteúdo Híbrida:** Combinar a similaridade de gêneros com a similaridade de sinopses, elenco, etc., pode levar a recomendações mais ricas. Isso pode ser feito ponderando diferentes pontuações de similaridade ou concatenando vetores de características.

### 5.3. Personalização e Filtragem Colaborativa

Atualmente, o sistema é puramente baseado em conteúdo (recomenda filmes semelhantes ao que o usuário gosta). Para um sistema mais completo, a personalização é chave:

-   **Histórico de Visualização do Usuário:** Armazenar e analisar o histórico de filmes assistidos e avaliados por um usuário permitiria recomendações mais personalizadas. Por exemplo, se um usuário assiste muitos filmes de terror dos anos 80, o sistema poderia priorizar filmes de terror dessa década.

-   **Filtragem Colaborativa:** Esta técnica recomenda itens com base nas preferências de usuários com gostos semelhantes. Existem dois tipos principais:
    -   **Baseada em Usuário:** "Usuários que gostaram de X também gostaram de Y."
    -   **Baseada em Item:** "Pessoas que gostaram de A também gostaram de B, C e D."
    A implementação de filtragem colaborativa exigiria um dataset de interações usuário-filme (avaliações, visualizações).

-   **Sistemas Híbridos:** A combinação de filtragem baseada em conteúdo e filtragem colaborativa geralmente produz os melhores resultados, mitigando as desvantagens de cada abordagem individualmente (e.g., o problema do "cold start" para novos itens em sistemas colaborativos).

### 5.4. Interface do Usuário ✅ **IMPLEMENTADO**

**STATUS: CONCLUÍDO** - O projeto agora possui uma interface web completa desenvolvida em Django.

-   **Interface Web Django ✅:** Foi desenvolvida uma aplicação web completa com Django que oferece:
    - Interface visual moderna com Bootstrap
    - Exibição de posters via integração TMDB API
    - Sistema de busca dinâmica com sugestões
    - Recomendações inteligentes em tempo real
    - Páginas detalhadas de filmes com sinopses
    - Design responsivo para diferentes dispositivos

-   **Evolução Adicional Possível:**
    - **Interface Mobile (React Native):** Para aplicações móveis nativas
    - **Interface Desktop (Electron):** Para aplicações desktop multiplataforma

### 5.5. Otimização e Escalabilidade

Para datasets muito grandes, o cálculo da matriz de similaridade pode se tornar um gargalo. Considerações futuras incluem:

-   **Otimização do Cálculo de Similaridade:** Para um número muito grande de filmes, o cálculo `N x N` da matriz de similaridade de cosseno pode ser inviável. Técnicas como Locality Sensitive Hashing (LSH) ou o uso de bibliotecas otimizadas para busca de vizinhos mais próximos (e.g., `Annoy`, `Faiss`) podem ser exploradas.

-   **Armazenamento de Modelos:** Salvar o `TfidfVectorizer` e a `similarity_matrix` (ou um modelo de vizinhos mais próximos) em disco (usando `pickle` ou `joblib`) evitaria a necessidade de recalcular tudo a cada execução, acelerando o tempo de resposta.

-   **Implantação:** Para disponibilizar o sistema para múltiplos usuários, ele precisaria ser implantado em um servidor, talvez como um serviço RESTful API.

Essas sugestões representam um caminho para transformar este protótipo funcional em um sistema de recomendação de filmes de terror mais completo, inteligente e amigável ao usuário.


## Equipe de Desenvolvimento

**Acadêmicos:**
- Ana Carolina Fanhani Straliot
- Gustavo do Prado Lima
- Jairson Steinert

**Professora Dra.:**
- Vanessa de Oliveira Gil

**Disciplina:**
- Inteligência Artificial

---