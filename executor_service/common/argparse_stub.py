from typing import Any


class ArgparserStub:
    def __init__(self, values: dict[str, str]):
        self.values = values

    def add_argument(self, *args, **kwargs) -> None:
        pass

    def parse_args(self) -> "ArgparserStub":
        return self

    def __getattribute__(self, key: str) -> Any:
        match key:
            case "add_argument" | "parse_args":
                return super().__getattribute__(key)
            case _:
                return super().__getattribute__("values")[key]


class ArgparseStub:
    def __init__(self, **kwargs: str):
        self.values = kwargs

    def ArgumentParser(self) -> ArgparserStub:
        return ArgparserStub(self.values)
