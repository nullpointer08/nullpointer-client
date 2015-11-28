from queue import Queue
from threading import Thread
import logging

class AsynchTask(object):
    '''
    A simple container for functions needed to run a task
    '''
    def __init__(self, work_func, params, success_func, error_func):
        self.work_func = work_func
        self.params = params
        self.success_func = success_func
        self.error_func = error_func


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
                if task == 'SHUTDOWN':
                    break
                try:
                    retval = task.work_func(*task.params)
                    task.success_func(retval)
                except Exception as e:
                    task.error_func(e)
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
        if 'success_func' not in kwargs:
            success_func = no_action
        else:
            success_func = kwargs['success_func']
        if 'error_func' not in kwargs:
            error_func = no_action
        else:
            error_func = kwargs['error_func']
        if 'params' not in kwargs:
            params = ()
        task = AsynchTask(work_func, success_func, error_func, params)
        self.LOG.debug('Submitting new AsynchTask to FIFO queue')
        self.task_queue.put(task)
        self.LOG.debug('AsynchTask accepted into FIFO queue')

    def is_full(self):
        '''
        If the task queue is full, calling submit() will block.
        Use this to check if submitting will block.
        '''
        return not self.task_queue.full()