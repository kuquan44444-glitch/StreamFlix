#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pruebas unitarias para StreamFlix
"""

import unittest
import os
import tempfile
from app import create_app, db
from app.models import User, Movie, Category
from config import TestingConfig

class StreamFlixTestCase(unittest.TestCase):
    """Clase base para las pruebas de StreamFlix"""
    
    def setUp(self):
        """Configurar entorno de pruebas"""
        self.app = create_app()
        self.app.config.from_object(TestingConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        # Crear todas las tablas
        db.create_all()
        
        # Crear datos de prueba
        self.create_test_data()
    
    def tearDown(self):
        """Limpiar después de las pruebas"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def create_test_data(self):
        """Crear datos de prueba"""
        # Crear categoría de prueba
        self.test_category = Category(name='Acción', description='Películas de acción')
        db.session.add(self.test_category)
        
        # Crear usuario de prueba
        self.test_user = User(
            username='testuser',
            email='test@example.com'
        )
        self.test_user.set_password('testpass123')
        db.session.add(self.test_user)
        
        # Crear usuario administrador de prueba
        self.test_admin = User(
            username='testadmin',
            email='admin@example.com',
            is_admin=True
        )
        self.test_admin.set_password('adminpass123')
        db.session.add(self.test_admin)
        
        db.session.commit()
        
        # Crear película de prueba
        self.test_movie = Movie(
            title='Película de Prueba',
            description='Una película para testing',
            category_id=self.test_category.id,
            uploaded_by=self.test_admin.id,
            year=2024,
            duration=120,
            rating=8.5
        )
        db.session.add(self.test_movie)
        db.session.commit()

class AuthTestCase(StreamFlixTestCase):
    """Pruebas de autenticación"""
    
    def test_user_registration(self):
        """Probar registro de usuario"""
        response = self.client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpass123',
            'password2': 'newpass123',
            'csrf_token': self.get_csrf_token('/auth/register')
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar que el usuario fue creado
        user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'newuser@example.com')
    
    def test_user_login(self):
        """Probar inicio de sesión"""
        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'testpass123',
            'csrf_token': self.get_csrf_token('/auth/login')
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
    
    def test_invalid_login(self):
        """Probar inicio de sesión con credenciales inválidas"""
        response = self.client.post('/auth/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword',
            'csrf_token': self.get_csrf_token('/auth/login')
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email o contrase', response.data)
    
    def test_logout(self):
        """Probar cierre de sesión"""
        # Primero iniciar sesión
        self.login_user('test@example.com', 'testpass123')
        
        # Luego cerrar sesión
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
    
    def get_csrf_token(self, url):
        """Obtener token CSRF para formularios"""
        response = self.client.get(url)
        # En un entorno de prueba real, extraerías el token del HTML
        return 'test-csrf-token'
    
    def login_user(self, email, password):
        """Helper para iniciar sesión"""
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password,
            'csrf_token': self.get_csrf_token('/auth/login')
        }, follow_redirects=True)

class MovieTestCase(StreamFlixTestCase):
    """Pruebas de funcionalidad de películas"""
    
    def test_movie_creation(self):
        """Probar creación de película"""
        movie = Movie(
            title='Nueva Película',
            description='Descripción de prueba',
            category_id=self.test_category.id,
            uploaded_by=self.test_admin.id
        )
        db.session.add(movie)
        db.session.commit()
        
        self.assertIsNotNone(movie.id)
        self.assertEqual(movie.title, 'Nueva Película')
    
    def test_movie_views_increment(self):
        """Probar incremento de visualizaciones"""
        initial_views = self.test_movie.views
        self.test_movie.increment_views()
        
        self.assertEqual(self.test_movie.views, initial_views + 1)
    
    def test_movie_embed_url(self):
        """Probar generación de URL embebida"""
        # Probar URL de YouTube
        self.test_movie.video_url = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
        embed_url = self.test_movie.get_video_embed_url()
        self.assertEqual(embed_url, 'https://www.youtube.com/embed/dQw4w9WgXcQ')
        
        # Probar URL de Vimeo
        self.test_movie.video_url = 'https://vimeo.com/123456789'
        embed_url = self.test_movie.get_video_embed_url()
        self.assertEqual(embed_url, 'https://player.vimeo.com/video/123456789')

class UserTestCase(StreamFlixTestCase):
    """Pruebas de modelo de usuario"""
    
    def test_password_hashing(self):
        """Probar hash de contraseñas"""
        user = User(username='testuser2', email='test2@example.com')
        user.set_password('mypassword')
        
        self.assertNotEqual(user.password_hash, 'mypassword')
        self.assertTrue(user.check_password('mypassword'))
        self.assertFalse(user.check_password('wrongpassword'))
    
    def test_user_representation(self):
        """Probar representación string del usuario"""
        self.assertEqual(str(self.test_user), '<User testuser>')

class CategoryTestCase(StreamFlixTestCase):
    """Pruebas de categorías"""
    
    def test_category_creation(self):
        """Probar creación de categoría"""
        category = Category(name='Comedia', description='Películas divertidas')
        db.session.add(category)
        db.session.commit()
        
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, 'Comedia')
    
    def test_category_movies_relationship(self):
        """Probar relación categoría-películas"""
        self.assertEqual(len(self.test_category.movies), 1)
        self.assertEqual(self.test_category.movies[0], self.test_movie)

class MainRoutesTestCase(StreamFlixTestCase):
    """Pruebas de rutas principales"""
    
    def test_index_page(self):
        """Probar página principal"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'StreamFlix', response.data)
    
    def test_movie_detail_page(self):
        """Probar página de detalle de película"""
        # Iniciar sesión primero
        self.login_user('test@example.com', 'testpass123')
        
        response = self.client.get(f'/movie/{self.test_movie.id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.test_movie.title.encode(), response.data)
    
    def test_movie_detail_requires_login(self):
        """Probar que el detalle de película requiere login"""
        response = self.client.get(f'/movie/{self.test_movie.id}')
        self.assertEqual(response.status_code, 302)  # Redirección a login
    
    def test_search_functionality(self):
        """Probar funcionalidad de búsqueda"""
        response = self.client.get('/search?q=Prueba')
        self.assertEqual(response.status_code, 200)
    
    def login_user(self, email, password):
        """Helper para iniciar sesión"""
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password,
            'csrf_token': 'test-csrf-token'
        }, follow_redirects=True)

class AdminTestCase(StreamFlixTestCase):
    """Pruebas de funcionalidad de administración"""
    
    def test_admin_dashboard_access(self):
        """Probar acceso al dashboard de admin"""
        # Iniciar sesión como admin
        self.login_admin()
        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
    
    def test_non_admin_dashboard_access(self):
        """Probar que usuarios normales no pueden acceder al admin"""
        # Iniciar sesión como usuario normal
        self.login_user('test@example.com', 'testpass123')
        
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirección
    
    def login_admin(self):
        """Helper para iniciar sesión como admin"""
        return self.client.post('/auth/login', data={
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'csrf_token': 'test-csrf-token'
        }, follow_redirects=True)
    
    def login_user(self, email, password):
        """Helper para iniciar sesión"""
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password,
            'csrf_token': 'test-csrf-token'
        }, follow_redirects=True)

if __name__ == '__main__':
    # Configurar y ejecutar las pruebas
    unittest.main(verbosity=2) 