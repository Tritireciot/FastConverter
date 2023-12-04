import multiprocessing
from multiprocessing import Process
from typing import Any, IO
from contextlib import redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from io import StringIO
import sys

@dataclass(init=True, kw_only=True)
class ToExecute:
    path: Path
    input_data: str


@dataclass(kw_only=True)
class ExecuteResult:
    result: str
    success: bool


class ScriptExecutor:
    def __init__(self, script_path: Path, result_queue: multiprocessing.Queue) -> None:
        self.script_path = script_path
        self.result_queue = result_queue
        self.stdin_hook = StringIO()
        self.prev_stdin_hook: IO | None = None
        self.stdout_hook = StringIO()
        self.prev_stdout_hook: IO | None = None
        self.stderr_hook = StringIO()
        self.prev_stderr_hook: IO | None = None
        self.source_code = ""

    def __enter__(self) -> "ScriptExecutor":
        sys.stdin.flush()
        sys.stdout.flush()
        sys.stderr.flush()

        self.prev_stdin_hook = sys.stdin
        sys.stdin = self.stdin_hook
        self.prev_stdout_hook = sys.stdout
        sys.stdout = self.stdout_hook
        self.prev_stderr_hook = sys.stderr
        sys.stderr = self.stderr_hook
        sys.displayhook = self.logger.error
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

    def execute_script(self, input_data: str) -> ExecuteResult:
        try:
            if not self.source_code:
                with open(self.script_path.resolve()) as file:
                    source_code = file.read()
                self.source_code = compile(source_code, '<inline>', 'exec')
            self.stdin_hook.write(input_data)
            with redirect_stdout(self.stdout_hook):
                exec(self.source_code, {**globals(), "input": self.stdin_hook.getvalue, "__name__": "__main__"}, {})
            try:
                result_data = self.stdout_hook.getvalue()
                self.result_queue.put(self.script_path, result_data)
            except Exception as e:
                pass

        except Exception as e:
            pass



class ExecutorProcess(Process):
    def __init__(self, script_queue: multiprocessing.Queue,
                 result_queue: multiprocessing.Queue):
        super().__init__(name="Executor", daemon=True)
        self.script_executor_class = ScriptExecutor
        self.executors: dict[Path, ScriptExecutor] = {}
        self.script_queue = script_queue
        self.result_queue = result_queue

    def run(self) -> None:
        while True:
            path, input_data = self.script_queue.get()
            try:
                with self.executors.get(path, self.script_executor_class(script_path=path, result_queue=self.result_queue)) as executor:
                    executor.execute_script(input_data)
                #self.logger.error("EXECUTED %s", results)
            except Exception as e:
                self.logger.error(e)


class ExecutorService:
    def __init__(self):
        self.__script_queue = multiprocessing.Queue()
        self.__result_queue = multiprocessing.Queue()
        self.__executor = ExecutorProcess(self.__script_queue, self.__result_queue)
        self.__executor.start()
    
    def execute_script(self, script_path: Path, input_data: dict[str, Any]) -> None:
        self.__script_queue.put((script_path.resolve(), input_data))
    
    def get_script_result(self, script_path: Path):
        path, result = self.__result_queue.get()
        while path != script_path:
            self.__result_queue.put((path, result))
            path, result = self.__result_queue.get()
        return result