#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración centralizada para StreamFlix
Manejo de diferentes entornos: desarrollo, testing, producción
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Configuración base"""
    
    # Configuración básica de Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production'
    
    # Base de datos
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///netflix_clone.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Configuración de uploads
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'app/static/uploads'
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 104857600))  # 100MB
    ALLOWED_EXTENSIONS = set(os.environ.get('ALLOWED_EXTENSIONS', 'mp4,avi,mov,wmv').split(','))
    IMAGE_EXTENSIONS = set(os.environ.get('IMAGE_EXTENSIONS', 'jpg,jpeg,png,webp').split(','))
    
    # Configuración de seguridad
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600  # 1 hora
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 horas
    
    # Configuración de email (para futuras funcionalidades)
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Configuración de logging
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    
    # Configuración de Redis (para futuras funcionalidades de cache)
    REDIS_URL = os.environ.get('REDIS_URL')
    
    # Configuración de API externa
    TMDB_API_KEY = os.environ.get('TMDB_API_KEY')  # Para obtener información de películas
    
    # Configuración de paginación
    MOVIES_PER_PAGE = 12
    USERS_PER_PAGE = 20
    
    # Configuración de cache
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    @staticmethod
    def init_app(app):
        """Inicialización específica de la aplicación"""
        pass

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    
    DEBUG = True
    TESTING = False
    
    # Configuración de seguridad relajada para desarrollo
    SESSION_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    
    # Base de datos de desarrollo
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///netflix_clone_dev.db'
    
    # Logging más verboso
    SQLALCHEMY_ECHO = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configurar logging para desarrollo
        import logging
        from logging import StreamHandler
        
        file_handler = StreamHandler()
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)

class TestingConfig(Config):
    """Configuración para testing"""
    
    TESTING = True
    DEBUG = False
    
    # Base de datos en memoria para tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Desactivar CSRF para tests
    WTF_CSRF_ENABLED = False
    
    # Configuración de seguridad para tests
    SESSION_COOKIE_SECURE = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

class ProductionConfig(Config):
    """Configuración para producción"""
    
    DEBUG = False
    TESTING = False
    
    # Base de datos de producción
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///netflix_clone.db'
    
    # Configuración de seguridad estricta
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Configuración de logging para producción
    SQLALCHEMY_ECHO = False
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Configurar logging para producción
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not app.debug and not app.testing:
            if app.config['LOG_TO_STDOUT']:
                stream_handler = logging.StreamHandler()
                stream_handler.setLevel(logging.INFO)
                app.logger.addHandler(stream_handler)
            else:
                if not os.path.exists('logs'):
                    os.mkdir('logs')
                file_handler = RotatingFileHandler('logs/streamflix.log',
                                                 maxBytes=10240000, backupCount=10)
                file_handler.setFormatter(logging.Formatter(
                    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
                file_handler.setLevel(logging.INFO)
                app.logger.addHandler(file_handler)
            
            app.logger.setLevel(logging.INFO)
            app.logger.info('StreamFlix startup')

class DockerConfig(ProductionConfig):
    """Configuración para contenedores Docker"""
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        # Log to stdout cuando se ejecuta en Docker
        import logging
        from logging import StreamHandler
        
        stream_handler = StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

# Mapeo de configuraciones
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Obtener configuración basada en la variable de entorno FLASK_ENV"""
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default']) 