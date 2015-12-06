import requests
import time
import logging


class ChunkedDownloader(object):
    '''
    Downloads a file in chunks. If a chunk cannot be downloaded within a given
    timeout, the chunk download is cancelled and will be re-attempted.
    '''

    LOG = logging.getLogger(__name__)
    CHUNK_SIZE = 500000  # 500 Kb
    CHUNK_DOWNLOAD_TIMEOUT = 120  # Seconds
    RETRY_TIMEOUT = 10  # Seconds

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
        range_header = {
            'Range': 'bytes=%s-%s' % (range_begin, range_end)
        }
        self.LOG.debug('Downloading bytes %s' % range_header['Range'])
        response = requests.get(
            url,
            timeout=(None, 60),
            stream=True,
            headers=range_header
        )
        return response.content
