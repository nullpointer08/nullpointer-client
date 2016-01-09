class Media(object):
    '''
    Represents an item to be displayed by the viewer. Consists
    of a media type, the URI to the content and the time the media should
    be displayed
    '''

    # Media types
    VIDEO = 'V'
    IMAGE = 'I'
    WEB_PAGE = 'W'
    VALID_TYPES = [VIDEO,IMAGE,WEB_PAGE]

    def __init__(self, content_type, content_uri, view_time):
        self.content_type = content_type
        self.content_uri = content_uri
        self.view_time = view_time

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (
            'ContentType=' + self.content_type +
            ',ContentUri=' + self.content_uri +
            ',ViewTime=' + str(self.view_time)
        )

    def __eq__(self, other):
        return \
            type(self) == type(other) and \
            self.content_type == other.content_type and \
            self.content_uri == other.content_uri and \
            self.view_time == other.view_time
