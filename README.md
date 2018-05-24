# Async Worker

Allows for the simple creation and management of longstanding asyncio workers.

## Installation
    
    pip install async_worker

## Design Details

The decorator wraps a single unit of work. This unit of work could be anything, such as pulling 
from a socket or reading from a file. This unit of work is passed to a "worker" that will call 
the function repeatedly until it is told to stop. The class handles starting and stoping the 
worker task.

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
