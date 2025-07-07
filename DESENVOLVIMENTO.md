# Configurações de desenvolvimento para o Sistema de Recomendação de Filmes de Terror

## Problemas Comuns do Pylance/IntelliSense

### Imports Django não reconhecidos
Os imports condicionais do Django (como `from movies.models import Movie`) são **intencionais** e funcionam corretamente em tempo de execução. O Pylance/IntelliSense pode mostrar avisos porque:

1. O Django só fica disponível após a configuração dinâmica do path
2. Os imports estão dentro de blocos try/except por design
3. O sistema funciona com fallback para CSV quando Django não está disponível

### Configuração recomendada do VS Code

O arquivo `.vscode/settings.json` foi configurado para:
- Incluir o diretório `frontend` no path de análise
- Configurar o Pylance para modo básico de verificação
- Melhorar o suporte a templates Django

### Estrutura de arquivos adicionais

- `pyrightconfig.json` - Configuração do Pylance/Pyright
- `__init__.py` - Estrutura de pacotes Python
- `.vscode/settings.json` - Configurações do VS Code

## Desenvolvimento

Para desenvolvimento ativo no Django:
```powershell
cd frontend
python manage.py runserver
```

Para uso do backend integrado:
```powershell
python recomendador_terror.py
```

## Notas sobre avisos do linter

Os avisos reportados pelo Pylance são esperados e não indicam problemas reais:
- ✅ `recomendador_terror.py` funciona corretamente com Django + fallback CSV
- ✅ `frontend/movies/views.py` funciona corretamente no contexto Django
- ✅ Imports condicionais são por design para máxima compatibilidade
