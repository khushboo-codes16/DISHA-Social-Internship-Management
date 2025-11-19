# Gunicorn configuration file for production
import os
import multiprocessing

# Server socket (Render manages the port automatically)
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes (optimized for Render's free tier)
# Use 2 workers for free tier, can increase on paid tiers
workers = int(os.getenv('WORKERS', '2'))
worker_class = "sync"
worker_connections = 1000
timeout = 60  # Increased timeout for database operations
keepalive = 2

# Logging
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log to stderr
loglevel = "info"

# Process naming
proc_name = "disha_app"

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Performance tuning for Render
max_requests = 1000
max_requests_jitter = 50