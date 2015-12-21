import requests
import logging
import os
from urlparse import urlparse
import re
import unicodedata
from hashlib import md5 as md5sum


class ResumableFileDownload(object):
    """
    Handles file operations on downloads.
    """
    MD5_STRING = "md5"
    LOG = logging.getLogger(__name__)

    def __init__(self, url, media_folder, filename, expected_md5, expected_size):
        self.url = url
        if expected_md5:
            filename = self.MD5_STRING + str(expected_md5) + filename

        self.complete_filepath = os.path.join(media_folder, filename)
        self.incomplete_filepath = self.complete_filepath + '.incomplete'
        self.expected_md5 = expected_md5
        self.expected_size = expected_size

    def is_complete(self):
        return os.path.isfile(self.complete_filepath)

    def stream_to_file(self, iter_function):
        with open(self.incomplete_filepath, 'ab') as f:
            for chunk in iter_function(chunk_size=1024):
                if chunk:
                    f.write(chunk)

    def download_complete(self):
        if os.path.isfile(self.incomplete_filepath):
            self.LOG.debug("is a file")
            with open(self.incomplete_filepath) as f:
                file_md5 = md5sum(f.read()).hexdigest()
            self.LOG.debug("md5: %s", file_md5)
            self.LOG.debug("comparing to md5: %s", self.expected_md5)
            if not self.expected_md5:
                os.rename(self.incomplete_filepath, self.complete_filepath)
                return
            elif file_md5 == self.expected_md5:
                os.rename(self.incomplete_filepath, self.complete_filepath)
                return
        raise Exception("Error completing download.")

    def bytes_downloaded(self):
        if os.path.isfile(self.incomplete_filepath):
            return os.path.getsize(self.incomplete_filepath)
        return 0


class ChunkedDownloader(object):
    """
    Handles making requests, reading responses and feeds data to ResumableFileDownload object
    """

    LOG = logging.getLogger(__name__)

    def __init__(self, server_url, device_id, media_folder, media_cleaner):
        self.HISRA_NET_LOC = urlparse(server_url).netloc
        self.AUTHORIZATION_HEADER = 'Device %s' % device_id
        self.MEDIA_FOLDER = media_folder
        self.TIMEOUTS = (None, 60)
        self.MEDIA_CLEANER = media_cleaner

    def download(self, content):

        url = content.content_uri
        headers = {}
        if urlparse(url).netloc == self.HISRA_NET_LOC:
            headers['Authorization'] = self.AUTHORIZATION_HEADER

        response = requests.get(
            url,
            timeout=self.TIMEOUTS,
            stream=True,
            headers=headers
        )

        if response.status_code != 200:
            raise Exception("Expected 200 response got: %s", response.status_code)

        filename = self.get_filename(response, url)

        md5 = self.get_md5(response)

        content_length = response.headers['Content-Length']

        if content_length is None:
            raise("Response from {0} had no content-length. Download aborted.".format(url))

        self.MEDIA_CLEANER.clean_media(content_length)

        resumable_download = ResumableFileDownload(url, self.MEDIA_FOLDER, filename,
                                                   md5, content_length)

        if resumable_download.is_complete():
            response.close()
            return resumable_download.complete_filepath

        bytes_downloaded = resumable_download.bytes_downloaded()
        if bytes_downloaded > 0:
            response.close()
            self.LOG.debug('Resuming a download with range: {0}-{1}'
                           .format(bytes_downloaded, resumable_download.expected_size))

            headers['Range'] = 'bytes={0}-{1}'.format(bytes_downloaded, resumable_download.expected_size)
            response = requests.get(url=url,
                                    timeout=self.TIMEOUTS,
                                    stream=True,
                                    headers=headers)
            if response.status_code != 206:
                raise Exception("Requested a range(206) but got: %s", response.status_code)

        resumable_download.stream_to_file(response.iter_content)

        resumable_download.download_complete()

        return resumable_download.complete_filepath

    @staticmethod
    def get_filename(response, url):
        filename = re.findall("filename=(.+)", response.headers['Content-Disposition'])
        if filename and len(filename):
            return filename[0].strip()
        else:
            return ChunkedDownloader.slugify(url)

    @staticmethod
    def get_md5(response):
        if hasattr(response.headers, 'Content-MD5'):
            return response.headers['Content-MD5']
        return None

    @staticmethod
    def slugify(value):
        """
        Convert to ASCII. Convert spaces to hyphens.
        Remove characters that aren't alphanumerics, underscores, or hyphens.
        Convert to lowercase. Also strip leading and trailing whitespace.
        """
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub('[^\w\s-]', '', value).strip().lower()
        return re.sub('[-\s]+', '-', value)

    '''
    original slugify by:
    Copyright (c) Django Software Foundation and individual contributors.
    All rights reserved.

    Redistribution and use in source and binary forms, with or without modification,
    are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Django nor the names of its contributors may be used
       to endorse or promote products derived from this software without
       specific prior written permission.

    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
    ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
    WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
    DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
    ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
    LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
    ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
    SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    '''