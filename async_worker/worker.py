"""
Worker

A worker is a ongoing async task.

async_worker:
    Decorator to be used in class definitions.

AsyncWorker:
    This class will provider a wrapper
        for a single function, giving the function a worker, start, and
        stop function.

AsyncWorkerFunction:
    Used in the class definition to return a new async worker for each new
        object.
"""
import asyncio


class AsyncWorker(object):

    """
    A decorator class that will wrap a function that acts as a single
    loop around a long standing function. Will also provide all the
    neccessary items for the worker to be managed. This is added to the
    object by the AsyncWorkerInit.
    """

    def __init__(self, work_fn, obj):
        """

        :param worker_fn: function that does a single step of a long running
                            job.
        :type worker_fn: callable
        """
        if not asyncio.iscoroutinefunction(work_fn):
            self._work_fn = asyncio.coroutine(work_fn)
        else:
            self._work_fn = work_fn

        self._is_running = False
        self._run = False
        self._task = None
        self._obj = obj

    @asyncio.coroutine
    def _worker(self):
        """
        Generic worker that will run the work function, yield control in the
        event loop, and then run the funtion again.

        If this task is cancelled, the cancellation is handled and the loop is
        stopped.
        """
        local_run = True
        while all([self._run, local_run]):
            try:
                yield from self._work_fn(self._obj)
                yield
            except asyncio.CancelledError:
                # Task cancelled by user
                local_run = False
                self.stop()

    def start(self):
        if not self._run:
            self._run = True
            self._task = asyncio.ensure_future(self._worker())

    def stop(self):
        if self._task is not None:
            self._run = False
            self._task.cancel()
            self._task = None

    @property
    def is_running(self):
        return self._run and self._task is not None

    def __del__(self):
        self.stop()


class AsyncWorkerFunction(object):

    """
    A decorator class that will wrap a function that acts as a single
    loop around a long standing function. Will also provide all the
    neccessary items for the worker to be managed.
    """

    def __init__(self, worker_name, worker_fn):
        self._worker_name = worker_name
        self._worker_fn = worker_fn

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        else:
            if not hasattr(obj, self._worker_name):
                async_worker = AsyncWorker(self._worker_fn, obj)
                setattr(obj, self._worker_name, async_worker)
            return getattr(obj, self._worker_name)

    def __set__(self, obj, value):
        raise AttributeError("Can't set attribute")


def async_worker(worker_fn_or_name):
    """
    Decorator for creating AsyncWorkers

    :param worker_fn_or_name: takes in a string or method. If method,
            this creates a AsyncWorkerFunction with the name of the
            method and '_worker' appended and the worker_fn being the method.
            If this is a string, this returns another decorator that sets
            the string as the name and the next function as the worker.
    :type worker_fn_or_name: str or callable
    """
    if callable(worker_fn_or_name):
        name = worker_fn_or_name.__name__
        worker_fn = worker_fn_or_name
        return AsyncWorkerFunction(name, worker_fn)
    else:
        name = worker_fn_or_name

        def set_worker_fn(worker_fn):
            return AsyncWorkerFunction(name, worker_fn)
        return set_worker_fn
