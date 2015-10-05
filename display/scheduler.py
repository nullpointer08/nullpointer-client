'''
Schedules the content in the playlist to be displayed.
The scheduling occurs in its own thread. To ensure thread safety, the 
play list should be modified using the modify_playlist_atomically() 
method.
'''

import time
from threading import Thread
from threading import Lock
from viewer import Viewer

class Scheduler(object):

    def __init__(self):
        self.viewer = Viewer()
        self._playlist = []
        self._playlist_lock = Lock()

    def start(self):
        self.running = True

        def schedule_worker(scheduler):
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
                scheduler.viewer.display_content(content)
                index = index + 1

            scheduler.viewer.shutdown()

        self.work_thread = Thread(target=schedule_worker, args=(self,))
        self.work_thread.start()

    def shutdown(self):
        self.running = False
        self.viewer.shutdown()
        self.work_thread.join()
        
    def modify_playlist_atomically(self, modifier_function):
        self._playlist_lock.acquire()
        try:
            modifier_function(self._playlist)
        finally:
            self._playlist_lock.release()
