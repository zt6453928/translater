# Gunicorn configuration for PDF Translator
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 300  # 5分钟超时，足够MinerU处理
keepalive = 2

# Restart workers after this many requests, this can prevent memory leaks
max_requests = 1000
max_requests_jitter = 50

# Logging
loglevel = "info"
accesslog = "-"
errorlog = "-"

# Process naming
proc_name = "pdf_translator"

# Server mechanics
preload_app = True
pidfile = "/tmp/gunicorn.pid"
user = "nobody"
group = "nogroup"
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/ssl/private.key"
# certfile = "/path/to/ssl/certificate.crt"