import os
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie

class Command(BaseCommand):
    help = 'Importa filmes de terror do arquivo CSV para o banco de dados Django'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv-file',
            type=str,
            default='horror_movies.csv',
            help='Caminho para o arquivo CSV (padrão: horror_movies.csv)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpar todos os filmes existentes antes de importar'
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        
        # Tentar encontrar o arquivo CSV
        csv_paths = [
            csv_file,  # Caminho fornecido pelo usuário
            os.path.join(settings.BASE_DIR, csv_file),  # Dentro do projeto Django
            os.path.join(settings.BASE_DIR, '..', csv_file),  # Diretório pai
        ]
        
        csv_path = None
        for path in csv_paths:
            if os.path.exists(path):
                csv_path = path
                break
        
        if not csv_path:
            self.stdout.write(
                self.style.ERROR(f'Arquivo CSV não encontrado: {csv_file}')
            )
            self.stdout.write('Tentei procurar em:')
            for path in csv_paths:
                self.stdout.write(f'  - {path}')
            return
        
        self.stdout.write(f'Encontrado arquivo CSV: {csv_path}')
        
        # Limpar filmes existentes se solicitado
        if options['clear']:
            self.stdout.write('Removendo filmes existentes...')
            Movie.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS('Filmes removidos com sucesso!')
            )
        
        # Ler arquivo CSV
        try:
            # Tentar diferentes separadores
            try:
                df = pd.read_csv(csv_path, sep=';')
                self.stdout.write(f'Arquivo CSV carregado com separador ";" - {len(df)} registros')
            except:
                df = pd.read_csv(csv_path, sep=',')
                self.stdout.write(f'Arquivo CSV carregado com separador "," - {len(df)} registros')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao ler arquivo CSV: {str(e)}')
            )
            return
        
        # Verificar colunas necessárias
        self.stdout.write(f'Colunas disponíveis no CSV: {list(df.columns)}')
        
        # Mapear colunas do CSV para campos do modelo
        column_mapping = {
            'title': 'title',
            'genre_names': 'genres',  # Mapear genre_names para genres
            'vote_average': 'vote_average',
            'overview': 'overview',
            'vote_count': 'vote_count',
            'release_date': 'release_date',
            'popularity': 'popularity',
            'runtime': 'runtime',
            'budget': 'budget',
            'revenue': 'revenue',
            'original_language': 'original_language',
        }
        
        required_columns = ['title', 'genre_names', 'vote_average']  # Usar genre_names
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            self.stdout.write(
                self.style.ERROR(f'Colunas obrigatórias não encontradas: {missing_columns}')
            )
            self.stdout.write(f'Colunas disponíveis: {list(df.columns)}')
            return
        
        # Contador de importação
        created_count = 0
        updated_count = 0
        error_count = 0
        
        # Importar filmes
        for count, (index, row) in enumerate(df.iterrows(), 1):
            try:
                # Processar data de lançamento
                release_date = None
                if 'release_date' in df.columns and pd.notna(row['release_date']):
                    try:
                        release_date = pd.to_datetime(row['release_date']).date()
                    except:
                        release_date = None
                
                # Buscar ou criar filme
                movie, created = Movie.objects.get_or_create(
                    title=row['title'],
                    defaults={
                        'overview': row.get('overview', '') or '',
                        'genres': row.get('genre_names', '') or '',  # Usar genre_names
                        'vote_average': float(row.get('vote_average', 0) or 0),
                        'vote_count': int(row.get('vote_count', 0) or 0),
                        'release_date': release_date,
                        'popularity': float(row.get('popularity', 0) or 0),
                        'runtime': int(row.get('runtime', 0) or 0) if pd.notna(row.get('runtime')) else None,
                        'budget': int(row.get('budget', 0) or 0) if pd.notna(row.get('budget')) else None,
                        'revenue': int(row.get('revenue', 0) or 0) if pd.notna(row.get('revenue')) else None,
                        'original_language': row.get('original_language', 'en') or 'en',
                    }
                )
                
                if created:
                    created_count += 1
                else:
                    # Atualizar filme existente se necessário
                    updated = False
                    if movie.overview != (row.get('overview', '') or ''):
                        movie.overview = row.get('overview', '') or ''
                        updated = True
                    if movie.genres != (row.get('genre_names', '') or ''):  # Usar genre_names
                        movie.genres = row.get('genre_names', '') or ''
                        updated = True
                    if movie.vote_average != float(row.get('vote_average', 0) or 0):
                        movie.vote_average = float(row.get('vote_average', 0) or 0)
                        updated = True
                    
                    if updated:
                        movie.save()
                        updated_count += 1
                
                # Mostrar progresso a cada 100 filmes
                if count % 100 == 0:
                    self.stdout.write(f'Processados {count} filmes...')
                    
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Erro ao processar filme "{row.get("title", "N/A")}": {str(e)}')
                )
        
        # Resultado final
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('IMPORTAÇÃO CONCLUÍDA!'))
        self.stdout.write(f'Filmes criados: {created_count}')
        self.stdout.write(f'Filmes atualizados: {updated_count}')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'Erros encontrados: {error_count}'))
        
        total_movies = Movie.objects.count()
        self.stdout.write(f'Total de filmes no banco: {total_movies}')
        self.stdout.write('='*50)
