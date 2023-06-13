# import multiprocessing
# from app.settings.logging import LOGGING_CONFIG

bind = "0.0.0.0:8080"
worker_class = 'uvicorn.workers.UvicornWorker'
# workers = multiprocessing.cpu_count() * 2 + 1
workers = 9
# threads = 2

timeout = 3600

# logconfig_dict = LOGGING_CONFIG
logleverl = 'debug'
# accesslog = '-'
# errorlog = '-'
