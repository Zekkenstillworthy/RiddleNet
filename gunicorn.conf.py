"""
Gunicorn Configuration for RiddleNet Flask-SocketIO Application
Optimized for AWS EC2 deployment with WebSocket support
"""
import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

# Worker processes
# For Flask-SocketIO with eventlet, use only 1 worker to maintain WebSocket connections
workers = 1
worker_class = "eventlet"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
preload_app = True

# Restart workers gracefully
max_worker_memory = int(os.getenv('MAX_WORKER_MEMORY', '200')) * 1024 * 1024  # 200MB default
restart_on_memory_usage = max_worker_memory

# Timeout settings
timeout = 120
keepalive = 5
graceful_timeout = 30

# SSL (if needed - configure these for HTTPS)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'riddlenet-gunicorn'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

# Environment variables
raw_env = [
    f'FLASK_ENV={os.getenv("FLASK_ENV", "production")}',
    f'DATABASE_URL={os.getenv("DATABASE_URL", "")}',
    f'SECRET_KEY={os.getenv("SECRET_KEY", "")}',
    f'AWS_REGION={os.getenv("AWS_REGION", "us-east-1")}',
    f'S3_BUCKET={os.getenv("S3_BUCKET", "")}',
]

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("RiddleNet Gunicorn server is ready. Listening on: %s", bind)

def worker_int(worker):
    """Called just after a worker exited on SIGINT or SIGQUIT."""
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized")

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker received SIGABRT signal")
