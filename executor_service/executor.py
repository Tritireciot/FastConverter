from .dto import ExecuteResult
from .executor_task import ExecutorTask
from .cacher import ScriptCacher
from pathlib import Path
from typing import Any
from multiprocessing import Process, Queue

class ExecutorService(Process):
    
    def __init__(self):
        super().__init__(name="Executor", daemon=True)
        self.script_queue = Queue()
        self.result_queue = Queue()
        self.__script_cacher = ScriptCacher()
        self.__executor_task = ExecutorTask
    
    def execute_script(self, script_path: Path, input_data: Any) -> None: #TODO: конкретный тип
        if script_path.exists():
            self.script_queue.put((script_path, input_data))
    
    def get_result(self):
        return self.result_queue.get()
    
    def execution(self, script_path: Path, input_data: Any):
        code = self.__script_cacher.get_script_code(script_path)
        try:
            with self.__executor_task() as task:
                return task.execute_script(code, input_data)
        except Exception as e: #TODO найти возможные ошибки
            return str(e)

    def run(self):
        while True:
            script_path, input_data = self.script_queue.get()
            result = self.execution(script_path, input_data)
            self.result_queue.put(ExecuteResult(script_path=script_path, result=result, success=True))