from multiprocessing import cpu_count
bind = "0.0.0.0:8004"
# Worker Options
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'
# Logging Options
loglevel = 'debug'
accesslog = '/home/administrateur/web_src/diaspoAPIsecured/access_log'
errorlog = '/home/administrateur/web_src/diaspoAPIsecured/error_log'