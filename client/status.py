import requests
import time
import datetime
import logging

from settings import AUTHORIZATION_HEADER, SERVER_VERIFY, STATUS_URL, STATUS_TIMEOUTS, PLAYLIST_URL


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

    def __init__(self):
        self.status_list = []
        self.headers = {'Authorization': AUTHORIZATION_HEADER}

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
        self.LOG.debug('Headers: ', self.headers)
        try:
            response = requests.post(
                url=STATUS_URL,
                json=data,
                headers=self.headers,
                timeout=STATUS_TIMEOUTS,
                verify=SERVER_VERIFY
            )
            if response.status_code == 201:
                self.LOG.debug('Status list posted')
                self.status_list = []
        except Exception as e:
            self.LOG.error('Could not submit collected events.')

    def add_status(self, event_type, event_category, event_description, event_time=None):

        if len(event_category) > 20:
            self.LOG.warn('Too long event category while adding status.')
            event_category = event_category[:20]

        if len(event_description) > 128:
            self.LOG.warn('Too long event description while adding status.')
            event_description = event_description[:128]

        if not event_description:
            event_description = 'No event description'

        if event_time is None:
            event_time = time.time()
            self.LOG.debug('event time was None')

        event_time = datetime.datetime.fromtimestamp(int(event_time)).strftime('%Y-%m-%d %H:%M:%S')

        self.LOG.debug('Creating status obj')
        status_obj = {
            'type': event_type,
            'category': event_category,
            'time': event_time,
            'description': event_description
        }

        self.LOG.debug('Appending status')
        self.status_list.append(status_obj)

    def confirm_new_playlist(self, playlist_id, playlist_update_time):
        if playlist_id is None:
            return
        data = {
            'confirmed_playlist': playlist_id,
            'update_time': playlist_update_time
        }
        try:
            response = requests.put(
                url=PLAYLIST_URL,
                json=data,
                headers=self.headers,
                timeout=STATUS_TIMEOUTS,
                verify=SERVER_VERIFY
            )
            if response.status_code == 200:
                self.LOG.debug('Playlist confirmed to server.')
                return
            if response.status_code == 428:
                self.LOG.info('Server playlist was updated after download')
                return

            self.add_status(
                StatusMonitor.EventTypes.ERROR,
                'StatusMonitor',
                'Could not confirm playlist use status: {0}'.format(response.status_code)
            )
        except Exception as e:
            self.LOG.error('Could not confirm playlist use.')
