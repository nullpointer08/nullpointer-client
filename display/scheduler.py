'''
Schedules the content in the playlist to be displayed.
The scheduling occurs in its own thread. To ensure thread safety, the 
play list should be modified using the modify_playlist_atomically() 
method.
'''

import time
import logging
from threading import Thread
from threading import Lock
from viewer import Viewer

class Scheduler(object):

    def __init__(self):
        logging.debug('Initializing scheduler')
        self.viewer = Viewer()
        self._playlist = []
        self._playlist_lock = Lock()

    def start(self):
        logging.debug('Starting scheduling')
        self.running = True

        def schedule_worker(scheduler):
            logging.debug('Scheduling thread started')
            index = 0
            while scheduler.running:
                lock = scheduler._playlist_lock
                lock.acquire()
                try:
                    playlist = scheduler._playlist
                    content_index = index % len(playlist)
                    content = playlist[content_index]
                finally:
                    lock.release()
                logging.debug('Scheduler began displaying %s', content)
                scheduler.viewer.display_content(content)
                index += 1
            scheduler.viewer.shutdown()
            logging.debug('Exiting scheduler worker thread')

        self.work_thread = Thread(target=schedule_worker, args=(self,))
        self.work_thread.start()

    def shutdown(self):
        logging.debug('Scheduler shutdown called')
        self.running = False
        self.viewer.shutdown()
        logging.debug('Scheduler waiting for worker thread to stop')
        self.work_thread.join()
        logging.debug('Scheduler shut down complete')
        
    def modify_playlist_atomically(self, modifier_function):
        logging.debug('Modifying scheduler playlist atomically')
        self._playlist_lock.acquire()
        try:
            modifier_function(self._playlist)
        finally:
            self._playlist_lock.release()
