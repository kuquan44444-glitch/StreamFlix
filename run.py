#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archivo principal para ejecutar la aplicación de streaming Netflix-Clone
"""

import os
from app import create_app

# Crear instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Crear directorio de uploads si no existe
    os.makedirs('app/static/uploads', exist_ok=True)
    os.makedirs('app/static/uploads/videos', exist_ok=True)
    os.makedirs('app/static/uploads/thumbnails', exist_ok=True)
    
    # Ejecutar en modo debug durante desarrollo
    app.run(debug=True, host='0.0.0.0', port=5000) 