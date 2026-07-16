#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuración de Gunicorn para StreamFlix
Adaptado para Render (Free Tier)
"""

import multiprocessing
import os

# Configuración del servidor
bind = "0.0.0.0:8000"  # Render yêu cầu bind tất cả các interface
backlog = 2048

# Configuración de workers - Giảm cho Free Tier
# workers = 1 (đủ cho free tier) hoặc tính theo CPU nhưng vừa phải
workers = 1  # Chỉ 1 worker để tiết kiệm memory
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100

# Timeouts
timeout = 30
keepalive = 2
graceful_timeout = 30

# Configuración de memoria - Giảm cho Free Tier
preload_app = False  # Tắt preload để tiết kiệm memory

# Logging - Log ra console để Render hiển thị
accesslog = "-"  # Log ra stdout
errorlog = "-"   # Log ra stderr
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Configuración de proceso - QUAN TRỌNG: Xóa user/group để chạy với user mặc định
# user = "streamflix"   # ĐÃ XÓA - User không tồn tại trên Render
# group = "streamflix"  # ĐÃ XÓA - Group không tồn tại trên Render
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

# Configuración de SSL (se deja comentado)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Hooks de aplicación (se mantienen)
def when_ready(server):
    server.log.info("StreamFlix server is ready. Listening on: %s", server.address)

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("worker received SIGABRT signal")
