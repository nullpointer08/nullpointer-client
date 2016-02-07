import logging.config
import os
from client.client import Client

START_PATH = os.path.dirname(os.path.realpath(__file__))

'''
A command line utility for starting the client.
'''


# LOGGING SETTINGS
LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'ERROR',
        },
        'client_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filename': os.path.join(START_PATH, 'client_debug.log'),
            'maxBytes': 1024*1024,  # 1MB
            'backupCount': 2,
            'encoding': 'utf8'
        },
        'display_debug': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'simple',
            'filename': os.path.join(START_PATH, 'display_debug.log'),
            'maxBytes': 1024*1024,  # 1MB
            'backupCount': 2,
            'encoding': 'utf8'
        },
        'errors': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'simple',
            'filename': os.path.join(START_PATH, 'error.log'),
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 2,
            'encoding': 'utf8'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'errors'],
            'level': 'ERROR',
        },
        'client': {
            'handlers': ['client_debug'],
            'level': 'DEBUG',
        },
        'display': {
            'handlers': ['display_debug'],
            'level': 'DEBUG',
        },

    },
}


def run():
    # Parse configuration to constants
    logging.config.dictConfig(LOGGING_CONFIG)
    client = Client()
    client.start()


if __name__ == '__main__':
    print 'Starting main'
    run()
