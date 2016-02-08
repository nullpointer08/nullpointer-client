NOTES/BUGS/IMPROVEMENTS:
If PI client has started downloading files from a playlist it will not stop before all files have been downloaded, 
unless an exception is thrown(network connection lost for example) or power is lost. 
If a user changes the playlist on the server it will not take effect before the old playlist has been fully downloaded.

Media is not removed from the PI when user removes media from the server. Media is only removed from PI when the sd card becomes full.

Downloads are fsynced only when complete. If we would fsync after every chunk we would decrease performance but lose(and have to redownload) less data if a power outage happens.

Media folder should never contain anything else but downloaded media. Media cleaner removes old files from this folder when the sd card gets full.

There's a possibility to fill up the device by adding a playlist that has enough media to take up all the free space on the device.
After this, when you change to another playlist, media cleaner cannot free up space because all the media is in use.
In this situation the user should change to an empty playlist first and after that try the new playlist again. 
At this point media cleaner realizes the old files are not in use and can free up space.

Media cleaner does not check the whole playlist being downloaded before removing files. This can cause a file to be first deleted and then downloaded again in some rare cases. 
Better implementation for media downloader would probably be to
1. create ResumableFileDownloads(download headers from server) for all the media in playlist being downloaded
2. ask media cleaner to free up the complete amount of space needed and pass it all the files on the new playlist that should not be deleted
(2.5. throw exception if not possible)
3. download actual media


Status messages are only stored in memory. Power loss causes unsent status messages to be lost. 

If the connection is lost between the last downloaded media file and sending the confirmation message(under 100ms apart), the confirmation is never sent. 
This does not occur often and the problem it causes it minimal, so a fix is left out of this version. 
Could be fixed by storing confirmation messages, like status messages and sending them the same way as well.

