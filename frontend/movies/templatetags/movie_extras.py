"""
Template tags personalizadas para o sistema de filmes
"""
from django import template
import requests
from functools import lru_cache
from django.conf import settings

register = template.Library()

TMDB_API_KEY = getattr(settings, 'TMDB_API_KEY', None)  # configure TMDB_API_KEY no settings.py
DEFAULT_POSTER_URL = getattr(settings, 'DEFAULT_POSTER_URL', settings.STATIC_URL + 'movies/img/no_poster.png')  # fallback local se sem poster TMDB

@lru_cache(maxsize=256)
def fetch_poster_path(title):
    try:
        url = 'https://api.themoviedb.org/3/search/movie'
        params = {'api_key': TMDB_API_KEY, 'query': title}
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get('results'):
            path = data['results'][0].get('poster_path')
            if path:
                return f'https://image.tmdb.org/t/p/w500{path}'
    except Exception:
        pass
    return None

@register.filter
def poster_url(title):
    path = fetch_poster_path(title)
    return path or DEFAULT_POSTER_URL

@register.filter
def split(value, separator):
    """Divide uma string usando o separador especificado"""
    if value:
        return value.split(separator)
    return []

@register.filter  
def mul(value, arg):
    """Multiplica dois valores"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """Divide dois valores"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@lru_cache(maxsize=256)
def fetch_overview(title):
    """Busca a sinopse do filme no TMDB pela palavra-chave de título"""
    try:
        url = 'https://api.themoviedb.org/3/search/movie'
        params = {'api_key': TMDB_API_KEY, 'query': title}
        resp = requests.get(url, params=params, timeout=5)
        data = resp.json()
        if data.get('results'):
            overview = data['results'][0].get('overview')
            if overview:
                return overview
    except Exception:
        pass
    return ''

@register.filter
def overview(title):
    """Retorna a sinopse do filme usando a API do TMDB"""
    return fetch_overview(title)
