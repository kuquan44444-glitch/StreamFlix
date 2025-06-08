# StreamFlix - Plataforma de Streaming Netflix-Clone

Una plataforma de streaming profesional desarrollada con Flask, diseñada para ser fácil de mantener, segura y completamente responsiva.

## 🎬 Características

### Funcionalidades Principales
- **Autenticación Segura**: Registro e inicio de sesión con contraseñas encriptadas (bcrypt)
- **Panel de Administración**: Gestión completa de películas, categorías y usuarios
- **Reproductor de Video**: Soporte para archivos MP4 locales y videos de YouTube/Vimeo
- **Búsqueda Avanzada**: Búsqueda por título, categoría, director y actores
- **Categorización**: Organización de contenido por categorías personalizables
- **Sistema de Calificaciones**: Calificación y visualización de estadísticas
- **Espacios Publicitarios**: Integración para Google AdSense y banners personalizados

### Características Técnicas
- **Diseño Responsivo**: Adaptado para móviles, tablets y escritorio
- **Seguridad Robusta**: Protección CSRF, validación de formularios, prevención XSS
- **Optimización**: Lazy loading, compresión de imágenes, caching
- **Base de Datos**: SQLite para fácil mantenimiento
- **API REST**: Endpoints para integración con aplicaciones móviles

## 🛠️ Tecnologías Utilizadas

### Backend
- **Flask 2.3.3**: Framework web principal
- **SQLAlchemy**: ORM para base de datos
- **Flask-Login**: Gestión de sesiones de usuario
- **Flask-WTF**: Formularios y protección CSRF
- **bcrypt**: Encriptación de contraseñas
- **Pillow**: Procesamiento de imágenes

### Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos con variables CSS
- **Bootstrap 5**: Framework CSS responsivo
- **JavaScript ES6**: Funcionalidades interactivas
- **Font Awesome**: Iconografía
- **Google Fonts**: Tipografía

### Base de Datos
- **SQLite**: Base de datos ligera y portable

## 📋 Requisitos del Sistema

### Desarrollo
- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- 2GB RAM mínimo
- 5GB espacio en disco

### Producción (VPS)
- Ubuntu 20.04 LTS o superior
- 2 vCPU
- 2.5 GB RAM
- 40 GB SSD
- Nginx
- Gunicorn

## 🚀 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/streamflix.git
cd streamflix
```

### 2. Crear Entorno Virtual
```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Edita el archivo `.env`:
```env
SECRET_KEY=tu_clave_secreta_super_segura_aqui_cambiala
DATABASE_URL=sqlite:///netflix_clone.db
FLASK_ENV=development
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=104857600
ALLOWED_EXTENSIONS=mp4,avi,mov,wmv
IMAGE_EXTENSIONS=jpg,jpeg,png,webp
```

### 5. Ejecutar la Aplicación
```bash
python run.py
```

La aplicación estará disponible en `http://localhost:5000`

## 👤 Credenciales por Defecto

**Administrador:**
- Email: `admin@netflix.com`
- Contraseña: `admin123`

> ⚠️ **Importante**: Cambia estas credenciales inmediatamente en producción.

## 📁 Estructura del Proyecto

```
streamflix/
├── app/
│   ├── __init__.py              # Configuración de la aplicación
│   ├── models.py                # Modelos de base de datos
│   ├── forms.py                 # Formularios WTF
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # Rutas de autenticación
│   │   ├── main.py              # Rutas principales
│   │   └── admin.py             # Rutas de administración
│   ├── templates/
│   │   ├── base.html            # Template base
│   │   ├── main/                # Templates principales
│   │   ├── auth/                # Templates de autenticación
│   │   └── admin/               # Templates de administración
│   └── static/
│       ├── css/
│       │   └── style.css        # Estilos personalizados
│       ├── js/
│       │   └── script.js        # JavaScript personalizado
│       └── uploads/             # Archivos subidos
│           ├── videos/          # Videos
│           └── thumbnails/      # Miniaturas
├── run.py                       # Archivo principal
├── requirements.txt             # Dependencias
├── .env                         # Variables de entorno
└── README.md                    # Documentación
```

## 🌐 Despliegue en VPS

### Configuración del Servidor (Ubuntu)

#### 1. Actualizar el Sistema
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Instalar Dependencias
```bash
sudo apt install python3 python3-pip python3-venv nginx supervisor -y
```

#### 3. Configurar Usuario de Aplicación
```bash
sudo adduser streamflix
sudo usermod -aG sudo streamflix
su - streamflix
```

