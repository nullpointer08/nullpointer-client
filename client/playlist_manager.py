import logging
import requests

from display.media import Media
from downloader import ChunkedDownloader
from media_cleaner import MediaCleaner
import playlist_utils
from settings import AUTHORIZATION_HEADER, PLAYLIST_TIMEOUTS, PLAYLIST_URL, SERVER_VERIFY


class PlaylistNotChanged(Exception):
    pass


class PlaylistManager(object):
    LOG = logging.getLogger(__name__)

    def __init__(self):

        media_cleaner = MediaCleaner()

        # Utility for downloading files
        self.downloader = ChunkedDownloader(media_cleaner)

        self.playlist_id = None
        self.playlist_update_time = None

    def fetch_local_playlist(self):
        try:
            local_playlist = playlist_utils.get_stored_playlist()
            # We do not download files here because it would defeat the purpose.
            # We trust the files have either been downloaded
            # or we start to download them the next time we download a playlist
            # this way if the playlist has changed we don't unnecessarily download old files
            return local_playlist
        except:
            self.LOG.info('No locally stored playlist')
            return []

    def fetch_remote_playlist_data(self):
        headers = {'Authorization': AUTHORIZATION_HEADER}
        self.LOG.debug('Fetching remote playlist from %s' % PLAYLIST_URL)
        response = requests.get(
                url=PLAYLIST_URL,
                timeout=PLAYLIST_TIMEOUTS,
                stream=False,
                headers=headers,
                verify=SERVER_VERIFY)

        if response.status_code == 200:
            self.LOG.debug('Fetched data: %s' % response.content)
            return response.content
        raise Exception('Wrong status from server while fetching playlist: %s' % response.status_code)

    def fetch_playlist(self):
        pl_data = self.fetch_remote_playlist_data()
        if pl_data is None:
            raise Exception("No playlist data received from server.")
        self.LOG.debug('Parsing playlist')
        media_url, playlist, playlist_id, playlist_update_time = playlist_utils.parse_playlist(pl_data)
        self.LOG.debug('Playlist with id %s and update time %s parsed', playlist_id, playlist_update_time)

        # check if the playlist is already in use by the device
        # Note that this is always false when we have just started the app
        # This is by design to make sure we have all the files
        if self.playlist_id == playlist_id and self.playlist_update_time == playlist_update_time:
            raise PlaylistNotChanged("Playlist data has not changed since last downloaded")

        self.download_playlist_files(playlist, media_url)

        playlist_utils.save_playlist_to_file(playlist)

        # save new playlist id and update time after we have finished all the tasks
        # that need to be performed when we download a playlist
        self.playlist_id = playlist_id
        self.playlist_update_time = playlist_update_time

        return playlist, playlist_id, playlist_update_time

    # NOTE: Also sets content_uri to local path to media file
    def download_playlist_files(self, playlist, own_server_media_url):
        self.downloader.set_hisra_net_loc(own_server_media_url)
        for content in playlist:
            if content.content_type == Media.WEB_PAGE:
                continue  # Web pages are not downloaded
            try:
                content.content_uri = self.downloader.download(content)
            except Exception, e:
                self.LOG.debug('Failed to download content, %s %s', content.content_uri, str(e))
                raise
