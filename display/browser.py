import time
import os
import sh
from media import Media
import logging

'''
A control class for the browser. Supports navigation to a web page and
displaying images.
'''


class Browser(object):

    # CONSTANTS
    STATIC_FILE_PATH = 'file://' + os.path.abspath(os.path.dirname(__file__))
    IMG_BG_HTML_FILE = 'image_base.html'
    IMG_BACKGROUND_HTML = os.path.join(STATIC_FILE_PATH, IMG_BG_HTML_FILE)

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.debug('Initializing browser')
        self._event_flags = {}
        self._event_listeners = {}
        self.start()

    def display_content(self, media):
        assert media.content_type in (Media.WEB_PAGE, Media.IMAGE)
        self.logger.debug('Browser received content %s', media)
        if not self.is_alive():
            self.start()
        if media.content_type == Media.WEB_PAGE:
            self.navigate(media.content_uri)
        else:
            self.show_image(media.content_uri)

    # Instead of shutting down the browser, displays a blank document
    def hide(self):
        self.logger.debug('Hiding browser')
        self.load_background()

    # Informs listeners of browser events
    def process_browser_events(self, line):
        event = str(line)
        for key in self._event_flags:
            if key in event:
                self.logger.debug('Setting event flag %s', key)
                self._event_flags[key] = True
        for key in self._event_listeners:
            if key in event:
                listener = self._event_listeners[key]
                if listener is not None:
                    self.logger.debug('Sending listeners of event %s', key)
                    listener()

    # Sleeps until a flag is set, used e.g. to wait for a page to load
    def wait_for_event(self, event):
        self.logger.debug('Browser waiting for event %s', event)
        while True:
            if event in self._event_flags and self._event_flags[event]:
                return
            time.sleep(0.1)

    def start(self):
        self.logger.debug('Starting browser process')
        self.process = sh.uzbl(
            config='-',
            _bg=True,
            _out=self.process_browser_events
        )
        self.command('set', 'verbose=0')
        self.command('set', 'geometry=maximized')
        self.command('set', 'print_events=1')
        self.command('set', 'show_status=0')
        self.logger.debug('Browser started. Loading background')
        self.logger.debug('Background file %s', Browser.IMG_BACKGROUND_HTML)
        self.load_background()

    def shutdown(self):
        self.logger.debug('Shutting down browser')
        self.process.process.kill()

    def command(self, command_type, command=""):
        if self.is_alive():
            cmd_string = command_type + " " + command + "\n"
            self.logger.debug('Browser handling command %s', cmd_string)
            self.process.process.stdin.put(cmd_string)

    def navigate(self, address):
        self.logger.debug('Browser navigating to %s', address)
        self._event_flags['LOAD_FINISH'] = False
        self._event_listeners['LOAD_FINISH'] = None
        self.command('uri', address)

    def load_background(self):
        self.navigate(Browser.IMG_BACKGROUND_HTML)

    def show_image(self, img_uri):
        self.wait_for_event('LOAD_FINISH')
        self.logger.debug('Browser beginning to show image %s', img_uri)
        # Add a geometry change listener that rescales the image
        def load_img_command():
            self.command('js', 'loadImageFullScreen("' + img_uri + '")')
            
        #self._event_listeners['GEOMETRY_CHANGED'] = load_img_command

        load_img_command()  # Loads the fullscreen image with JavaScript

    def is_alive(self):
        if self.process is None:
            return False
        else:
            return self.process.process.exit_code is None
