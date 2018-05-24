import pytest
import asyncio
from async_worker import async_worker, AsyncWorkerFunction, AsyncWorker


class ExampleDirectCode(object):

    def __init__(self):
        self.count = 0
        self.add_to_count_worker = AsyncWorker(self.add_to_count)

    def add_to_count(self):
        self.count += 1


class ExampleAsyncClass(object):

    def __init__(self, sleep_time=0.01):
        self.count = 0
        self.sleep_time = sleep_time

    @async_worker
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

    @async_worker
    def adder(self):
        """
        Adds 1 to the count and then sleeps and does not sleep. Function
        is synchronous.
        """
        self.count += 1


class ExampleErrorClass(object):

    def __init__(self, sleep_time=0.01):
        self.count = 0
        self.sleep_time = sleep_time

    @async_worker
    def divide_by_zero_adder(self):
        """
        Adds 1 to the count and then sleeps and does not sleep. Function
        is synchronous.
        """
        1/0


@pytest.mark.asyncio
async def test_direct_worker():
    w = ExampleDirectCode()
    assert w.count is 0

    w.add_to_count_worker.start()
    await asyncio.sleep(.01)

    assert w.count > 3
    assert w.add_to_count_worker.is_running

    w.add_to_count_worker.stop()
    count = w.count

    assert w.add_to_count_worker.is_running is False
    assert w.add_to_count_worker._task is None

    await asyncio.sleep(.01)
    assert w.count == count


@pytest.mark.asyncio
async def test_async_worker():
    assert isinstance(ExampleAsyncClass.adder, AsyncWorkerFunction)
    w = ExampleAsyncClass()
    assert isinstance(w.adder, AsyncWorker)
    assert w.count is 0

    w.adder.start()
    await asyncio.sleep(.01)

    assert w.count > 3
    assert w.adder.is_running

    w.adder.stop()
    count = w.count

    assert w.adder.is_running is False
    assert w.adder._task is None

    await asyncio.sleep(.01)
    assert w.count == count


@pytest.mark.asyncio
async def test_sync_worker():
    assert isinstance(ExampleSyncClass.adder, AsyncWorkerFunction)
    w = ExampleSyncClass()
    assert isinstance(w.adder, AsyncWorker)
    assert w.count is 0

    w.adder.start()
    await asyncio.sleep(.01)

    assert w.count > 3
    assert w.adder.is_running

    w.adder.stop()
    count = w.count

    assert w.adder.is_running is False
    assert w.adder._task is None

    await asyncio.sleep(.01)
    assert w.count == count


@pytest.mark.asyncio
async def test_error_in_work_fn():
    w = ExampleErrorClass()
    assert w.count is 0

    with pytest.raises(ZeroDivisionError):
        w.divide_by_zero_adder.start()

        await asyncio.sleep(0.01)
        w.divide_by_zero_adder.stop()
