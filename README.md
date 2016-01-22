NOTES/BUGS/IMPROVEMENTS:
There's a possibility to fill up the device by adding a playlist that has enough media to take up all the free space on the device.
After this, when you change to another playlist, media cleaner cannot free up space because all the media is in use.
In this situation the user should change to an empty playlist first and after that try the new playlist again. 
At this point media cleaner realizes the old files are not in use and can free up space.

Status messages are only stored in memory. Power loss causes unsent status messages to be lost. 

If the connection is lost between the last downloaded media file and sending the confirmation message(under 100ms apart), the confirmation is never sent. 
This does not occur often and the problem it causes it minimal, so a fix is left out of this version. 
Could be fixed by storing confirmation messages, like status messages and sending them the same way as well.

