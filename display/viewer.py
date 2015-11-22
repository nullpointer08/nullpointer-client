import time
from media import Media
from browser import Browser
from video_player import VideoPlayer
import logging


class Viewer(object):
    '''
    A high-level class for viewing any supported media type.
    Delegates viewing to the browser or video player depending on media
    type. The displaying is performed in a separate thread, so
    shutdown() must be called before killing the program to avoid
    errors upon program termination.
    '''

    DISPLAY_TIME_GRANULARITY = 1  # seconds
    BROWSER = Browser()
    PLAYER = VideoPlayer()

    VIEWERS = {
        Media.IMAGE: BROWSER,
        Media.WEB_PAGE: BROWSER,
        Media.VIDEO: PLAYER
    }

    def display_content(self, content):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Viewer received content %s', content)
        viewer = self.VIEWERS[content.content_type]

        displayed_time = 0
        viewer.display_content(content)
        self.running = True

        while self.running and displayed_time < content.view_time:
            time.sleep(self.DISPLAY_TIME_GRANULARITY)
            displayed_time += self.DISPLAY_TIME_GRANULARITY
            self.keep_alive(viewer, content)

        viewer.hide()
        self.logger.debug('Viewer finished displaying content %s', content)

    def keep_alive(self, viewer, content):
        if not viewer.is_alive():
            self.logger.debug('Resurrecting viewer for content %s', content)
            viewer.display_content(content)

    def shutdown(self):
        self.logger.debug('Viewer shutdown requested')
        self.running = False
        self.BROWSER.shutdown()
        self.PLAYER.shutdown()
        self.logger.debug('Viewer shutdown complete')
