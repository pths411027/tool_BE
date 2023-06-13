import os

# from app.settings.config import LoggerSettings

root_path = os.path.abspath(os.curdir)
logs_path = os.path.join(root_path, 'app/logs')
if not os.path.exists(logs_path):
    os.makedirs(logs_path)

# LOGGER_SETTINGS = LoggerSettings()

LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "app.utils.logger.ColourizedFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - [%(process)s] - %(name)s(%(lineno)d): %(message)s",
            "use_colors": True,
        },
        "console": {
            "()": "app.utils.logger.ColourizedFormatter",
            "fmt": "%(levelprefix)s %(asctime)s: %(message)s",
            "use_colors": True,
        },
        "file_formatter": {
            "()": "app.utils.logger.ColourizedFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - [%(process)s] - %(name)s(%(lineno)d): %(message)s",
            "use_colors": False,
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "console": {
            "formatter": "console",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        # 'debug_file_handler': {  # even doesn't be used, error also raise if logs/ doesn't exist
        #     "formatter": "file_formatter",
        #     "class": "logging.handlers.RotatingFileHandler",
        #     "level": "DEBUG",
        #     "filename": f"{logs_path}/debug.log",
        #     "maxBytes": 5242880,
        #     "backupCount": 3,
        #     "encoding": "utf8"
        # },
        # 'logstash': {
        #     'level': LOGGER_SETTINGS.logstash_log_level,
        #     'class': 'logstash.TCPLogstashHandler',
        #     'host': LOGGER_SETTINGS.logstash_host,
        #     'port': LOGGER_SETTINGS.logstash_port,  # Default value: 5000
        #     'version': 1,
        #     'message_type': 'logstash',  # 'type' field in logstash message. Default value: 'logstash'.
        #     'fqdn': False,  # Fully qualified domain name. Default value: false.
        #     'tags': ['fastapi', 'bi_portal', LOGGER_SETTINGS.app_tag],  # list of tags. Default: None.
        # },
    },
    "loggers": {
        "app": {
            "handlers": [
                "console",
                # "debug_file_handler",
                # "logstash",
            ],
            "level": "DEBUG",
            "propagate": False
        },
        # "app.error": {
        #     "handlers": ["console"],
        #     "level": "INFO",
        #     "propagate": False
        # },
        # "gunicorn": {
        #     "handlers": ["console"],
        #     "level": "INFO",
        #     "propagate": True
        # },
        "uvicorn": {
            "handlers": [
                "console",
                # "logstash",
            ],
            "level": "INFO",
            "propagate": True
        },
    },
}
