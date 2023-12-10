import multiprocessing
import threading
from uuid import UUID

from pydantic import ValidationError

from .dto import ExecuteRequest, Stored, ExecuteFuture, ExecuteResult
from .exceptions import (
    RepositoryException,
    UnprocessableResponseException,
)
import adaptix


class MessageStorage:
    def __init__(self, script_queue: multiprocessing.Queue) -> None:
        self.__script_queue = script_queue
        self.__set_condition = threading.Condition()
        self.__storage: dict[UUID, Stored] = {}  # TODO: LRU Dict

        self.__retort = adaptix.Retort()

    def remove_message_callback(self, message_uuid: UUID):
        with self.__set_condition:
            # Prevent self-deleting from the dict
            self.__storage[message_uuid].future = None
            del self.__storage[message_uuid]

    def create(
            self,
            message: ExecuteRequest,
    ) -> ExecuteFuture:
        with self.__set_condition:
            message_future = ExecuteFuture()

            def done_callback(f: ExecuteFuture) -> None:
                if message.id is None:
                    return

                self.remove_message_callback(message.id)

            # TODO: Check on local example
            message_future.add_done_callback(done_callback)
            self.__storage[message.id] = Stored(
                message=message, future=message_future
            )
            self.__script_queue.put(message)
            self.__set_condition.notify()
            return message_future

    def set_result(self, message: ExecuteResult):
        stored = self.__storage[message.id]
        if stored.future is None:
            stored.future = ExecuteFuture()
            stored.future.set_exception(RepositoryException("Future was unset"))

        try:

            stored.future.set_result(message)
        except ValidationError:
            stored.future.set_exception(
                UnprocessableResponseException(
                    self.__retort.dump(message)
                )
            )
        except Exception as e:
            raise RepositoryException from e
