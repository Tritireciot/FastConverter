import logging
import multiprocessing
import sys
from dataclasses import dataclass
from io import StringIO
from multiprocessing import Process
from pathlib import Path
import time
from typing import Any, IO
from contextlib import redirect_stdout


@dataclass(init=True, kw_only=True)
class ToExecute:
    path: Path
    input_data: str


@dataclass(kw_only=True)
class ExecuteResult:
    result: str
    success: bool


class ScriptExecutor:
    def __init__(self, script_path: Path) -> None:
        self.logger = logging.getLogger(__name__)
        self.script_path = script_path
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
            self.logger.error("Executing script, %s", input_data, extra={"script_path": self.script_path.resolve()})
            with redirect_stdout(self.stdout_hook):
                exec(self.source_code, {**globals(), "input": self.stdin_hook.getvalue, "__name__": "__main__"}, {})
            try:
                result_data = self.stdout_hook.getvalue()
                self.logger.error("Executing successful: %s", result_data)
                return ExecuteResult(result=result_data, success=False)
            except Exception as e:
                self.logger.error(e)
                result_data = self.stdout_hook.getvalue()
                self.logger.debug("Executing successful: %s", result_data)
                return ExecuteResult(result=result_data, success=True)

        except Exception as e:
            self.logger.error(e, extra={"script_path": self.script_path})


class ExecutorProcess(Process):
    def __init__(self, script_queue: multiprocessing.Queue,
                 result_queue: multiprocessing.Queue):
        super().__init__(name="Executor", daemon=True)
        self.script_executor_class = ScriptExecutor
        self.executors: dict[Path, ScriptExecutor] = {}
        self.script_queue = script_queue
        self.result_queue = result_queue

        self.logger = logging.getLogger(self.__class__.__name__)
    
    def execute_script(self, script_path: Path, input_data: dict[str, Any]) -> ExecuteResult:
        self.script_queue.put((script_path.resolve(), input_data))
        return self.result_queue.get()
    
    def run(self) -> None:
        while True:
            path, input_data = self.script_queue.get()
            try:
                with self.executors.get(path, self.script_executor_class(script_path=path)) as executor:
                    results = executor.execute_script(input_data)
                self.logger.error("EXECUTED %s", results)
                self.result_queue.put(results)
            except Exception as e:
                self.logger.error(e)


def main() -> None:
    logging.basicConfig(format="%(levelname)s:%(name)s:%(process)d - %(message)s")
    script_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()
    exec_process = ExecutorProcess(script_queue, result_queue)
    exec_process.start()

    script_path = Path('./generate_smth.py')
    #script_path2 = Path('./generate_smth_2.py')

    input_data = "150"

    #adapter = ExecutorAdapter(script_queue, result_queue)
    t = time.time()
    #print(exec_process.execute_script(script_path2, input_data=input_data))
    
    print(exec_process.execute_script(script_path, input_data=input_data))
    logging.error(time.time() - t)
    #logging.error(res)

    #logging.error(t1 / t2)


if __name__ == '__main__':
    main()
