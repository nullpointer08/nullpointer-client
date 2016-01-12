import requests
import time
import json
import datetime

class StatusMonitor(object):
    '''
    Collects status information and submits it as a batch to the server
    '''

    ERROR = 'error'
    SUCCESS = 'success'

    class Categories:
        CONNECTION = 'Connection'

    def __init__(self, status_url, confirm_pl_url, device_id):
        self.status_url = status_url
        self.confirm_pl_url = confirm_pl_url
        self.device_id = device_id
        self.status_list = []
        headers = {}
        headers['Authorization'] = 'Device %s' % device_id
        self.headers = headers

    def submit_collected_events(self):
        if len(self.status_list) == 0:
            return None
        print "Submitting collected events %s" % self.status_list
        data = self.status_list
        response = requests.post(
            self.status_url,
            json=data,
            headers=self.headers
        )
        if response.status_code == 200:
            self.status_list = []
        return response

    def add_status(self, event_type, event_category, event_description, event_time=-1):
        if len(event_type) > 20:
            raise ValueError('Max event category length is 20')
        if len(event_description) > 128:
            raise ValueError('Max. event description length is 128')
        if event_time == -1:
            event_time = time.time()
        event_time = datetime.datetime.fromtimestamp(
            int(event_time)
        ).strftime('%Y-%m-%d %H:%M:%S')
        status_obj = {
            'type': event_type,
            'category': event_category,
            'time': event_time,
            'description': event_description,
            'device_id': self.device_id
        }
        self.status_list.append(status_obj)

    def confirm_new_playlist(self, playlist_id):
        data = {
            'confirmed_playlist': playlist_id
        }
        response = requests.put(
            self.confirm_pl_url,
            json=data,
            headers=self.headers
        )
        if response.status_code != 200:
            self.add_status(
                StatusMonitor.ERROR,
                'StatusMonitor',
                'Could not confirm playlist use'
            )
        return response

if __name__ == '__main__':
    status = StatusMonitor('http://drajala.ddns.net:8000/api/status', 'dev1')
    status.add_status(
        StatusMonitor.SUCCESS,
        'Test',
        'Sending test status'
    )
    response = status.submit_collected()
    print response.content
