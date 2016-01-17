import requests
import time
from urlparse import urljoin
import datetime
import logging


class StatusMonitor(object):
    """
    Collects status information and submits it as a batch to the server
    """

    LOG = logging.getLogger(__name__)

    class EventTypes:
        ERROR = 0
        SUCCESS = 1

    class Categories:
        CONNECTION = 'Connection'
        OMITTED_STATUSES = 'Omitted'

    def __init__(self, config):
        server_url = config.get('Server', 'server_url')
        playlist_server_path = config.get('Server', 'playlist_server_path')
        status_server_path = config.get('Server', 'status_server_path')
        self.status_url = urljoin(server_url, status_server_path)
        self.confirm_pl_url = urljoin(server_url, playlist_server_path)
        # Device ID
        device_id_file = open(config.get('Device', 'device_id_file'), 'r')
        device_id = device_id_file.read().strip()
        device_id_file.close()

        status_connection_timeout = int(config.get('Client', 'status_connection_timeout'))
        if status_connection_timeout == 0:
            status_connection_timeout = None
        status_bytes_timeout = int(config.get('Client', 'status_bytes_timeout'))
        if status_bytes_timeout == 0:
            status_bytes_timeout = None
        self.timeouts = (status_bytes_timeout, status_connection_timeout)

        self.status_list = []
        self.headers = {'Authorization':'Device {0}'.format(device_id)}

    def submit_collected_events(self):
        if len(self.status_list) == 0:
            return None
        if len(self.status_list) > 50:
            del self.status_list[4:-10]
            self.add_status(StatusMonitor.EventTypes.ERROR,
                            StatusMonitor.Categories.OMITTED_STATUSES,
                            'Too many status msgs collected. Purged all but 4 oldest and 10 newest')

        self.LOG.debug("Submitting collected events. Last: %s", self.status_list[-1])
        data = self.status_list
        try:
            response = requests.post(
                self.status_url,
                json=data,
                headers=self.headers,
                timeout=self.timeouts
            )
            if response.status_code == 201:
                self.status_list = []
        except Exception as e:
            self.LOG.error('Could not submit collected events', e)

    def add_status(self, event_type, event_category, event_description, event_time=None):
        if len(event_category) > 20:
            self.LOG.warn('Too long event category while adding status.')
            event_category = event_category[:20]
        if len(event_description) > 128:
            self.LOG.warn('Too long event description while adding status.')
            event_description = event_description[:128]
        if event_time is None:
            event_time = time.time()
            self.LOG.debug('event time was None')

        event_time = datetime.datetime.fromtimestamp(
            int(event_time)
        ).strftime('%Y-%m-%d %H:%M:%S')
        self.LOG.debug('Creating status obj')
        status_obj = {
            'type': event_type,
            'category': event_category,
            'time': event_time,
            'description': event_description
        }
        self.LOG.debug('Appending status')
        self.status_list.append(status_obj)

    def confirm_new_playlist(self, playlist_id):
        if playlist_id is None:
            return
        data = {
            'confirmed_playlist': playlist_id
        }
        response = requests.put(
            self.confirm_pl_url,
            json=data,
            headers=self.headers,
            timeout=self.timeouts
        )
        if response.status_code != 200:
            self.add_status(
                StatusMonitor.EventTypes.ERROR,
                'StatusMonitor',
                'Could not confirm playlist use'
            )
        return response
'''
if __name__ == '__main__':
    status = StatusMonitor('http://192.168.1.60:8000/api/status', '98efa39bd87bf3c7084e07f55c26c577')
    status.add_status(
        StatusMonitor.EventTypes.SUCCESS,
        'Test',
        'Sending test status'
    )
    response = status.submit_collected()
    print response.content
'''