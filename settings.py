from urlparse import urljoin
import os

# MUST BE CHANGED IN ORDER FOR THE PI TO WORK
# This Pi's unique device id
UNIQUE_DEVICE_ID = "abcdefghijklmnopqrstuvwxyz1234567890"

# Server that serves playlist information
SERVER_URL = "https://ikkuna.seepra.fi"

# SETTINGS
# Defaults should work. Change with care

# Should requests to https servers be verified?
# True / False / absolute_path_to_a_crt_file_that_should_used
# NOTE: if crt file is not found defaults to True
# False should only be used in development environment! Not for production. Security risk.
SERVER_VERIFY = "/etc/ssl/certs/ca-certificates.crt"

# POLL TIME
# How long should the PI wait between playlist update checks. Default 60 seconds.
PLAYLIST_POLL_TIME = 60

# TIMEOUTS
# Can be set to None if connection should never timeout (not recommended)
# Bytes means how many seconds to wait for single byte to be downloaded before timing out
# Connection means how many seconds to wait for a connection to be established before timing out

# These timeouts apply to playlist json being downloaded from SERVER_URL
PLAYLIST_BYTES_TIMEOUT = 30
PLAYLIST_CONNECTION_TIMEOUT = 60

# These timeouts apply to status and confirmation messages being sent to SERVER_URL
STATUS_BYTES_TIMEOUT = 30
STATUS_CONNECTION_TIMEOUT = 60

# These timeouts apply to media being downloaded from urls specified in the playlist
MEDIA_DOWNLOAD_BYTES_TIMEOUT = 30
MEDIA_DOWNLOAD_CONNECTION_TIMEOUT = 60

# Media download chunk size.
# Increase for quicker downloads with a better connections, decrease for slow connections
MEDIA_DOWNLOAD_CHUNK_SIZE = 100000 # Bytes

# MEDIA CLEANER
# How many megabytes should be left free on the partition after a file has been downloaded.
CLEANUP_THRESHOLD_IN_MEGABYTES = 10
# How many megabytes should be cleared on top of the size of the file being downloaded when a cleanup is ran.
EXTRA_SPACE_TO_FREE_UP_IN_MEGABYTES = 100

# Local folders (defaults should be fine unless you are using the PI for something else as well)
# can be dynamic or absolute

# Where downloaded media should be stored
# NOTE!: Media folder should never contain anything else.
# Media cleaner removes files from this folder if the sd card gets full.
MEDIA_FOLDER = "media/"
# Where playlist file should be created
PLAYLIST_FILEPATH = "playlist/playlist.json"

# DO NOT CHANGE ANYTHING BELOW UNLESS SERVER API HAS CHANGED

# Path on the server where the playlist is located
PLAYLIST_SERVER_PATH = "/api/device/playlist"
# Path on the server where the status messages should be posted
STATUS_SERVER_PATH = "/api/device/status"

# json key of the url for the media host server
PLAYLIST_MEDIA_URL_STRING = "media_url"
# json key for the playlist id
PLAYLIST_ID_STRING = "id"
# json key for the playlist update time
PLAYLIST_UPDATE_TIME_STRING = "updated"
# json key of a playlist media schedule in json returned by the server
SCHEDULE_NAME_STRING = "media_schedule_json"

# json key of the time designated for a single playlist item in json returned by the server
SCHEDULE_TIME_STRING = "time"
# json key of the media type designated for a single playlist item in json returned by the server
SCHEDULE_TYPE_STRING = "media_type"
# json key of the url to media file designated for single playlist item in json returned by the server
SCHEDULE_URI_STRING = "url"

# Identifier that is put in Authorization header before the unique device id
AUTHORIZATION_TOKEN_IDENTIFIER = "Device"

"""
DO NOT EDIT AFTER THIS POINT
Below code initializes constants based on the settings above
"""

AUTHORIZATION_HEADER = AUTHORIZATION_TOKEN_IDENTIFIER + " " + UNIQUE_DEVICE_ID

if isinstance(SERVER_VERIFY, str):
    if not os.path.isfile(SERVER_VERIFY):
        SERVER_VERIFY = True

MEDIA_FOLDER = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        MEDIA_FOLDER)
if not os.path.exists(MEDIA_FOLDER):
    os.makedirs(MEDIA_FOLDER)

PLAYLIST_FILEPATH = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        PLAYLIST_FILEPATH)

playlist_folder = os.path.dirname(PLAYLIST_FILEPATH)
if not os.path.exists(playlist_folder):
    os.makedirs(playlist_folder)

PLAYLIST_URL = urljoin(SERVER_URL, PLAYLIST_SERVER_PATH)

STATUS_URL = urljoin(SERVER_URL, STATUS_SERVER_PATH)

PLAYLIST_TIMEOUTS = (PLAYLIST_BYTES_TIMEOUT, PLAYLIST_CONNECTION_TIMEOUT)

STATUS_TIMEOUTS = (STATUS_BYTES_TIMEOUT, STATUS_CONNECTION_TIMEOUT)

MEDIA_DOWNLOAD_TIMEOUTS = (MEDIA_DOWNLOAD_BYTES_TIMEOUT, MEDIA_DOWNLOAD_CONNECTION_TIMEOUT)

CLEANUP_THRESHOLD_BYTES = CLEANUP_THRESHOLD_IN_MEGABYTES * 1000 * 1000

EXTRA_SPACE_TO_FREE_UP_BYTES = EXTRA_SPACE_TO_FREE_UP_IN_MEGABYTES * 1000 * 1000

