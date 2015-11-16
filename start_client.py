'''
A command line utility for starting the client.
Use the -f or --fullscreen switch to start in fullscreen borderless mode
using xinit (X cannot be on)
'''

from optparse import OptionParser
import subprocess
import os
from client.client import Client

START_PATH = os.path.dirname(os.path.realpath(__file__))
START_SHELL_SCRIPT_NAME = 'start.sh'

def run(fullscreen):
    if fullscreen:
        start_sh_path = START_PATH + '/' + START_SHELL_SCRIPT_NAME
        subprocess.Popen(['xinit', start_sh_path, '&'])
    else:
        client = Client(START_PATH + '/client/client.properties')
        client.poll_playlist()

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
