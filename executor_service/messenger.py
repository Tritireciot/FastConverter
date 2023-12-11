import uuid
from pathlib import Path
from typing import Any

from executor_service.dto import ExecuteRequest, ExecuteFuture, ExecuteResult
from executor_service.storage import MessageStorage


class ExecutorAdapter:

    def __init__(self, storage: MessageStorage):
        self.__storage = storage
        self.__execution_future: ExecuteFuture | None = None

    def put(self, script_path: Path, content: dict[str, Any]) -> "ExecutorAdapter":
        if self.__execution_future is not None:
            return self # TODO: raise Exception
        self.__execution_future = self.__storage.create(ExecuteRequest(id=uuid.uuid4(), script_path=script_path, content=content))
        return self

    def result(self) -> ExecuteResult:
        return self.__execution_future.result()


class ExecutorAdapterFactory:
    def __init__(self, storage: MessageStorage) -> None:
        self.storage = storage

    def create_new(self) -> ExecutorAdapter:
        return ExecutorAdapter(storage=self.storage)
