'''
A control class for the browser. Supports navigation to a web page and 
displaying images.
'''

import sh
import time
import os
import logging
from media import Media
logging.getLogger("sh").setLevel(logging.WARNING)

class Browser(object):

    def __init__(self):
        logging.debug('Initiation browser')
        self._event_flags = {}
        self._event_listeners = {}
        self.start()

    def display_content(self, media):
        assert media.content_type in (Media.WEB_PAGE, Media.IMAGE)
        logging.debug('Browser received content %s', media)
        if not self.is_alive():
            self.start()
        if media.content_type == Media.WEB_PAGE:
            self.navigate(media.content_uri)
        else:
            self.show_image(media.content_uri)

    # Instead of shutting down the browser, displays a blank document
    def hide(self):
        logging.debug('Hiding browser')
        self.command('js', 'document.open();')

    # Informs listeners of browser events
    def process_browser_events(self, line):
        event = str(line)
        for key in self._event_flags:
            if key in event:
                logging.debug('Setting event flag %s', key)
                self._event_flags[key] = True
        for key in self._event_listeners:
            if key in event:
                listener = self._event_listeners[key]
                if listener is not None:
                    logging.debug('Sending listeners of event %s', key)
                    listener()

    # Sleeps until a flag is set, used e.g. to wait for a page to load
    def wait_for_event(self, event):
        logging.debug('Browser waiting for event %s', event)
        while True:
            if event in self._event_flags and self._event_flags[event]:
                return
            time.sleep(0.25)

    def start(self):
        logging.debug('Starting browser process')
        self.process = sh.uzbl(
            print_events=True, 
            config='-', 
            verbose='', 
            _bg=True, 
            _out=self.process_browser_events
        )
        self.command('set', 'geometry=maximized')

    def shutdown(self):
        logging.debug('Shutting down browser')
        self.process.process.kill()

    def command(self, command_type, command=""):
        if self.is_alive():
            cmd_string = command_type + " " + command + "\n"
            logging.debug('Browser handling command %s', cmd_string)
            self.process.process.stdin.put(cmd_string)

    def navigate(self, address):
        logging.debug('Browser navigating to %s', address)
        self._event_flags['LOAD_FINISH'] = False
        self._event_listeners['LOAD_FINISH'] = None
        self.command('uri', address)

    def show_image(self, img_uri):
        logging.debug('Browser beginning to show image %s', img_uri)
        img_background = os.path.dirname(__file__) + '/image_base.html'
        img_background = os.path.abspath(img_background)
        self.navigate('file://' + img_background)
        self.wait_for_event('LOAD_FINISH')

        # Add a geometry change listener that rescales the image
        def load_img_command(): 
            self.command('js', 'loadImageFullScreen("' + img_uri + '")')
        self._event_listeners['GEOMETRY_CHANGED'] = load_img_command

        load_img_command()  # Loads the fullscreen image with JavaScript

    def is_alive(self):
        if self.process is None:
            return false
        else:
            return self.process.process.exit_code is None

