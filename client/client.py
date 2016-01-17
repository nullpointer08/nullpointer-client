from asynch_executor import AsynchExecutor
import logging
import time
from playlist_manager import PlaylistManager
from display.scheduler import Scheduler
from media_cleaner import MediaCleaner
from status import StatusMonitor


class Client(object):

    LOG = logging.getLogger(__name__)

    def __init__(self, config):
        self.executor = AsynchExecutor(2)
        self.status_monitor = StatusMonitor(config)
        self.pl_manager = PlaylistManager(config)
        self.POLL_TIME = config.getfloat('Client', 'playlist_poll_time')
        self.scheduler = Scheduler()

    def schedule_playlist(self, playlist, playlist_id, playlist_update_time):
        self.LOG.debug('Client scheduling playlist %s' % playlist)
        if len(playlist) == 0:
            self.LOG.debug('No media to schedule')
            return

        def replace_playlist(scheduled_pl):
            del scheduled_pl[:]
            for media in playlist:
                scheduled_pl.append(media)
        self.scheduler.modify_playlist_atomically(replace_playlist)
        self.status_monitor.confirm_new_playlist(playlist_id, playlist_update_time)
        if not self.scheduler.running:
            self.scheduler.start()
        self.status_monitor.submit_collected_events()

    def start(self):
        # Get the first playlist from file. If there is no ready playlist,
        # this returns an empty playlist
        playlist = self.pl_manager.fetch_local_playlist()
        self.schedule_playlist(playlist, None)

        # Run by AsynchExecutor
        def get_new_playlist_and_free_up_space_if_necessary():
            return self.pl_manager.fetch_playlist()

        # Called by AsynchExecutor when there was an error
        def pl_fetch_error(error):
            self.LOG.error('Exception fetching playlist: {0}'.format(error.message))
            self.status_monitor.add_status(
                StatusMonitor.EventTypes.ERROR,
                StatusMonitor.Categories.CONNECTION,
                str(error.message)
            )
            self.LOG.debug('Creating status obj')
            self.status_monitor.submit_collected_events()

        self.executor.start()
        try:
            while True:
                if not self.executor.is_full():
                    self.executor.submit(
                        get_new_playlist_and_free_up_space_if_necessary,
                        on_success=self.schedule_playlist,
                        on_error=pl_fetch_error
                    )
                else:
                    self.LOG.debug('Executor task queue is full')
                time.sleep(self.POLL_TIME)
        except KeyboardInterrupt:
            self.executor.shutdown()
            if self.scheduler:
                self.scheduler.shutdown()
