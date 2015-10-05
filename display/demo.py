from scheduler import Scheduler
from playlist import FileBasedPlayList

file_playlist = FileBasedPlayList('playlist.txt')
def add_playlist_to_scheduler(scheduler_playlist):
    for content in file_playlist:
        scheduler_playlist.append(content)

scheduler = Scheduler()
scheduler.modify_playlist_atomically(add_playlist_to_scheduler)
scheduler.start()

raw_input("Press enter to exit\n")
scheduler.shutdown()
