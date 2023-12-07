from .dto import ExecuteResult
from .executor_task import ExecutorTask
from .cacher import ScriptCacher
from .messenger import ExecutorMessenger
from pathlib import Path
from typing import Any

class ExecutorService:
    
    def __init__(self):
        self.__messenger = ExecutorMessenger()
        self.__script_cacher = ScriptCacher()
        self.__executor_task = ExecutorTask()

    
    def execute_script(self, script_path: Path, input_data: Any) -> None: #TODO: конкретный тип
        code = self.__script_cacher.get_script_code(script_path)
        try:
            with self.__executor_task as task:
                result = task.execute_script(code, input_data)
                self.__messenger.put(ExecuteResult(script_path=script_path, result=result, success=True))
        except Exception as e: #TODO найти возможные ошибки
            self.__messenger.put(ExecuteResult(script_path=script_path, result=str(e), success=False))

        
