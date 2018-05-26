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
    """

    def __init__(self, work_fn):
        """

        :param worker_fn: function that does a single step of a long running
                            job.
        :type worker_fn: callable
        """
        if not asyncio.iscoroutinefunction(work_fn):
            self._work_fn = asyncio.coroutine(work_fn)
        else:
            self._work_fn = work_fn

        self._run = False
        self._task = None
        self._future = None

        self._start_event = asyncio.Event()
        self._stop_event = asyncio.Event()
        self._stop_event.set()

    @asyncio.coroutine
    def _worker(self):
        """
        Generic worker that will run the work function, yield control in the
        event loop, and then run the funtion again.

        If this task is cancelled, the cancellation is handled and the loop is
        stopped.
        """
        self._start_event.set()
        self._stop_event.clear()
        local_run = True
        try:
            while all([self._run, local_run]):
                yield from self._work_fn()
                yield
        except asyncio.CancelledError:
            # Task cancelled by user
            local_run = False
        finally:
            self._start_event.clear()
            self._stop_event.set()

    def start(self):
        if not self._run:
            self._run = True
            self._task = asyncio.ensure_future(self._worker())
            self._future = None

            def capture_future(future):
                self._future = future

            self._task.add_done_callback(capture_future)

    async def ensure_start(self):
        """
        Start method that can be awaited until the worker method gets a
        change to start running.
        """
        self.start()
        await self._start_event.wait()

    def stop(self):
        if hasattr(self, '_task') and self._task is not None:
            self._run = False
            self._task.cancel()
            self._task = None
            if self._future and self._future.exception() is not None:
                future = self._future
                self._future = None
                raise future.exception()

    async def ensure_stop(self):
        self.stop()
        await self._stop_event.wait()

    def __del__(self):
        self.stop()

    @property
    def is_running(self):
        return (self._run
                and self._task is not None)


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
                def worker_fn():
                    return self._worker_fn(obj)
                async_worker = AsyncWorker(worker_fn)
                setattr(obj, self._worker_name, async_worker)
            return getattr(obj, self._worker_name)

    def __set__(self, obj, value):
        raise AttributeError("Can't set attribute")

    def __call__(self, obj, *args, **kwargs):
        return self._worker_fn(obj, *args, **kwargs)


def async_worker(work_fn):
    """
    Decorator for creating AsyncWorkers

    :param work_fn: Method to create async worker from
    :type worker_fn_or_name: callable
    """
    if callable(work_fn):
        name = f'_{work_fn.__name__}_worker'
        return AsyncWorkerFunction(name, work_fn)
    else:
        raise ValueError('Must pass in callable')
