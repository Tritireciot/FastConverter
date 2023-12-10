from collections import defaultdict
from pathlib import Path
from typing import Callable, TypeAlias

from executor_service.dto import CachedCodeType

DefaultFactory: TypeAlias = Callable[[Path], CachedCodeType]


class LazyCodeCache(defaultdict[Path, CachedCodeType]):
    default_factory: Callable[[Path], CachedCodeType] = None

    def __init__(self, default_factory: DefaultFactory):
        self.default_factory = default_factory
        super().__init__()

    def __missing__(self, key: Path):
        if self.default_factory is None: raise KeyError((key,))
        self[key] = value = self.default_factory(key)
        return value
