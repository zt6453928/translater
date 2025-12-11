"""
Gunicorn configuration for production (Zeabur/Heroku-like).

- Increases request timeout to avoid worker being killed while
  parsing/translating/AI-fixing long PDFs.
-
Usage: gunicorn -c gunicorn.conf.py app:app
You can also set GUNICORN_CMD_ARGS="--config gunicorn.conf.py".
"""

import os

# Bind to the platform provided port or default 8000
bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"

# Worker model: threaded workers handle blocking I/O well
worker_class = os.environ.get('GUNICORN_WORKER_CLASS', 'gthread')

# Concurrency (be conservative for small containers)
workers = int(os.environ.get('GUNICORN_WORKERS', '1'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))

# Avoid 30s default timeout — long translation jobs need more time
timeout = int(os.environ.get('GUNICORN_TIMEOUT', '600'))
graceful_timeout = int(os.environ.get('GUNICORN_GRACEFUL_TIMEOUT', '600'))

# Keep the connection alive a bit longer for slow networks
keepalive = int(os.environ.get('GUNICORN_KEEPALIVE', '75'))

# Logging to stdout/stderr so platform collects logs
accesslog = '-'
errorlog = '-'
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')

