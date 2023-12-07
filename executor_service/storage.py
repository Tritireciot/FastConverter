import threading
from dataclasses import dataclass
from typing import Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel, ValidationError

from .dto import ZMQFuture, ZMQMessage
from .exceptions import (
    RepositoryException,
    UnprocessableResponseException,
)

TContent = TypeVar("TContent", bound=BaseModel)


@dataclass(eq=False, slots=True)
class Stored(Generic[TContent]):
    message: ZMQMessage
    future: ZMQFuture | None
    response_type: Type[TContent] | None
    destination: str


class ZMQMessageStorage:
    def __init__(self) -> None:
        self.__set_condition = threading.Condition()
        self.__storage: dict[UUID, Stored] = {}

    def remove_message_callback(self, message_uuid: UUID):
        with self.__set_condition:
            # Prevent self-deleting from the dict
            self.__storage[message_uuid].future = None
            del self.__storage[message_uuid]

    def get_fresh(self) -> tuple[str, ZMQMessage] | None:
        with self.__set_condition:
            self.__set_condition.wait()
            for message in self.__storage.values():
                if message.future is not None and (
                    not message.future.running() and not message.future.done()
                ):
                    return message.destination, message.message

        return None

    def create(
        self,
        message: ZMQMessage,
        response_type: Type[TContent] | None,
        destination: str,
    ) -> ZMQFuture:
        with self.__set_condition:
            message_future = ZMQFuture()

            def done_callback(f: ZMQFuture) -> None:
                if message.id is None:
                    return

                self.remove_message_callback(message.id)

            # TODO: Check on local example
            message_future.add_done_callback(done_callback)
            self.__storage[message.id] = Stored(
                message, message_future, response_type, destination
            )
            self.__set_condition.notify_all()
            return message_future

    def set_result(self, key: UUID, message: dict):
        stored = self.__storage[key]
        if stored.future is None:
            stored.future = ZMQFuture()
            stored.future.set_exception(RepositoryException("Future was unset"))

        if stored.response_type is None:
            stored.future.set_result(ZMQMessage[BaseModel].parse_obj(message))
            return

        try:
            stored.future.set_result(
                ZMQMessage[stored.response_type].parse_obj(message)  # type: ignore
            )
        except ValidationError:
            stored.future.set_exception(
                UnprocessableResponseException(
                    message, stored.response_type, stored.destination
                )
            )
        except Exception as e:
            raise RepositoryException from e
