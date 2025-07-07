from django.core.management.base import BaseCommand
from movies.models import Movie
from movies.templatetags.movie_extras import fetch_overview

class Command(BaseCommand):
    help = 'Popula o campo overview dos filmes no banco usando a API do TMDB para títulos sem sinopse.'

    def handle(self, *args, **options):
        movies = Movie.objects.filter(overview__isnull=True) | Movie.objects.filter(overview__exact='')
        total = movies.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('Não há filmes sem sinopse para atualizar.'))
            return

        self.stdout.write(f'Encontrados {total} filmes sem sinopse. Iniciando atualização...')
        updated = 0
        for movie in movies:
            sinopse = fetch_overview(movie.title)
            if sinopse:
                movie.overview = sinopse
                movie.save(update_fields=['overview'])
                updated += 1
                self.stdout.write(f'[{updated}/{total}] Atualizado: {movie.title}')
            else:
                self.stdout.write(f'[{updated}/{total}] Sem sinopse: {movie.title}')

        self.stdout.write(self.style.SUCCESS(f'Processamento concluído. Sinopses atualizadas: {updated} de {total}.'))
