#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rutas de administración para Netflix-Clone
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Movie, Category, User, AdSpace
from app.forms import MovieForm, CategoryForm, AdSpaceForm
from functools import wraps
import os
import uuid
from PIL import Image
import logging

# Configurar logging
logger = logging.getLogger(__name__)

# Crear blueprint de administración
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorador para requerir permisos de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Necesitas permisos de administrador para acceder a esta página.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Panel de administración principal"""
    try:
        # Estadísticas generales
        total_movies = Movie.query.count()
        total_users = User.query.count()
        total_categories = Category.query.count()
        featured_movies = Movie.query.filter_by(is_featured=True).count()
        
        # Películas más vistas
        top_movies = Movie.query.order_by(Movie.views.desc()).limit(5).all()
        
        # Usuarios más recientes
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        
        stats = {
            'total_movies': total_movies,
            'total_users': total_users,
            'total_categories': total_categories,
            'featured_movies': featured_movies,
            'top_movies': top_movies,
            'recent_users': recent_users
        }
        
        return render_template('admin/dashboard.html', stats=stats)
        
    except Exception as e:
        logger.error(f'Error en dashboard admin: {str(e)}')
        flash('Error al cargar el panel de administración.', 'danger')
        return redirect(url_for('main.index'))

@admin_bp.route('/movies')
@login_required
@admin_required
def movies():
    """Lista de todas las películas"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 12
        
        movies = Movie.query.order_by(Movie.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/movies.html', movies=movies)
        
    except Exception as e:
        logger.error(f'Error al cargar películas admin: {str(e)}')
        flash('Error al cargar las películas.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/movies/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_movie():
    """Agregar nueva película"""
    form = MovieForm()
    
    # Cargar categorías para el formulario
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        try:
            # Crear nueva película
            movie = Movie(
                title=form.title.data,
                description=form.description.data,
                category_id=form.category_id.data,
                duration=form.duration.data,
                year=form.year.data,
                director=form.director.data,
                actors=form.actors.data,
                video_url=form.video_url.data,
                trailer_url=form.trailer_url.data,
                is_featured=form.is_featured.data,
                is_new=form.is_new.data,
                rating=form.rating.data or 0.0,
                uploaded_by=current_user.id
            )
            
            # Procesar archivo de miniatura
            if form.thumbnail.data:
                thumbnail_file = save_thumbnail(form.thumbnail.data)
                if thumbnail_file:
                    movie.thumbnail = thumbnail_file
            
            # Procesar archivo de video
            if form.video_file.data:
                video_file = save_video(form.video_file.data)
                if video_file:
                    movie.video_file = video_file
            
            db.session.add(movie)
            db.session.commit()
            
            logger.info(f'Nueva película agregada: {movie.title} por {current_user.username}')
            flash('Película agregada exitosamente.', 'success')
            return redirect(url_for('admin.movies'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error al agregar película: {str(e)}')
            flash('Error al agregar la película. Intenta nuevamente.', 'danger')
    
    return render_template('admin/add_movie.html', form=form)

@admin_bp.route('/movies/edit/<int:movie_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_movie(movie_id):
    """Editar película existente"""
    movie = Movie.query.get_or_404(movie_id)
    form = MovieForm(obj=movie)
    
    # Cargar categorías para el formulario
    categories = Category.query.all()
    form.category_id.choices = [(c.id, c.name) for c in categories]
    
    if form.validate_on_submit():
        try:
            # Actualizar datos de la película
            movie.title = form.title.data
            movie.description = form.description.data
            movie.category_id = form.category_id.data
            movie.duration = form.duration.data
            movie.year = form.year.data
            movie.director = form.director.data
            movie.actors = form.actors.data
            movie.video_url = form.video_url.data
            movie.trailer_url = form.trailer_url.data
            movie.is_featured = form.is_featured.data
            movie.is_new = form.is_new.data
            movie.rating = form.rating.data or movie.rating
            
            # Procesar nueva miniatura si se proporciona
            if form.thumbnail.data:
                # Eliminar miniatura anterior si existe
                if movie.thumbnail:
                    delete_file(movie.thumbnail)
                
                thumbnail_file = save_thumbnail(form.thumbnail.data)
                if thumbnail_file:
                    movie.thumbnail = thumbnail_file
            
            # Procesar nuevo video si se proporciona
            if form.video_file.data:
                # Eliminar video anterior si existe
                if movie.video_file:
                    delete_file(movie.video_file)
                
                video_file = save_video(form.video_file.data)
                if video_file:
                    movie.video_file = video_file
            
            db.session.commit()
            
            logger.info(f'Película editada: {movie.title} por {current_user.username}')
            flash('Película actualizada exitosamente.', 'success')
            return redirect(url_for('admin.movies'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error al editar película {movie_id}: {str(e)}')
            flash('Error al actualizar la película. Intenta nuevamente.', 'danger')
    
    return render_template('admin/edit_movie.html', form=form, movie=movie)

@admin_bp.route('/movies/delete/<int:movie_id>', methods=['POST'])
@login_required
@admin_required
def delete_movie(movie_id):
    """Eliminar película"""
    try:
        movie = Movie.query.get_or_404(movie_id)
        
        # Eliminar archivos asociados
        if movie.thumbnail:
            delete_file(movie.thumbnail)
        if movie.video_file:
            delete_file(movie.video_file)
        
        db.session.delete(movie)
        db.session.commit()
        
        logger.info(f'Película eliminada: {movie.title} por {current_user.username}')
        flash('Película eliminada exitosamente.', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error al eliminar película {movie_id}: {str(e)}')
        flash('Error al eliminar la película.', 'danger')
    
    return redirect(url_for('admin.movies'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories():
    """Lista de categorías"""
    try:
        categories = Category.query.all()
        return render_template('admin/categories.html', categories=categories)
        
    except Exception as e:
        logger.error(f'Error al cargar categorías: {str(e)}')
        flash('Error al cargar las categorías.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/categories/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_category():
    """Agregar nueva categoría"""
    form = CategoryForm()
    
    if form.validate_on_submit():
        try:
            # Verificar que no exista la categoría
            existing = Category.query.filter_by(name=form.name.data).first()
            if existing:
                flash('Ya existe una categoría con ese nombre.', 'danger')
                return render_template('admin/add_category.html', form=form)
            
            category = Category(
                name=form.name.data,
                description=form.description.data
            )
            
            db.session.add(category)
            db.session.commit()
            
            logger.info(f'Nueva categoría agregada: {category.name} por {current_user.username}')
            flash('Categoría agregada exitosamente.', 'success')
            return redirect(url_for('admin.categories'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error al agregar categoría: {str(e)}')
            flash('Error al agregar la categoría.', 'danger')
    
    return render_template('admin/add_category.html', form=form)

@admin_bp.route('/ads')
@login_required
@admin_required
def ads():
    """Gestión de espacios publicitarios"""
    try:
        ads = AdSpace.query.all()
        return render_template('admin/ads.html', ads=ads)
        
    except Exception as e:
        logger.error(f'Error al cargar anuncios: {str(e)}')
        flash('Error al cargar los anuncios.', 'danger')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Lista de usuarios"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        users = User.query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/users.html', users=users)
        
    except Exception as e:
        logger.error(f'Error al cargar usuarios: {str(e)}')
        flash('Error al cargar los usuarios.', 'danger')
        return redirect(url_for('admin.dashboard'))

def save_thumbnail(thumbnail_file):
    """Guardar archivo de miniatura con redimensionado"""
    try:
        if not thumbnail_file:
            return None
        
        # Generar nombre único
        filename = secure_filename(thumbnail_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Crear directorio si no existe
        thumbnails_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails')
        os.makedirs(thumbnails_dir, exist_ok=True)
        
        # Ruta completa del archivo
        file_path = os.path.join(thumbnails_dir, unique_filename)
        
        # Guardar archivo temporalmente
        thumbnail_file.save(file_path)
        
        # Redimensionar imagen
        with Image.open(file_path) as img:
            # Convertir a RGB si es necesario
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Redimensionar manteniendo aspecto (máximo 400x600)
            img.thumbnail((400, 600), Image.Resampling.LANCZOS)
            img.save(file_path, 'JPEG', quality=85, optimize=True)
        
        return f"uploads/thumbnails/{unique_filename}"
        
    except Exception as e:
        logger.error(f'Error al guardar miniatura: {str(e)}')
        return None

def save_video(video_file):
    """Guardar archivo de video"""
    try:
        if not video_file:
            return None
        
        # Generar nombre único
        filename = secure_filename(video_file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Crear directorio si no existe
        videos_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'videos')
        os.makedirs(videos_dir, exist_ok=True)
        
        # Ruta completa del archivo
        file_path = os.path.join(videos_dir, unique_filename)
        
        # Guardar archivo
        video_file.save(file_path)
        
        return f"uploads/videos/{unique_filename}"
        
    except Exception as e:
        logger.error(f'Error al guardar video: {str(e)}')
        return None

def delete_file(file_path):
    """Eliminar archivo del sistema"""
    try:
        if file_path:
            full_path = os.path.join(current_app.root_path, 'static', file_path)
            if os.path.exists(full_path):
                os.remove(full_path)
                logger.info(f'Archivo eliminado: {file_path}')
    except Exception as e:
        logger.error(f'Error al eliminar archivo {file_path}: {str(e)}')

@admin_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Servir archivos subidos"""
    upload_dir = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_dir, filename) 