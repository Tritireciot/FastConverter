import ast
import importlib
import json
import traceback
from io import StringIO
from typing import Any

from executor_service.common.argparse_stub import ArgparseStub
from executor_service.dto import CachedCodeType


class ExecutorTask:
    def __init__(self) -> None:
        self.stdin_hook = StringIO()
        self.stdout_hook = StringIO()

    def __print_stub(self, value: Any) -> None:
        self.stdout_hook.write(str(value))

    def execute_script(self, code: CachedCodeType, input_data: Any) -> str | None:  # TODO: конкретный тип
        try:
            if not isinstance(input_data, str):
                self.stdin_hook.write(json.dumps(input_data))
            else:
                self.stdin_hook.write(input_data)
            imports = {}
            for statement in code.imports:
                if isinstance(statement, ast.Import):
                    for name in statement.names:
                        imports[name.name] = importlib.import_module(name.name)
                if isinstance(statement, ast.ImportFrom):
                    module = importlib.import_module(statement.module)
                    imports.update({name.asname or name.name: getattr(module, name.name) for name in statement.names})
            exec(code.code, {**imports, "print": self.__print_stub,
                             "input": self.stdin_hook.getvalue,
                             "argparse": ArgparseStub(algorithm="Base"),
                             "__name__": "__main__", "hasattr": hasattr,
                             **code.functions})  # TODO: nu - ОЧЕНЬ ОПАСНО. builtins лучше перезаписать
            return self.stdout_hook.getvalue()
        except Exception:  # TODO найти возможные ошибки
            print(traceback.format_exc())
