import logging.config
import os
from optparse import OptionParser
import subprocess
import ConfigParser
from client.client import Client

START_PATH = os.path.dirname(os.path.realpath(__file__))
START_SHELL_SCRIPT_NAME = 'start.sh'
CONFIG_PATH = os.path.join(START_PATH, 'client/client.properties')

'''
A command line utility for starting the client.
Use the -f or --fullscreen switch to start in fullscreen borderless mode
using xinit (X cannot be on)
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


def run(fullscreen):
    if fullscreen:
        start_sh_path = START_PATH + '/' + START_SHELL_SCRIPT_NAME
        subprocess.Popen(['xinit', start_sh_path, '&'])
    else:
        config = ConfigParser.ConfigParser()
        with open(CONFIG_PATH) as config_fp:
            config.readfp(config_fp)
        logging.config.dictConfig(LOGGING_CONFIG)
        client = Client(config)
        client.start()


if __name__ == '__main__':
    print 'Starting main'

    parser = OptionParser()
    parser.add_option(
        '-f',
        '--fullscreen',
        action='store_true',
        dest='fullscreen',
        default=False,
        help='Starts the client in full screen borderless mode.'
    )
    (options, args) = parser.parse_args()
    run(options.fullscreen)
