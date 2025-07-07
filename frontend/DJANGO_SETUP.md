# Sistema de Recomendação de Filmes de Terror - Django

## Estrutura do Projeto Django

### 1. Instalação das Dependências Django

```powershell
# Ative seu ambiente virtual primeiro
.\.venv\Scripts\Activate

# Instale as dependências Django (será criado um requirements específico)
pip install django
pip install django-bootstrap4  # Para estilização
pip freeze > frontend/requirements_django.txt
```

### 2. Criação do Projeto Django

```powershell
# Navegar para o diretório frontend
cd frontend

# Criar projeto Django dentro do frontend
django-admin startproject horror_recommender .

# Criar app para o recomendador
python manage.py startapp movies

# Voltar para o diretório principal (opcional)
cd ..
```

### 3. Estrutura Proposta (Separando Frontend)

```
frontend/                    # Diretório Frontend Django
├── horror_recommender/      # Projeto principal Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── __init__.py
├── movies/                  # App do recomendador
│   ├── models.py           # Modelo Movie
│   ├── views.py            # Lógica de recomendação
│   ├── urls.py             # URLs do app
│   ├── forms.py            # Formulários
│   ├── admin.py            # Interface admin
│   ├── templates/movies/   # Templates HTML
│   │   ├── base.html
│   │   ├── home.html
│   │   └── recommendations.html
│   ├── static/movies/      # CSS, JS, imagens
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── management/         # Comandos personalizados
│       └── commands/
│           └── import_movies.py
├── manage.py               # Script Django
└── requirements_django.txt # Dependências Django

# Arquivos originais (mantidos na raiz)
recomendador_terror.py      # Código original Python
horror_movies.csv           # Dataset
requirements.txt            # Dependências originais
```

### 4. Funcionalidades Django Propostas

#### **Models (movies/models.py)**
- Modelo `Movie` com todos os campos do CSV
- Métodos para busca e recomendação

#### **Views (movies/views.py)**
- `HomeView`: Lista de filmes e formulário de busca
- `RecommendationView`: Exibe recomendações
- `MovieDetailView`: Detalhes do filme

#### **Templates**
- Interface responsiva com Bootstrap
- Busca por filmes
- Cards com informações dos filmes
- Página de recomendações

#### **Admin Interface**
- Gestão de filmes pelo Django Admin
- Filtros e busca

### 5. Próximos Passos

1. **Instalar dependências Django**
2. **Criar projeto e app Django no diretório frontend**
3. **Configurar models e importar dados do CSV**
4. **Migrar código de recomendação para views Django**
5. **Criar templates HTML responsivos**
6. **Configurar URLs e routing**

### 6. Comandos para Execução

```powershell
# Executar o sistema original (Python puro)
python recomendador_terror.py

# Executar o frontend Django
cd frontend
python manage.py runserver
```

### 7. Vantagens da Separação

- **Backend original** mantido intacto para testes e comparação
- **Frontend Django** como uma camada separada
- **Facilidade de desenvolvimento** e manutenção
- **Possibilidade de APIs** para integração futura


