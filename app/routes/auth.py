#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rutas de autenticación para Netflix-Clone
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User
from app.forms import LoginForm, RegisterForm
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear blueprint de autenticación
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Ruta de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        try:
            # Buscar usuario por email
            user = User.query.filter_by(email=form.email.data.lower().strip()).first()
            
            if user and user.check_password(form.password.data):
                if not user.is_active:
                    flash('Tu cuenta ha sido desactivada. Contacta al administrador.', 'warning')
                    return render_template('auth/login.html', form=form)
                
                # Actualizar último login
                user.last_login = datetime.utcnow()
                db.session.commit()
                
                # Iniciar sesión
                login_user(user, remember=True)
                
                logger.info(f'Usuario {user.username} ha iniciado sesión exitosamente')
                flash(f'¡Bienvenido {user.username}!', 'success')
                
                # Redirigir a la página solicitada o al inicio
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.index'))
            else:
                flash('Email o contraseña incorrectos.', 'danger')
                logger.warning(f'Intento fallido de login para email: {form.email.data}')
                
        except Exception as e:
            logger.error(f'Error durante el login: {str(e)}')
            flash('Ocurrió un error durante el inicio de sesión.', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Ruta de registro de usuario"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        try:
            # Verificar que no exista el usuario o email
            existing_user = User.query.filter(
                (User.username == form.username.data.lower().strip()) |
                (User.email == form.email.data.lower().strip())
            ).first()
            
            if existing_user:
                if existing_user.username == form.username.data.lower().strip():
                    flash('Este nombre de usuario ya está registrado.', 'danger')
                else:
                    flash('Este email ya está registrado.', 'danger')
                return render_template('auth/register.html', form=form)
            
            # Crear nuevo usuario
            user = User(
                username=form.username.data.lower().strip(),
                email=form.email.data.lower().strip()
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            logger.info(f'Nuevo usuario registrado: {user.username}')
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error durante el registro: {str(e)}')
            flash('Ocurrió un error durante el registro. Intenta nuevamente.', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Ruta de cierre de sesión"""
    username = current_user.username
    logout_user()
    logger.info(f'Usuario {username} ha cerrado sesión')
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """Ruta del perfil de usuario"""
    return render_template('auth/profile.html', user=current_user) 