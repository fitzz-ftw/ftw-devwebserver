import asyncio
import threading


class BaseBroker:
    """
    Provides a base class for managing broker instances.

    :cvar int __instances: Total count of active broker instances.
    :ivar int _id: Unique identifier for the instance.
    """
    __instances = 0
    def __init__(self) -> None:
        """
        Initializes the base broker instance and increments the instance count.
        """
        self._id = self.__incr()

    def __delete__(self, instance) -> None:
        """
        Decrements the instance count upon deletion.

        :param instance: The instance to be deleted.
        """
        self.__decr()

    @classmethod
    
    def __incr(cls) -> int:
        """
        Increments the total number of broker instances.

        :returns: The new total count of instances.
        """
        cls.__instances += 1
        return cls.__instances
    
    @classmethod
    def __decr(cls) -> None:
        """
        Decrements the total number of broker instances.
        """
        cls.__instances -=1

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(Id: {self._id}/{self.__instances})"
        )

class QueueBroker(BaseBroker): # may be defect!
    """
    Manages signals using an asynchronous queue for communication between 
    threads and the event loop.

    :ivar int _id: Unique identifier for the instance.
    :ivar asyncio.Queue _queue: The queue used to buffer change signals.
    :ivar threading.Lock _wlock: Lock to ensure thread-safe queue access.
    """
    
    __instances = 0
    def __init__(self) -> None:
        """
        Initializes the queue broker and the associated thread lock.
        """
        self._id = self.__incr()
        self._queue = asyncio.Queue(maxsize=1)
        self._wlock= threading.Lock()

    def signal_change(self) -> None:
        """
        Signals a change event in a thread-safe manner.
        """
        if not self._queue.full():
            with self._wlock:
                self._queue.put_nowait(None)
        print("Changed",
              "Maxsize:", self._queue.maxsize,
              "Qsize:", self._queue.qsize(), 
            "Full:",self._queue.full(), 
            ", Empty:" ,self._queue.empty())
        

    async def wait_for_reload(self):# -> Any:
        """
        Waits for a reload signal to be placed in the queue.
        """
        print(
            "Unchanged",
            "Maxsize:",
            self._queue.maxsize,
            "Qsize:",
            self._queue.qsize(),
            "Full:",
            self._queue.full(),
            ", Empty:",
            self._queue.empty(),
        )
        data = await self._queue.get()
        print(
            "Changed",
            "Maxsize:",
            self._queue.maxsize,
            "Qsize:",
            self._queue.qsize(),
            "Full:",
            self._queue.full(),
            ", Empty:",
            self._queue.empty(),
        )
        return data

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(Id: {self._id}/{self.__instances}, "
            f"Queue: {self._queue.qsize()})"
        )


class ReloadBroker(BaseBroker):
    """
    Handles reload signals using threading events with an optional delay.

    :ivar threading.Event _event: The threading event used to signal a reload.
    :type _event: threading.Event
    """
    def __init__(self, timedelay:float=0.1) -> None:
        """
        Initializes the reload broker with a specified delay.

        :param timedelay: The delay in seconds before the reload signal is fully processed.
        """
        super().__init__()
        self._event = threading.Event()
        self.timedelay=timedelay
        

    def signal_change(self) -> None:
        """
        Triggers the reload signal event.
        """
        self._event.set()
        
    async def wait_for_reload(self) -> None:
        """
        Waits until a reload signal is set and applies the configured delay.
        """
        while not self._event.is_set():
            await asyncio.sleep(0.1)
        self._event.clear()
        await asyncio.sleep(max(self.timedelay,0.01))
