#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rutas principales para Netflix-Clone
"""

from flask import Blueprint, render_template, request, jsonify, current_app, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.models import Movie, Category, AdSpace
from app.forms import SearchForm
from sqlalchemy import or_, desc
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint principal
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página principal - Dashboard tipo Netflix"""
    try:
        # Obtener películas destacadas (máximo 5)
        featured_movies = Movie.query.filter_by(is_featured=True).limit(5).all()
        
        # Obtener películas nuevas del mes (máximo 10)
        new_movies = Movie.query.filter_by(is_new=True).order_by(desc(Movie.created_at)).limit(10).all()
        
        # Obtener películas por categoría (máximo 8 por categoría)
        categories_with_movies = []
        categories = Category.query.all()
        
        for category in categories:
            movies = Movie.query.filter_by(category_id=category.id).limit(8).all()
            if movies:  # Solo incluir categorías con películas
                categories_with_movies.append({
                    'category': category,
                    'movies': movies
                })
        
        # Obtener espacios publicitarios activos
        header_ads = AdSpace.query.filter_by(location='header', is_active=True).all()
        sidebar_ads = AdSpace.query.filter_by(location='sidebar', is_active=True).all()
        footer_ads = AdSpace.query.filter_by(location='footer', is_active=True).all()
        
        # Formulario de búsqueda
        search_form = SearchForm()
        search_form.category.choices = [(0, 'Todas las categorías')] + [(c.id, c.name) for c in categories]
        
        return render_template('main/index.html',
                             featured_movies=featured_movies,
                             new_movies=new_movies,
                             categories_with_movies=categories_with_movies,
                             search_form=search_form,
                             header_ads=header_ads,
                             sidebar_ads=sidebar_ads,
                             footer_ads=footer_ads)
                             
    except Exception as e:
        logger.error(f'Error en página principal: {str(e)}')
        return render_template('errors/500.html'), 500

@main_bp.route('/movie/<int:movie_id>')
@login_required
def movie_detail(movie_id):
    """Página de detalle de película"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        
        # Incrementar contador de visualizaciones
        movie.increment_views()
        
        # Obtener películas relacionadas de la misma categoría
        related_movies = Movie.query.filter(
            Movie.category_id == movie.category_id,
            Movie.id != movie.id
        ).limit(6).all()
        
        # Obtener anuncios entre películas
        between_ads = AdSpace.query.filter_by(location='between_movies', is_active=True).all()
        
        return render_template('main/movie_detail.html',
                             movie=movie,
                             related_movies=related_movies,
                             between_ads=between_ads)
                             
    except Exception as e:
        logger.error(f'Error al mostrar película {movie_id}: {str(e)}')
        return render_template('errors/404.html'), 404

@main_bp.route('/watch/<int:movie_id>')
@login_required
def watch_movie(movie_id):
    """Página del reproductor de video"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        
        # Verificar que la película tenga contenido para reproducir
        if not movie.video_file and not movie.video_url:
            flash('Esta película no está disponible para reproducción.', 'warning')
            return redirect(url_for('main.movie_detail', movie_id=movie_id))
        
        # Incrementar visualizaciones
        movie.increment_views()
        
        return render_template('main/watch.html', movie=movie)
        
    except Exception as e:
        logger.error(f'Error al reproducir película {movie_id}: {str(e)}')
        return render_template('errors/404.html'), 404

@main_bp.route('/category/<int:category_id>')
def category_movies(category_id):
    """Página de películas por categoría"""
    try:
        category = Category.query.get_or_404(category_id)
        
        # Paginación
        page = request.args.get('page', 1, type=int)
        per_page = 12  # Películas por página
        
        movies = Movie.query.filter_by(category_id=category_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('main/category.html',
                             category=category,
                             movies=movies)
                             
    except Exception as e:
        logger.error(f'Error al mostrar categoría {category_id}: {str(e)}')
        return render_template('errors/404.html'), 404

@main_bp.route('/search', methods=['GET', 'POST'])
def search():
    """Página de búsqueda de películas"""
    form = SearchForm()
    
    # Cargar categorías para el formulario
    categories = Category.query.all()
    form.category.choices = [(0, 'Todas las categorías')] + [(c.id, c.name) for c in categories]
    
    movies = []
    query = None
    selected_category = None
    
    if form.validate_on_submit():
        query = form.query.data.strip()
        selected_category = form.category.data if form.category.data != 0 else None
        
        try:
            # Construir consulta de búsqueda
            search_query = Movie.query
            
            # Filtrar por término de búsqueda
            if query:
                search_query = search_query.filter(
                    or_(
                        Movie.title.contains(query),
                        Movie.description.contains(query),
                        Movie.director.contains(query),
                        Movie.actors.contains(query)
                    )
                )
            
            # Filtrar por categoría
            if selected_category:
                search_query = search_query.filter_by(category_id=selected_category)
            
            # Ordenar por relevancia (título primero, luego por fecha)
            movies = search_query.order_by(desc(Movie.created_at)).all()
            
        except Exception as e:
            logger.error(f'Error en búsqueda: {str(e)}')
            flash('Error durante la búsqueda. Intenta nuevamente.', 'danger')
    
    # Para peticiones GET, obtener parámetros de la URL
    elif request.method == 'GET':
        query = request.args.get('q', '').strip()
        selected_category = request.args.get('category', type=int)
        
        if query or selected_category:
            form.query.data = query
            if selected_category:
                form.category.data = selected_category
            
            # Realizar búsqueda
            try:
                search_query = Movie.query
                
                if query:
                    search_query = search_query.filter(
                        or_(
                            Movie.title.contains(query),
                            Movie.description.contains(query),
                            Movie.director.contains(query),
                            Movie.actors.contains(query)
                        )
                    )
                
                if selected_category:
                    search_query = search_query.filter_by(category_id=selected_category)
                
                movies = search_query.order_by(desc(Movie.created_at)).all()
                
            except Exception as e:
                logger.error(f'Error en búsqueda GET: {str(e)}')
    
    return render_template('main/search.html',
                         form=form,
                         movies=movies,
                         query=query,
                         selected_category=selected_category)

@main_bp.route('/api/movies/trending')
def api_trending_movies():
    """API endpoint para películas en tendencia"""
    try:
        # Películas más vistas en los últimos 30 días
        trending = Movie.query.order_by(desc(Movie.views)).limit(10).all()
        
        movies_data = []
        for movie in trending:
            movies_data.append({
                'id': movie.id,
                'title': movie.title,
                'thumbnail': movie.thumbnail,
                'views': movie.views,
                'rating': movie.rating,
                'category': movie.category.name
            })
        
        return jsonify({
            'success': True,
            'movies': movies_data
        })
        
    except Exception as e:
        logger.error(f'Error en API trending: {str(e)}')
        return jsonify({
            'success': False,
            'error': 'Error al obtener películas en tendencia'
        }), 500

@main_bp.errorhandler(404)
def not_found(error):
    """Manejador de error 404"""
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    """Manejador de error 500"""
    db.session.rollback()
    return render_template('errors/500.html'), 500 