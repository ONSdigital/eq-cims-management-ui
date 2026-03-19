"""Gunicorn configuration."""

import os

import gunicorn

workers = int(os.getenv("WEB_SERVER_WORKERS", "3"))
threads = int(os.getenv("WEB_SERVER_THREADS", "10"))
keepalive = int(os.getenv("HTTP_KEEP_ALIVE", "2"))
loglevel = os.getenv("LOG_LEVEL", "info")
ACCESSLOG = "-"
ERRORLOG = "-"
BIND = "0.0.0.0:5100"
gunicorn.SERVER_SOFTWARE = "None"
