from start_client import logger
from threading import Thread
from threading import Lock
from viewer import Viewer
'''
Schedules the content in the playlist to be displayed.
The scheduling occurs in its own thread. To ensure thread safety, the
play list should be modified using the modify_playlist_atomically()
method.
'''


class Scheduler(object):

    def __init__(self):
        logger.debug('Initializing scheduler')
        self.viewer = Viewer()
        self._playlist = []
        self._playlist_lock = Lock()
        self.running = False

    def start(self):
        logger.debug('Starting scheduling')
        self.running = True

        def schedule_worker(scheduler):
            logger.debug('Scheduling thread started')
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
                logger.debug('Scheduler began displaying %s', content)
                scheduler.viewer.display_content(content)
                index += 1
            scheduler.viewer.shutdown()
            logger.debug('Exiting scheduler worker thread')

        self.work_thread = Thread(target=schedule_worker, args=(self,))
        self.work_thread.start()

    def shutdown(self):
        logger.debug('Scheduler shutdown called')
        self.running = False
        self.viewer.shutdown()
        logger.debug('Scheduler waiting for worker thread to stop')
        self.work_thread.join()
        logger.debug('Scheduler shut down complete')

    def modify_playlist_atomically(self, modifier_function):
        logger.debug('Modifying scheduler playlist atomically')
        self._playlist_lock.acquire()
        try:
            modifier_function(self._playlist)
        finally:
            self._playlist_lock.release()
