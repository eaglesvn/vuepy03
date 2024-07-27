# src/gunicorn/gunicorn_config.py ttsstt.py
import multiprocessing

# Bind the server to all IP addresses of the host.
bind = '0.0.0.0:5001'

# Use gevent for asynchronous workers
worker_class = 'gevent'

# Calculate the number of workers dynamically based on the number of CPU cores
# Formula: CPU cores * 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Number of threads for each worker
# With gevent, you might consider using a low thread count
threads = 1

# Timeout in seconds before a worker is killed and restarted
timeout = 120

# The maximum number of simultaneous clients
worker_connections = 1000

# How verbose the Gunicorn log files should be
loglevel = 'debug'

# Paths for access and error logs
errorlog = '/app1/src/gunicorn/error.log'
accesslog = '/app1/src/gunicorn/access.log'

# Custom format for the access logs
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'
