# Asyncio Worker

Allows for the simple creation and management of longstanding asyncio workers.

## Installation
    
    pip install async_worker

## How to Use

    from async_worker import async_worker

    class ExampleClass(object):

        def __init__(self):
            self.count = 0

        @async_worker('add_worker')
        def adder(self):
            """
            Adds 1 to the count and then sleeps and does not sleep. Function
            is synchronous.
            """
            self.count += 1

and then when you're ready to start the worker.

    w = ExampleClass()
    w.start()

and when you're done or want the worker to stop.

    w.stop()
