import threading
from multiprocessing import Process, Queue

import anyio.from_thread
import anyio.to_thread

from .cacher import ScriptCacher
from .dto import ExecuteRequest, ExecuteResult
from .executor_task import ExecutorTask


class ExecutorService(Process):
    def __init__(self, script_queue: Queue, result_queue: Queue):
        super().__init__(name="Executor", daemon=True)
        self.script_queue = script_queue
        self.result_queue = result_queue
        self.executor_task = ExecutorTask

    def get_result(self):
        return self.result_queue.get()

    def execute(self, cacher: ScriptCacher, request: ExecuteRequest):
        code = cacher.get_script_code(request.script_path)
        try:
            return request.id, request.script_path, self.executor_task().execute_script(code, request.content), True
        except Exception as e:  # TODO найти возможные ошибки
            return request.id, request.script_path, str(e), False

    async def wait_for_tasks(self, stopped: threading.Event) -> None:
        cacher = ScriptCacher()

        def fetch_and_execute():
            req_id, script_path, result, success = self.execute(cacher, self.script_queue.get())
            self.result_queue.put(ExecuteResult(id=req_id, script_path=script_path, result=result, success=success))

        while not stopped.is_set():
            await anyio.to_thread.run_sync(fetch_and_execute)

    def run(self):
        async def __run():
            stopped = threading.Event()
            await self.wait_for_tasks(stopped)
            stopped.wait()

        anyio.run(__run)
