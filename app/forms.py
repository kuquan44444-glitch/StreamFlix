#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Formularios WTF con validación para Netflix-Clone
"""

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, TextAreaField, SelectField, IntegerField, BooleanField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, NumberRange, Optional, URL
import os

class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido.'),
        Email(message='Ingresa un email válido.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida.')
    ])

class RegisterForm(FlaskForm):
    """Formulario de registro de usuario"""
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(message='El nombre de usuario es requerido.'),
        Length(min=3, max=20, message='El nombre debe tener entre 3 y 20 caracteres.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido.'),
        Email(message='Ingresa un email válido.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida.'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres.')
    ])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Confirma tu contraseña.'),
        EqualTo('password', message='Las contraseñas deben coincidir.')
    ])

class MovieForm(FlaskForm):
    """Formulario para agregar/editar películas"""
    title = StringField('Título', validators=[
        DataRequired(message='El título es requerido.'),
        Length(max=200, message='El título no puede exceder 200 caracteres.')
    ])
    description = TextAreaField('Descripción', validators=[
        DataRequired(message='La descripción es requerida.')
    ])
    category_id = SelectField('Categoría', coerce=int, validators=[
        DataRequired(message='Selecciona una categoría.')
    ])
    duration = IntegerField('Duración (minutos)', validators=[
        Optional(),
        NumberRange(min=1, max=1000, message='La duración debe estar entre 1 y 1000 minutos.')
    ])
    year = IntegerField('Año', validators=[
        Optional(),
        NumberRange(min=1900, max=2030, message='Ingresa un año válido.')
    ])
    director = StringField('Director', validators=[
        Optional(),
        Length(max=100, message='El nombre del director no puede exceder 100 caracteres.')
    ])
    actors = TextAreaField('Actores principales', validators=[Optional()])
    
    # Archivos multimedia
    thumbnail = FileField('Miniatura', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Solo se permiten imágenes (JPG, PNG, WEBP).')
    ])
    video_file = FileField('Archivo de Video', validators=[
        FileAllowed(['mp4', 'avi', 'mov', 'wmv'], 'Solo se permiten videos (MP4, AVI, MOV, WMV).')
    ])
    video_url = URLField('URL de Video (YouTube/Vimeo)', validators=[
        Optional(),
        URL(message='Ingresa una URL válida.')
    ])
    trailer_url = URLField('URL del Trailer', validators=[
        Optional(),
        URL(message='Ingresa una URL válida.')
    ])
    
    # Estado
    is_featured = BooleanField('Película Destacada')
    is_new = BooleanField('Nueva del Mes')
    rating = IntegerField('Calificación (1-10)', validators=[
        Optional(),
        NumberRange(min=1, max=10, message='La calificación debe estar entre 1 y 10.')
    ])

class CategoryForm(FlaskForm):
    """Formulario para agregar/editar categorías"""
    name = StringField('Nombre de la Categoría', validators=[
        DataRequired(message='El nombre es requerido.'),
        Length(max=100, message='El nombre no puede exceder 100 caracteres.')
    ])
    description = TextAreaField('Descripción', validators=[Optional()])

class SearchForm(FlaskForm):
    """Formulario de búsqueda"""
    query = StringField('Buscar películas...', validators=[
        DataRequired(message='Ingresa un término de búsqueda.'),
        Length(min=2, max=100, message='La búsqueda debe tener entre 2 y 100 caracteres.')
    ])
    category = SelectField('Categoría', coerce=int, validators=[Optional()])

class AdSpaceForm(FlaskForm):
    """Formulario para espacios publicitarios"""
    name = StringField('Nombre del Espacio', validators=[
        DataRequired(message='El nombre es requerido.'),
        Length(max=100, message='El nombre no puede exceder 100 caracteres.')
    ])
    location = SelectField('Ubicación', choices=[
        ('header', 'Cabecera'),
        ('sidebar', 'Barra Lateral'),
        ('footer', 'Pie de Página'),
        ('between_movies', 'Entre Películas')
    ], validators=[DataRequired(message='Selecciona una ubicación.')])
    ad_code = TextAreaField('Código del Anuncio (HTML)', validators=[
        DataRequired(message='El código del anuncio es requerido.')
    ])
    is_active = BooleanField('Activo')

def validate_file_size(form, field):
    """Validador personalizado para tamaño de archivo"""
    if field.data:
        # Verificar tamaño del archivo (máximo 100MB)
        max_size = 100 * 1024 * 1024  # 100MB en bytes
        if len(field.data.read()) > max_size:
            field.data.seek(0)  # Resetear el puntero del archivo
            raise ValidationError('El archivo es demasiado grande. Máximo 100MB permitido.')
        field.data.seek(0)  # Resetear el puntero del archivo 