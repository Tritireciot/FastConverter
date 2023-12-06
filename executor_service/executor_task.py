from contextlib import redirect_stdout
from io import StringIO
import sys
from typing import IO, Any
from types import CodeType


class ExecutorTask:
    def __init__(self) -> None:
        self.stdin_hook = StringIO()
        self.prev_stdin_hook: IO | None = None
        self.stdout_hook = StringIO()
        self.prev_stdout_hook: IO | None = None
        self.stderr_hook = StringIO()
        self.prev_stderr_hook: IO | None = None

    def __enter__(self) -> "ExecutorTask":
        sys.stdin.flush()
        sys.stdout.flush()
        sys.stderr.flush()

        self.prev_stdin_hook = sys.stdin
        sys.stdin = self.stdin_hook
        self.prev_stdout_hook = sys.stdout
        sys.stdout = self.stdout_hook
        self.prev_stderr_hook = sys.stderr
        sys.stderr = self.stderr_hook
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.stdin_hook.flush()
        self.stdout_hook.flush()
        self.stderr_hook.flush()
        self.stdin_hook.close()
        self.stdout_hook.close()
        self.stderr_hook.close()

        sys.stdin = self.prev_stdin_hook
        sys.stdout = self.prev_stdout_hook
        sys.stderr = self.prev_stderr_hook

    def execute_script(self, code: CodeType, input_data: Any) -> str | None: #TODO: конкретный тип
        try:
            self.stdin_hook.write(input_data)
            with redirect_stdout(self.stdout_hook):
                exec(code, {**globals(), "input": self.stdin_hook.getvalue, "__name__": "__main__"}, {})
                return self.stdout_hook.getvalue()
        except Exception as e: #TODO найти возможные ошибки
            pass