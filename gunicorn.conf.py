#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de Gunicorn para StreamFlix
Optimizado para VPS con 2 vCPU y 2.5GB RAM
"""

import multiprocessing
import os

# Configuración del servidor
bind = "127.0.0.1:8000"
backlog = 2048

# Configuración de workers
workers = multiprocessing.cpu_count() * 2 + 1  # Fórmula recomendada
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Configuración de memoria
max_worker_memory = 200  # MB por worker
preload_app = True

# Logging
accesslog = "/var/log/streamflix_access.log"
errorlog = "/var/log/streamflix_error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de proceso
user = "streamflix"
group = "streamflix"
tmp_upload_dir = None
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Configuración de desarrollo vs producción
if os.environ.get('FLASK_ENV') == 'development':
    reload = True
    workers = 1
    loglevel = "debug"
else:
    reload = False
    daemon = False

# Configuración de SSL (si se usa)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Hooks de aplicación
def when_ready(server):
    """Ejecutar cuando el servidor esté listo"""
    server.log.info("StreamFlix server is ready. Listening on: %s", server.address)

def worker_int(worker):
    """Ejecutar cuando un worker reciba SIGINT o SIGQUIT"""
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Ejecutar antes de hacer fork de un worker"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Ejecutar después de hacer fork de un worker"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    """Ejecutar cuando un worker reciba SIGABRT"""
    worker.log.info("worker received SIGABRT signal") 