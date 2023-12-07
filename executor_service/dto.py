from dataclasses import dataclass
from pathlib import Path
from typing import Generic, Type, TypeVar
from concurrent.futures import Future

from pydantic import BaseModel
from pydantic.generics import GenericModel

@dataclass(kw_only=True)
class ExecuteResult:
    script_path: Path
    result: str
    success: bool

TContent = TypeVar("TContent", bound=BaseModel)

class ZMQMessage(GenericModel, Generic[TContent]):
    script_path: Path
    content: TContent


ZMQFuture = Future[ZMQMessage[TContent]]

@dataclass(eq=False, slots=True)
class Stored(Generic[TContent]):
    message: ZMQMessage
    future: ZMQFuture | None
    response_type: Type[TContent] | None
