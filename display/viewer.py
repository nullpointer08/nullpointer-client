'''
A high-level class for viewing any supported media type.
Delegates viewing to the browser or video player depending on media
type. The displaying is performed in a separate thread, so shutdown()
must be called before killing the program to avoid errors upon
program termination.
'''

import time
from media import Media
from browser import Browser
from video_player import VideoPlayer

class Viewer(object):
    
    DISPLAY_TIME_GRANULARITY = 1 # seconds
    BROWSER = Browser()
    PLAYER = VideoPlayer()
    
    VIEWERS = {
        Media.IMAGE: BROWSER,
        Media.WEB_PAGE: BROWSER,
        Media.VIDEO: PLAYER
    }
    
    def display_content(self, content):
        viewer = self.VIEWERS[content.content_type]
    
        displayed_time = 0
        viewer.display_content(content)
        self.running = True
        
        while self.running and displayed_time < content.view_time:
            time.sleep(self.DISPLAY_TIME_GRANULARITY)
            displayed_time += self.DISPLAY_TIME_GRANULARITY
            self.keep_alive(viewer, content)
        
        viewer.hide()
        
    def keep_alive(self, viewer, content):
        if not viewer.is_alive():
            viewer.display_content(content)
        
    def shutdown(self):
        print "Viewer shut down"
        self.running = False
        self.BROWSER.shutdown()
        self.PLAYER.shutdown()

