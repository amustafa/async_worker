import pytest
import asyncio
from async_worker import async_worker, AsyncWorkerFunction, AsyncWorker


class ExampleAsyncClass(object):

    def __init__(self, sleep_time=0.01):
        self.count = 0
        self.sleep_time = sleep_time

    @async_worker('add_worker')
    async def adder(self):
        """
        Adds 1 to the count and then sleeps for for self.sleep_time.
        Function is asynchronous
        """
        self.count += 1


class ExampleSyncClass(object):

    def __init__(self, sleep_time=0.01):
        self.count = 0
        self.sleep_time = sleep_time

    @async_worker('add_worker')
    def adder(self):
        """
        Adds 1 to the count and then sleeps and does not sleep. Function
        is synchronous.
        """
        self.count += 1


@pytest.mark.asyncio
async def test_async_worker():
    assert isinstance(ExampleAsyncClass.adder, AsyncWorkerFunction)
    w = ExampleAsyncClass()
    assert isinstance(w.adder, AsyncWorker)
    assert w.count is 0

    w.add_worker.start()
    await asyncio.sleep(.01)

    assert w.count > 3
    assert w.add_worker.is_running

    w.add_worker.stop()
    count = w.count

    assert w.add_worker.is_running is False
    assert w.add_worker._task is None

    await asyncio.sleep(.01)
    assert w.count == count


@pytest.mark.asyncio
async def test_sync_worker():
    assert isinstance(ExampleSyncClass.adder, AsyncWorkerFunction)
    w = ExampleSyncClass()
    assert isinstance(w.adder, AsyncWorker)
    assert w.count is 0

    w.add_worker.start()
    await asyncio.sleep(.01)

    assert w.count > 3
    assert w.add_worker.is_running

    w.add_worker.stop()
    count = w.count

    assert w.add_worker.is_running is False
    assert w.add_worker._task is None

    await asyncio.sleep(.01)
    assert w.count == count
