import logging
import multiprocessing
import sys
from dataclasses import dataclass
from io import StringIO
from multiprocessing import Process
from multiprocessing.shared_memory import SharedMemory
from pathlib import Path
import time
from typing import Any, IO
from contextlib import redirect_stdout
from concurrent.futures import Future, ThreadPoolExecutor
import numpy as np



class Executor(Process):
    def __init__(self):
        super().__init__(name="Executor", daemon=True)
        self.script_queue = multiprocessing.Queue()
        self.result_queue = multiprocessing.Queue()
        self.pool = ThreadPoolExecutor()
        self.shm = SharedMemory(create=True, size=1024)
        self.futures = np.ndarray([], dtype=Future, buffer=self.shm.buf)
    
    def execute_script(self, script_path: Path, input_data: dict[str, Any]):
        self.script_queue.put((script_path.resolve(), input_data))
        while len(self.futures) == 0:
            pass
        res = self.futures[-1]
        np.delete(self.futures, -1)
        return res.result()
    
    def func(self, input_data):
        input_data = int(input_data)
        for i in range(10**8):
            input_data += i
        return input_data

    
    def run(self) -> None:
        while True:
            path, input_data = self.script_queue.get()
            try:
                with self.pool as executor:
                    np.append(self.futures ,executor.submit(self.func, input_data))
            except Exception as e:
                print(e)


def main() -> None:
    exec_process = Executor()
    exec_process.start()
    script_path = Path('./generate_smth.py')
    input_data = "150"
    print(exec_process.execute_script(script_path, input_data=input_data))


if __name__ == '__main__':
    main()
