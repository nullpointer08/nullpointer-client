from threading import Thread
from threading import Lock
from viewer import Viewer
import logging


class Scheduler(object):
    '''
    Schedules the content in the playlist to be displayed.
    The scheduling occurs in its own thread. To ensure thread safety,
    the play list should be modified using the
    modify_playlist_atomically() method.
    '''

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing scheduler')
        self.viewer = Viewer()
        self._playlist = []
        self._playlist_lock = Lock()
        self.running = False

    def start(self):
        self.logger.debug('Starting scheduling')
        self.running = True

        def schedule_worker(scheduler):
            self.logger.debug('Scheduling thread started')
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
                self.logger.debug('Scheduler began displaying %s', content)
                scheduler.viewer.display_content(content)
                index += 1
            scheduler.viewer.shutdown()
            self.logger.debug('Exiting scheduler worker thread')

        self.work_thread = Thread(target=schedule_worker, args=(self,))
        self.work_thread.daemon = True
        self.work_thread.start()

    def shutdown(self):
        self.logger.debug('Scheduler shutdown called')
        self.running = False
        self.viewer.shutdown()
        self.logger.debug('Scheduler waiting for worker thread to stop')
        self.work_thread.join()
        self.logger.debug('Scheduler shut down complete')

    def modify_playlist_atomically(self, modifier_function):
        self.logger.debug('Modifying scheduler playlist atomically')
        self._playlist_lock.acquire()
        try:
            modifier_function(self._playlist)
            self.viewer.interrupt()
        finally:
            self._playlist_lock.release()
