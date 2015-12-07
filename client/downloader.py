import requests
import time
import logging
import base64
from urlparse import urlparse


class ChunkedDownloader(object):
    '''
    Downloads a file in chunks. If a chunk cannot be downloaded within a given
    timeout, the chunk download is cancelled and will be re-attempted.
    '''

    LOG = logging.getLogger(__name__)
    CHUNK_SIZE = 500000  # 500 Kb
    CHUNK_DOWNLOAD_TIMEOUT = 120  # Seconds
    RETRY_TIMEOUT = 10  # Seconds

    def __init__(self, server_url, device_id):
        self.HISRA_NET_LOC = urlparse(server_url).netloc
        self.AUTHORIZATION_HEADER = 'Device %s' % device_id

    def download(self, url, data_collector_func):
        '''
        The downloaded bytes are provided in chunks to the data_collector_func
        as a parameter when they become available.
        '''
        self.LOG.debug('Beginning to download content from %s' % url)
        bytes_fetched = 0
        while True:
            try:
                chunk = self.download_chunk(url, bytes_fetched)
                bytes_fetched += len(chunk)
                self.LOG.debug('Bytes in chunk: %s, total fetched: %s' % (len(chunk), bytes_fetched))
                data_collector_func(chunk)
                if len(chunk) != ChunkedDownloader.CHUNK_SIZE:
                    break
            except Exception, e:
                self.LOG.debug('Error downloading chunk from %s: %s. Retrying in %s seconds.' % (url, e, self.RETRY_TIMEOUT))
                time.sleep(ChunkedDownloader.RETRY_TIMEOUT)
        self.LOG.debug('Finished downloading %s: %s bytes' % (url, bytes_fetched))
        return bytes_fetched

    def download_chunk(self, url, range_begin):
        range_end = range_begin + ChunkedDownloader.CHUNK_SIZE - 1
        headers = {
            'Range': 'bytes=%s-%s' % (range_begin, range_end)
        }
        if urlparse(url).netloc == self.HISRA_NET_LOC:
            headers['Authorization'] = self.AUTHORIZATION_HEADER

        self.LOG.debug('Downloading bytes %s' % headers['Range'])
        response = requests.get(
            url,
            timeout=(None, 60),
            stream=True,
            headers=headers
        )
        return response.content
