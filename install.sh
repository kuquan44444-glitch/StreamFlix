#!/bin/bash

# Script de instalación automatizada para StreamFlix
# Compatible con Ubuntu 20.04+ y Debian 10+

set -e  # Salir si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si se ejecuta como root
if [[ $EUID -eq 0 ]]; then
   print_error "Este script no debe ejecutarse como root"
   exit 1
fi

# Verificar sistema operativo
if ! command -v apt &> /dev/null; then
    print_error "Este script solo funciona en sistemas basados en Debian/Ubuntu"
    exit 1
fi

print_status "Iniciando instalación de StreamFlix..."

# Variables de configuración
APP_USER="streamflix"
APP_DIR="/home/$APP_USER/streamflix"
DOMAIN=""
EMAIL=""

# Solicitar información al usuario
read -p "Ingresa tu dominio (ej: ejemplo.com): " DOMAIN
read -p "Ingresa tu email para SSL (opcional): " EMAIL

# Actualizar sistema
print_status "Actualizando sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias del sistema
print_status "Instalando dependencias del sistema..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    nginx \
    supervisor \
    git \
    curl \
    wget \
    unzip \
    certbot \
    python3-certbot-nginx \
    ufw \
    fail2ban \
    htop \
    tree

# Crear usuario de aplicación
print_status "Creando usuario de aplicación..."
if ! id "$APP_USER" &>/dev/null; then
    sudo adduser --disabled-password --gecos "" $APP_USER
    sudo usermod -aG sudo $APP_USER
    print_success "Usuario $APP_USER creado"
else
    print_warning "Usuario $APP_USER ya existe"
fi

# Configurar firewall
print_status "Configurando firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw allow 80
sudo ufw allow 443

# Clonar repositorio
print_status "Clonando repositorio..."
sudo -u $APP_USER bash -c "
    cd /home/$APP_USER
    if [ ! -d 'streamflix' ]; then
        git clone https://github.com/tu-usuario/streamflix.git
    else
        cd streamflix
        git pull
    fi
"

# Configurar entorno virtual y dependencias
print_status "Configurando entorno virtual..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
"

# Configurar variables de entorno
print_status "Configurando variables de entorno..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    if [ ! -f .env ]; then
        cp .env .env.backup 2>/dev/null || true
        cat > .env << EOF
SECRET_KEY=$(openssl rand -hex 32)
DATABASE_URL=sqlite:///netflix_clone.db
FLASK_ENV=production
UPLOAD_FOLDER=app/static/uploads
MAX_CONTENT_LENGTH=104857600
ALLOWED_EXTENSIONS=mp4,avi,mov,wmv
IMAGE_EXTENSIONS=jpg,jpeg,png,webp
EOF
    fi
"

# Crear directorios necesarios
print_status "Creando directorios..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    mkdir -p app/static/uploads/videos
    mkdir -p app/static/uploads/thumbnails
    mkdir -p logs
"

# Inicializar base de datos
print_status "Inicializando base de datos..."
sudo -u $APP_USER bash -c "
    cd $APP_DIR
    source venv/bin/activate
    python -c 'from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()'
"

# Configurar Supervisor
print_status "Configurando Supervisor..."
sudo tee /etc/supervisor/conf.d/streamflix.conf > /dev/null << EOF
[program:streamflix]
command=$APP_DIR/venv/bin/gunicorn -c gunicorn.conf.py run:app
directory=$APP_DIR
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/streamflix.log
stderr_logfile=/var/log/streamflix_error.log
environment=PATH="$APP_DIR/venv/bin"
EOF

# Configurar Nginx
print_status "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/streamflix > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias $APP_DIR/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /uploads {
        alias $APP_DIR/app/static/uploads;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Activar sitio de Nginx
sudo ln -sf /etc/nginx/sites-available/streamflix /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Verificar configuración de Nginx
sudo nginx -t

# Configurar logs
print_status "Configurando logs..."
sudo touch /var/log/streamflix.log
sudo touch /var/log/streamflix_error.log
sudo chown $APP_USER:$APP_USER /var/log/streamflix*.log

# Configurar Fail2Ban
print_status "Configurando Fail2Ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true

[nginx-http-auth]
enabled = true

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/*error.log
findtime = 600
bantime = 7200
maxretry = 10
EOF

# Reiniciar servicios
print_status "Reiniciando servicios..."
sudo systemctl restart fail2ban
sudo systemctl restart nginx
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start streamflix

# Configurar SSL si se proporcionó email
if [ ! -z "$EMAIL" ] && [ ! -z "$DOMAIN" ]; then
    print_status "Configurando SSL con Let's Encrypt..."
    sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive --redirect
fi

# Configurar cron para renovación de SSL
print_status "Configurando renovación automática de SSL..."
(sudo crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -

# Configurar logrotate
print_status "Configurando rotación de logs..."
sudo tee /etc/logrotate.d/streamflix > /dev/null << EOF
/var/log/streamflix*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        supervisorctl restart streamflix
    endscript
}
EOF

# Configurar backup automático
print_status "Configurando backup automático..."
sudo -u $APP_USER bash -c "
    mkdir -p /home/$APP_USER/backups
    cat > /home/$APP_USER/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=\"/home/$APP_USER/backups\"
DATE=\$(date +%Y%m%d_%H%M%S)
cd $APP_DIR
tar -czf \"\$BACKUP_DIR/streamflix_backup_\$DATE.tar.gz\" \\
    --exclude='venv' \\
    --exclude='__pycache__' \\
    --exclude='*.pyc' \\
    --exclude='.git' \\
    .
# Mantener solo los últimos 7 backups
find \"\$BACKUP_DIR\" -name \"streamflix_backup_*.tar.gz\" -mtime +7 -delete
EOF
    chmod +x /home/$APP_USER/backup.sh
"

# Agregar backup al cron
(sudo -u $APP_USER crontab -l 2>/dev/null; echo "0 2 * * * /home/$APP_USER/backup.sh") | sudo -u $APP_USER crontab -

# Verificar estado de servicios
print_status "Verificando estado de servicios..."
sudo systemctl status nginx --no-pager -l
sudo supervisorctl status streamflix

# Mostrar información final
print_success "¡Instalación completada!"
echo ""
echo "=== INFORMACIÓN DE LA INSTALACIÓN ==="
echo "Aplicación: StreamFlix"
echo "Usuario: $APP_USER"
echo "Directorio: $APP_DIR"
echo "Dominio: $DOMAIN"
echo "URL: http://$DOMAIN"
if [ ! -z "$EMAIL" ]; then
    echo "SSL: Configurado con Let's Encrypt"
    echo "URL HTTPS: https://$DOMAIN"
fi
echo ""
echo "=== CREDENCIALES POR DEFECTO ==="
echo "Email: admin@netflix.com"
echo "Contraseña: admin123"
echo ""
print_warning "¡IMPORTANTE! Cambia las credenciales de administrador inmediatamente"
echo ""
echo "=== COMANDOS ÚTILES ==="
echo "Ver logs: sudo tail -f /var/log/streamflix.log"
echo "Reiniciar app: sudo supervisorctl restart streamflix"
echo "Estado de servicios: sudo supervisorctl status"
echo "Backup manual: sudo -u $APP_USER /home/$APP_USER/backup.sh"
echo ""
echo "=== PRÓXIMOS PASOS ==="
echo "1. Accede a tu sitio web"
echo "2. Inicia sesión como administrador"
echo "3. Cambia las credenciales por defecto"
echo "4. Configura las categorías y sube contenido"
echo "5. Personaliza los espacios publicitarios"
echo ""
print_success "¡StreamFlix está listo para usar!" 