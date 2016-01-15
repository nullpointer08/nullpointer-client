from Queue import Queue
from threading import Thread
import logging


class AsynchTask(object):
    '''
    A simple container for functions needed to run a task
    '''
    def __init__(self, work_func, on_success, on_error, params):
        self.work_func = work_func
        self.on_success = on_success
        self.on_error = on_error
        self.params = params


class AsynchExecutor(object):
    '''
    Executes tasks submitted to a FIFO queue using a daemon thread.
    Calls to submit() block until there is space in the queue.
    The daemon thread will block if the queue is empty.
    '''

    LOG = logging.getLogger(__name__)

    def __init__(self, queue_size=10):
        self.LOG.debug('Initializing AsynchExecutor')
        self.running = False
        self.task_queue = Queue(queue_size)  # FIFO queue

        def consume_task_queue(executor):
            while executor.is_running():
                task = executor.task_queue.get()
                self.LOG.debug('Running task %s' % task)
                if task == 'SHUTDOWN':
                    break
                try:
                    retval, retval2 = task.work_func(*task.params)
                    self.LOG.debug('AsynchTask finished with retval %s' % retval)
                    task.on_success(retval, retval2)
                except Exception as e:
                    task.on_error(e)
        self.work_thread = Thread(target=consume_task_queue, args=(self,))
        self.work_thread.daemon = True

    def start(self):
        ''' Starts the daemon thread '''
        self.running = True
        self.work_thread.start()
        self.LOG.debug('Started AsynchExecutor worker thread')

    def shutdown(self):
        ''' Stops the worker thread and joins with it '''
        self.LOG.debug('Stopping AsynchExecutor worker thread')
        self.running = False
        self.task_queue.put('SHUTDOWN')
        self.work_thread.join()
        self.LOG.debug('AsynchExecutor worker thread stopped')

    def is_running(self):
        return self.running

    def submit(self, work_func, **kwargs):
        '''
        Uses the functions passed as parameters to create and
        AsynchTask and places it in the task queue.
        This operation blocks if the task queue is full.
        '''
        def no_action(param):
            pass

        if 'on_success' not in kwargs:
            on_success = no_action
        else:
            on_success = kwargs['on_success']
        if 'on_error' not in kwargs:
            on_error = no_action
        else:
            on_error = kwargs['on_error']
        if 'params' not in kwargs:
            params = ()
        else:
            params = kwargs['params']

        task = AsynchTask(work_func, on_success, on_error, params)
        self.LOG.debug('Submitting new AsynchTask to FIFO queue...')
        self.task_queue.put(task)
        self.LOG.debug('AsynchTask accepted into FIFO queue')

    def is_full(self):
        '''
        If the task queue is full, calling submit() will block.
        Use this to check if submitting will block.
        '''
        return self.task_queue.full()
