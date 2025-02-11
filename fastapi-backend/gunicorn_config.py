import os

# Bind to the port defined in the $PORT environment variable if available, otherwise default to 8000
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"

# Worker processes - reduce number of workers to save memory
workers = 2  # Instead of cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Reduce memory usage
max_requests = 1000
max_requests_jitter = 50
worker_connections = 500  # Reduced from 1000

# Timeouts
timeout = 120
keepalive = 5

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "zap-recap"

# Memory management
worker_tmp_dir = "/tmp"  # Use disk instead of RAM (/dev/shm)
preload_app = True  # Enable preloading to benefit from copy-on-write, reducing memory usage

# Prevent memory leaks
max_requests_jitter = 50

# Resource limits - reduced to save memory
limit_request_line = 2048  # Reduced from 4094
limit_request_fields = 50  # Reduced from 100
limit_request_field_size = 4096  # Reduced from 8190


# Memory limits per worker (in MB)
# def when_ready(server):
#     # Set memory limit for workers
#     try:
#         import resource
#         # Increase memory limit per worker to 384MB. Adjust as needed.
#         memory_limit = 384 * 1024 * 1024
#         resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
#     except ImportError:
#         pass
