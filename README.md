# Sistema de Recomendação de Filmes de Terror

Este projeto fornece um protótipo simples de recomendador de filmes de terror, baseado em vetores TF-IDF dos gêneros e similaridade de cosseno. Em caso de empate na similaridade, utiliza a nota média (`vote_average`) como critério de desempate.

## Pré-requisitos

- Python 3.6 ou superior
- Git (opcional)

## Setup do Ambiente

1. Clone ou baixe este repositório e entre na pasta do projeto:
   ```powershell
   git clone <URL-do-repositório>
   cd filmes
   ```

2. Crie um ambiente virtual Python:
   ```powershell
   python -m venv venv
   ```

3. Ative o ambiente virtual:

   - No Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - No Windows Command Prompt (cmd):
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   - No macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

Com o ambiente virtual ativado, basta executar:
```bash
python recomendador_terror.py
```
Siga as instruções na tela para escolher um filme e receber recomendações.

## Estrutura de Arquivos

```
├── horror_movies.csv       # Dataset de filmes de terror
├── recomendador_terror.py  # Script principal do recomendador
├── requirements.txt        # Dependências do projeto
└── README.md               # Este arquivo de instruções
```

## Notas

- Certifique-se de que o arquivo `horror_movies.csv` esteja no mesmo diretório do script.
- Para abrir o projeto no VS Code, selecione o interpretador dentro de `venv` (Ctrl+Shift+P → Python: Select Interpreter).



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
