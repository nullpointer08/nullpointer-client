import requests
import time
import logging
import os
import shutil
from urlparse import urlparse


class ResumableFileDownload(object):
    '''
    A utility class which downloads the data from the given url to the
    given file path. In case the download is interrupted e.g. by
    a power failure, it will cotinue downloading from the last byte stored
    on disk.

    This works by dowloading data to a '.incomplete' file. When the download is
    finished, the '.incomplete' file is copied to a regular file with the
    '.incomplete' extension removed. If the download is interrupted, the
    missing portion of the file is downloaded based on the number of bytes
    the '.incomplete' file contains.
    '''

    def __init__(self, url, filepath, downloader):
        self.url = url
        self.filepath = filepath
        self.incomplete_filepath = filepath + '.incomplete'
        self.downloader = downloader

    def download(self):
        if self.is_incomplete():
            self.download_missing_bytes()
            shutil.copy2(self.incomplete_filepath, self.filepath)
            os.remove(self.incomplete_filepath)

    def is_incomplete(self):
        if not os.path.isfile(self.filepath):
            return True
        if os.path.isfile(self.incomplete_filepath):
            return True
        return False

    def download_missing_bytes(self):
        if not os.path.isfile(self.incomplete_filepath):
            fetched_bytes = 0
        else:
            fetched_bytes = os.path.getsize(self.incomplete_filepath)
        with open(self.incomplete_filepath, 'ab') as incomplete_file:
            self.downloader.download(
                self.url,
                incomplete_file.write,
                fetched_bytes
            )


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

    def download(self, url, data_collector_func, bytes_fetched=0):
        '''
        The downloaded bytes are provided in chunks to the data_collector_func
        as a parameter when they become available.
        '''
        self.LOG.debug('Beginning to download content from %s' % url)
        while True:
            try:
                chunk = self.download_chunk(url, bytes_fetched)
                bytes_fetched += len(chunk)
                self.LOG.debug('Bytes in chunk: %s, total fetched: %s' % (len(chunk), bytes_fetched))
                data_collector_func(chunk)
                if len(chunk) != ChunkedDownloader.CHUNK_SIZE:
                    break
            except Exception, e:
                print "Timed out when downloading chunk: %s" % e
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
            # timeout=(None, 60),
            stream=True,
            headers=headers
        )
        return response.content


if __name__ == '__main__':
    file_dl = ResumableFileDownload('http://www.sample-videos.com/video/mp4/720/big_buck_bunny_720p_2mb.mp4', 'vid.mp4')
    file_dl.download()
    print "Finished file download"
