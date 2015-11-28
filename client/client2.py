from asynch_executor import AsynchExecutor
import logging


class Client(object):

    LOG = logging.getLogger(__name__)

    def __init__(self, config):
        self.executor = AsynchExecutor(2)
        self.pl_manager = PlaylistManager(config)
        self.POLL_TIME = self.config.get('Client', 'playlist_poll_time')
        self.scheduler = Scheduler()

    def schedule_playlist(self, playlist):
        def replace_playlist(scheduled_pl):
            del scheduled_pl[:]
            for media in playlist:
                scheduled_pl.append(media)
        self.scheduler.modify_playlist_atomically(replace_playlist)
        if not self.scheduler.running:
            self.scheduler.start() 
        
    def start(self):
        # Get the first playlist from file
        playlist = self.pl_manager.fetch_playlist(local=True)
        self.schedule_playlist(playlist)
        
        # After this, start polling for new playlists asynchronously
        def pl_fetch_success(playlist):
            self.schedule_playlist(playlist)
        def pl_fetch_error(error):
            self.LOG.error("Error fetching playlist: %s" % e)
        try:
            while True:
                if not self.executor.is_full():
                    self.executor(
                        self.pl_manager.fetch_playlist, 
                        params=(False),
                        pl_fetch_success,
                        pl_fetch_error
                    )
                time.sleep(poll_time)
        except KeyboardInterrupt:
            if self.scheduler:
                self.scheduler.shutdown()
