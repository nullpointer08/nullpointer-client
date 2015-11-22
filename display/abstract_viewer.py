from abc import ABCMeta, abstractmethod


class AbstractViewer(object):
    '''
    An interface for viewing specific types of media.
    '''
    __metaclass__ = ABCMeta

    @abstractmethod
    def display_content(self, content):
        '''
        Makes the viewer display the given content
        :param content: An instance of Media to be displayed
        '''
        pass

    @abstractmethod
    def hide(self):
        '''
        Called after displaying a piece of content is finished. This should
        be called instead of shutdown if it is expected that the same viewer
        can be used again soon without restarting it.
        '''
        pass

    @abstractmethod
    def is_alive(self):
        '''
        Called to find out if the viewer, e.g. web browser, is alive and
        ready to accept content.
        :return: Whether the viewer is running and ready to accept content
        :rtype: Boolean
        '''
        pass

    @abstractmethod
    def shutdown(self):
        '''
        Shuts down the viewer and releases all its resources. For example,
        this could be used to kill the web browser process used to display
        web pages.
        '''
        pass
