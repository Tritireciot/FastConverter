from multiprocessing import Queue
from threading import Thread

from executor_service.storage import MessageStorage


class ResultListener(Thread):
    def __init__(self, storage: MessageStorage, result_queue: Queue) -> None:
        self.__storage = storage
        self.__result_queue = result_queue
        super().__init__(name="Result Listener Thread", daemon=True)

    def run(self) -> None:
        while True:
            self.__storage.set_result(self.__result_queue.get())

