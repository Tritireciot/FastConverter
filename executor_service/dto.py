import ast
from concurrent.futures import Future
from dataclasses import dataclass, field
from pathlib import Path
from types import CodeType
from typing import Generic, TypeVar, Any
from uuid import UUID

from pydantic import BaseModel
from pydantic.generics import GenericModel


@dataclass(frozen=True, kw_only=True)
class CachedCodeType:
    code: str
    imports: list[ast.Import | ast.ImportFrom] = field(default_factory=list)
    functions: dict[str, CodeType] = field(default_factory=list)

@dataclass(kw_only=True)
class ExecuteResult:
    id: UUID
    script_path: Path
    result: str
    success: bool


@dataclass(kw_only=True)
class ExecuteRequest:
    id: UUID
    script_path: Path
    content: Any


ExecuteFuture = Future[ExecuteResult]


@dataclass(eq=False, slots=True, kw_only=True)
class Stored:
    message: ExecuteRequest
    future: ExecuteFuture | None
