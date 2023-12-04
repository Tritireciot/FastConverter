import logging
import multiprocessing
import sys
from io import StringIO
from pathlib import Path
import time
from typing import Any, IO
from contextlib import redirect_stdout


class ScriptExecutor:
    def __init__(self, script_path: Path, result_queue: multiprocessing.Queue) -> None:
        self.logger = logging.getLogger(__name__)
        self.script_path = script_path
        self.stdin_hook = StringIO()
        self.prev_stdin_hook: IO | None = None
        self.stdout_hook = StringIO()
        self.prev_stdout_hook: IO | None = None
        self.stderr_hook = StringIO()
        self.prev_stderr_hook: IO | None = None
        self.source_code = ""
        self.result_queue = result_queue

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

    def execute_script(self, input_data: str):
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
                self.result_queue.put((self.script_path, result_data))
            except Exception as e:
                self.logger.error(e)
        except Exception as e:
            self.end()
            self.logger.error(e, extra={"script_path": self.script_path})


class ExecutorService:

    def __init__(self):
        self.__result_queue = multiprocessing.Queue()
        self.script_executor_class = ScriptExecutor
        self.executors: dict[Path, ScriptExecutor] = {}
    
    def execute_script(self, script_path: Path, input_data: dict[str, Any]):
        try:
            with self.executors.get(script_path, self.script_executor_class(script_path=script_path, result_queue=self.__result_queue)) as executor:
                executor.execute_script(input_data)
                if script_path not in self.executors:
                    self.executors[script_path] = executor
        except Exception as e:
            print(e)
    
    def get_script_result(self, script_path: Path):
        path, results = self.__result_queue.get()
        while script_path != path:
            self.__result_queue.put((path, results))
            path, results = self.__result_queue.get()
        return results

def main():
    
    logging.basicConfig(format="%(levelname)s:%(name)s:%(process)d - %(message)s")
    executor_service = ExecutorService()
    t = time.time()
    executor_service.execute_script(Path('./generate_smth.py'), "150")
    print(executor_service.get_script_result(Path('./generate_smth.py')))

if __name__ == '__main__':
    main()
