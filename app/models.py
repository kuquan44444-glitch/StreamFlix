#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de base de datos para Netflix-Clone
"""

from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import bcrypt

class User(UserMixin, db.Model):
    """Modelo de usuario con autenticación segura"""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        """Establecer contraseña hasheada con bcrypt"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        self.password_hash = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Verificar contraseña"""
        if isinstance(password, str):
            password = password.encode('utf-8')
        return bcrypt.checkpw(password, self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f'<User {self.username}>'

class Category(db.Model):
    """Modelo de categoría de películas"""
    
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación uno a muchos con películas
    movies = db.relationship('Movie', backref='category', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Movie(db.Model):
    """Modelo de película"""
    
    __tablename__ = 'movies'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    duration = db.Column(db.Integer)  # Duración en minutos
    year = db.Column(db.Integer)
    director = db.Column(db.String(100))
    actors = db.Column(db.Text)
    
    # Archivos multimedia
    thumbnail = db.Column(db.String(255))  # Ruta de la miniatura
    video_file = db.Column(db.String(255))  # Ruta del archivo de video
    video_url = db.Column(db.String(500))  # URL de YouTube/Vimeo
    trailer_url = db.Column(db.String(500))  # URL del trailer
    
    # Estado y metadatos
    is_featured = db.Column(db.Boolean, default=False)  # Película destacada
    is_new = db.Column(db.Boolean, default=True)  # Nueva del mes
    views = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)  # Calificación promedio
    
    # Relaciones
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relación con usuario que subió la película
    uploader = db.relationship('User', backref='uploaded_movies')
    
    def increment_views(self):
        """Incrementar contador de visualizaciones"""
        self.views += 1
        db.session.commit()
    
    def get_video_embed_url(self):
        """Obtener URL embebida para reproducción"""
        if self.video_url:
            # Convertir URLs de YouTube a formato embebido
            if 'youtube.com/watch?v=' in self.video_url:
                video_id = self.video_url.split('v=')[1].split('&')[0]
                return f'https://www.youtube.com/embed/{video_id}'
            elif 'youtu.be/' in self.video_url:
                video_id = self.video_url.split('/')[-1].split('?')[0]
                return f'https://www.youtube.com/embed/{video_id}'
            # Convertir URLs de Vimeo a formato embebido
            elif 'vimeo.com/' in self.video_url:
                video_id = self.video_url.split('/')[-1]
                return f'https://player.vimeo.com/video/{video_id}'
            else:
                return self.video_url
        return None
    
    def __repr__(self):
        return f'<Movie {self.title}>'

class AdSpace(db.Model):
    """Modelo para espacios publicitarios"""
    
    __tablename__ = 'ad_spaces'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nombre del espacio publicitario
    location = db.Column(db.String(50), nullable=False)  # header, sidebar, footer, between_movies
    ad_code = db.Column(db.Text)  # Código HTML del anuncio
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdSpace {self.name} - {self.location}>' 