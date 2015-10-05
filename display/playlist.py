from media import Media

class FileBasedPlayList(object):
    
    def __init__(self, filepath):
        self._playlist = []
        for line in open(filepath):
            split_line = line.split(',')
            self._playlist.append(Media(split_line[0], split_line[1], int(split_line[2])))
    
    def __iter__(self):
        return iter(self._playlist)

    def __str__(self):
        return str(self.__repr__())
    
    def __repr__(self):
        return repr(self._playlist)
