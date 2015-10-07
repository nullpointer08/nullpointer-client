import sys
import unittest
import time
from nullpointer.display.video_player import VideoPlayer
from nullpointer.display.media import Media

class VideoPlayerTest(unittest.TestCase):

    ''' Must be overriden for unnittest to work '''
    def runTest(self):
        pass

    ''' Tests whether displaying content starts the video player 
        and if the video player is shut down appropriately '''
    def test_display_and_shutdown(self):
        player = VideoPlayer()
        display_time = 2 # Seconds
        content = Media(
            Media.VIDEO, 
            'http://techslides.com/demos/sample-videos/small.mp4',
            display_time
        )
        player.display_content(content)
        self.assertTrue(player.is_alive())
        time.sleep(display_time + 0.5)
        player.shutdown()
        self.assertFalse(player.is_alive())

