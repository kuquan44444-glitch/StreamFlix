#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inicialización de la aplicación Flask Netflix-Clone
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración de la aplicación
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///netflix_clone.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    app.config['MAX_CONTENT_LENGTH'] = int(os.environ.get('MAX_CONTENT_LENGTH', 104857600))  # 100MB
    
    # Configuración de seguridad
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'info'
    
    # Importar modelos antes de crear las tablas
    from app.models import User, Movie, Category
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    
    # Crear tablas de base de datos
    with app.app_context():
        db.create_all()
        
        # Crear usuario administrador por defecto si no existe
        admin_user = User.query.filter_by(email='admin@netflix.com').first()
        if not admin_user:
            from app.models import User
            admin = User(
                username='admin',
                email='admin@netflix.com',
                is_admin=True
            )
            admin.set_password('admin123')  # Cambiar en producción
            db.session.add(admin)
            
            # Crear categorías por defecto
            default_categories = ['Acción', 'Comedia', 'Drama', 'Terror', 'Ciencia Ficción', 'Romance', 'Documental']
            for cat_name in default_categories:
                if not Category.query.filter_by(name=cat_name).first():
                    category = Category(name=cat_name)
                    db.session.add(category)
            
            db.session.commit()
    
    # Registrar funciones de contexto global
    @app.context_processor
    def inject_global_vars():
        """Inyectar variables globales en todas las plantillas"""
        from app.models import Category
        return dict(
            get_categories=lambda: Category.query.all()
        )
    
    return app

@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login"""
    from app.models import User
    return User.query.get(int(user_id)) 