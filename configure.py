'''
Command line utility for setting the client properties.
'''

import os
import ConfigParser
import sys
import readline
import glob

CONFIG_ITEMS = (
    {
        'section': 'Storage',
        'item': 'media_folder',
        'description': 'Enter the folder where the media is downloaded to',
        'default': '/media/'
    },
    {
        'section': 'Storage',
        'item': 'playlist_file',
        'description': 'Enter the filename of the JSON playlist',
        'default': '/playlist/playlist.json'
    },
    {
        'section': 'Device',
        'item': 'device_id_file',
        'description': 'Enter the filepath to the device id file',
        'default': '/client/device_id.devid'
    }, 
    {
        'section': 'Client',
        'item': 'playlist_poll_time',
        'description': 'Enter how often a new playlist is fetched (seconds)',
        'default': '60'
    },
    {
        'section': 'Server',
        'item': 'playlist_url',
        'description': 'Enter the URL to fetch playlists from. (Not for end users)',
        'default': 'http://drajala.ddns.net:8000/api/device/{device_id}/playlist'
    },
    {
        'section': 'Logging',
        'item': 'client_log_file',
        'description': 'Enter the absolute filepath to the log file',
        'default': 'client.log'
    }
)

def complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def setup_autocomplete():
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete)


def configure():
    setup_autocomplete()
    
    config_path = './client/client.properties'
    config_file = open(config_path, 'rw')
    config = ConfigParser.ConfigParser()
    config.readfp(config_file)
    
    done_count = 1
    print '\nPress enter to use the default value or enter your own'
    for item in CONFIG_ITEMS:
        section = item['section']
        config_item = item['item']
        default_val = os.path.join(os.path.realpath(__file__), config.get(section, config_item))
        print '\n' + item['description']
        value = raw_input('%s/%s) Default [%s]> ' % (done_count, len(CONFIG_ITEMS), default_val)).strip()
        if len(value) == 0:
            value = default_val
        if not os.path.exists(value):
            os.makedirs(value)
        config.set(section, config_item, value)
        done_count += 1
    
    config_file.close()
    config_file = open(config_path, 'w')
    config.write(config_file)
    config_file.close()
    print '\nSaved config to %s' % os.path.abspath(config_path)

if __name__ == '__main__':
    configure()