#### 4. Clonar y Configurar la Aplicación
```bash
git clone https://github.com/tu-usuario/streamflix.git
cd streamflix
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 5. Configurar Variables de Entorno para Producción
```bash
nano .env
```

```env
SECRET_KEY=clave_super_segura_para_produccion
DATABASE_URL=sqlite:///netflix_clone.db
FLASK_ENV=production
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=104857600
ALLOWED_EXTENSIONS=mp4,avi,mov,wmv
IMAGE_EXTENSIONS=jpg,jpeg,png,webp
```

#### 6. Configurar Gunicorn
Crear archivo `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 2
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

#### 7. Configurar Supervisor
Crear `/etc/supervisor/conf.d/streamflix.conf`:
```ini
[program:streamflix]
command=/home/streamflix/streamflix/venv/bin/gunicorn -c gunicorn.conf.py run:app
directory=/home/streamflix/streamflix
user=streamflix
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/streamflix.log
```

#### 8. Configurar Nginx
Crear `/etc/nginx/sites-available/streamflix`:
```nginx
server {
    listen 80;
    server_name tu-dominio.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/streamflix/streamflix/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias /home/streamflix/streamflix/app/static/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 9. Activar Configuraciones
```bash
sudo ln -s /etc/nginx/sites-available/streamflix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamflix
```

#### 10. Configurar SSL con Let's Encrypt (Opcional)
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d tu-dominio.com
```

## 🔧 Configuración Avanzada

### Optimización de Rendimiento
1. **Compresión de Imágenes**: Las miniaturas se redimensionan automáticamente
2. **Lazy Loading**: Carga diferida de imágenes
3. **Caching**: Headers de cache para archivos estáticos
4. **Minificación**: Compresión de CSS y JS en producción

### Seguridad
1. **HTTPS**: Configurar SSL/TLS
2. **Firewall**: Configurar UFW
3. **Fail2Ban**: Protección contra ataques de fuerza bruta
4. **Backups**: Configurar copias de seguridad automáticas

### Monitoreo
1. **Logs**: Configurar rotación de logs
2. **Métricas**: Implementar monitoreo de recursos
3. **Alertas**: Configurar notificaciones de errores

## 📱 Uso de la Plataforma

### Para Usuarios
1. **Registro**: Crear cuenta con email y contraseña
2. **Navegación**: Explorar películas por categorías
3. **Búsqueda**: Encontrar contenido específico
4. **Reproducción**: Ver películas en streaming

### Para Administradores
1. **Gestión de Contenido**: Subir y organizar películas
2. **Gestión de Usuarios**: Administrar cuentas de usuario
3. **Configuración**: Personalizar categorías y anuncios
4. **Estadísticas**: Monitorear uso de la plataforma

## 🔍 Solución de Problemas

### Problemas Comunes

#### Error de Permisos de Archivos
```bash
sudo chown -R streamflix:streamflix /home/streamflix/streamflix
sudo chmod -R 755 /home/streamflix/streamflix
```

#### Base de Datos No Se Crea
```bash
cd /home/streamflix/streamflix
source venv/bin/activate
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

#### Videos No Se Reproducen
1. Verificar formato de video (MP4 recomendado)
2. Comprobar tamaño de archivo (máximo 100MB)
3. Verificar permisos de directorio uploads

#### Error 502 Bad Gateway
1. Verificar que Gunicorn esté ejecutándose
2. Comprobar logs: `sudo tail -f /var/log/streamflix.log`
3. Reiniciar servicios: `sudo supervisorctl restart streamflix`

## 📊 Información del VPS

**Servidor Configurado:**
- **IP**: 107.174.133.202
- **Usuario**: root
- **Contraseña**: n5X5dB6xPLJj06qr4C
- **Puerto SSH**: 22

> ⚠️ **Seguridad**: Cambia la contraseña root y configura autenticación por clave SSH.

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas:
- **Email**: soporte@streamflix.com
- **Documentación**: [Wiki del Proyecto](https://github.com/tu-usuario/streamflix/wiki)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/streamflix/issues)

## 🎯 Roadmap

### Próximas Características
- [ ] Sistema de comentarios y reseñas
- [ ] Lista de favoritos personalizada
- [ ] Notificaciones push
- [ ] API móvil completa
- [ ] Sistema de suscripciones
- [ ] Análiticas avanzadas
- [ ] Soporte para subtítulos
- [ ] Streaming adaptativo

---

**Desarrollado con ❤️ para la comunidad de streaming** 