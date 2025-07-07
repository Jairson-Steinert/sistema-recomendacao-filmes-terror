# Sistema de Recomendação de Filmes de Terror

Este projeto fornece um sistema completo de recomendação de filmes de terror com duas interfaces:
1. **Backend via Terminal** - Usa algoritmo TF-IDF e similaridade de cosseno
2. **Interface Web Django** - Interface web moderna com banco de dados e integração TMDB

🚀 **NOVIDADES**: 
- O backend agora lê dados do banco Django por padrão, com fallback automático para CSV!
- Integração com API TMDB para exibição de imagens de alta qualidade e sinopses atualizadas

## Arquitetura do Sistema

- **Backend Original**: `recomendador_terror.py` - Agora integrado com Django
- **Frontend Web**: `frontend/` - Aplicação Django completa com integração TMDB
- **Dados**: Banco SQLite (Django) + CSV de fallback
- **API Externa**: The Movie Database (TMDB) para imagens e sinopses

## Pré-requisitos

- Python 3.6 ou superior
- Git (opcional)
- Chave da API TMDB (opcional, para imagens e sinopses - obtenha em: https://www.themoviedb.org/settings/api)

## Setup do Ambiente

1. Clone ou baixe este repositório e entre na pasta do projeto:
   ```powershell
   git clone https://github.com/Jairson-Steinert/sistema-recomendacao-filmes-terror.git
   cd filmes
   ```

2. Crie um ambiente virtual Python:
   ```powershell
   py -m venv .venv
   # Se ocorrer erro ao copiar arquivos do venv, tente:
   python -m venv .venv
   ```

3. Ative o ambiente virtual:

   - No Windows PowerShell:
     ```powershell
     # Caso receba erro de execução de scripts, permita-os:
     Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
     # Em seguida, ative o venv:
     . .\.venv\Scripts\Activate.ps1
     ```
   - No Windows (Prompt do CMD):
     ```cmd
     .\.venv\Scripts\activate.bat
     ```
   - No macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
4. **(Opcional, para usuários do VS Code)** Selecione o interpretador Python. Abra a paleta de comandos (Ctrl+Shift+P) e procure por `Python: Select Interpreter`. Escolha o ambiente que você acabou de criar (`.venv`).
5. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

6. **(Opcional)** Configure a chave da API TMDB:
   ```powershell
   # Crie o arquivo .env na pasta frontend/
   cd frontend
   echo "TMDB_API_KEY=sua_chave_aqui" > .env
   cd ..
   ```

## Uso

### 🎯 Método Recomendado: Backend Integrado com Django

1. **Configure o Django primeiro** (se ainda não fez):
   ```powershell
   # Instale dependências Django
   pip install -r frontend/requirements_django.txt
   
   # Configure e migre banco de dados
   cd frontend
   python manage.py migrate
   
   # Importe dados do CSV para o banco
   python manage.py import_movies ../horror_movies.csv
   
   # Crie superuser (opcional)
   python manage.py create_admin
   
   # Configure chave TMDB (opcional)
   echo "TMDB_API_KEY=sua_chave_aqui" > .env
   
   # Popule sinopses via TMDB (opcional)
   python manage.py populate_overviews
   cd ..
   ```

2. **Execute o backend** (agora lê do banco Django):
   ```powershell
   python recomendador_terror.py
   ```

### 🌐 Interface Web Django

1. **Execute o servidor Django**:
   ```powershell
   cd frontend
   python manage.py runserver
   ```

2. **Acesse no navegador**: http://127.0.0.1:8000

   **Funcionalidades da Interface Web:**
   - 🖼️ Imagens de alta qualidade via API TMDB
   - 📖 Sinopses atualizadas (TMDB + local como fallback)
   - 🎯 Sistema de recomendação baseado em similaridade
   - 📱 Interface responsiva e moderna

### 📄 Fallback CSV (Automático)

Se o Django não estiver disponível, o sistema automaticamente usa o CSV como fallback.

## Estrutura de Arquivos

```
├── .vscode/                             # Configurações VS Code
├── .venv/                               # Ambiente virtual Python
├── horror_movies.csv                    # Dataset original (usado como fallback)
├── recomendador_terror.py               # 🚀 Backend integrado Django + CSV fallback
├── requirements.txt                     # Dependências básicas
├── pyrightconfig.json                   # Configuração Pylance/Pyright
├── __init__.py                          # Estrutura de pacotes Python
├── README.md                            # Este arquivo
├── DESENVOLVIMENTO.md                   # Documentação para desenvolvedores
├── DJANGO_SETUP.md                      # Documentação Django detalhada
├── Documentação do Sistema...           # Documentação original do projeto
└── frontend/                            # 🌐 Aplicação Django completa
    ├── requirements_django.txt          # Dependências Django
    ├── horror_movies.csv                # Cópia local do CSV
    ├── db.sqlite3                       # 🗄️ Banco de dados SQLite
    ├── manage.py                        # Django management
    ├── horror_recommender/              # Projeto Django principal
    │   ├── settings.py                 # Configurações Django
    │   ├── urls.py                     # URLs principais
    │   └── wsgi.py                     # WSGI para deploy
    └── movies/                          # App principal
        ├── models.py                   # Modelo Movie
        ├── views.py                    # Views do sistema
        ├── forms.py                    # Formulários Django
        ├── urls.py                     # URLs do app
        ├── admin.py                    # Interface administrativa
        ├── services.py                 # Algoritmo de recomendação
        ├── templates/movies/           # Templates HTML
        │   ├── base.html              # Template base
        │   ├── home.html              # Página inicial
        │   ├── recommendations.html   # Página de recomendações
        │   └── detail.html            # Detalhes do filme
        └── management/commands/        # Comandos customizados
            ├── import_movies.py       # Importação CSV → Django
            └── create_admin.py        # Criação de superuser
```

## Fontes de Dados

- **Primária**: Banco SQLite (Django) - 28.768 filmes importados
- **Fallback**: horror_movies.csv - Usado automaticamente se Django não disponível
- **API Externa**: The Movie Database (TMDB) - Imagens de alta qualidade e sinopses atualizadas

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

Desenvolvido em Julho de 2025.
