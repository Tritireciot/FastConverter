import multiprocessing
from pathlib import Path

from executor_service.executor import ExecutorService
from executor_service.messenger import ExecutorAdapterFactory
from executor_service.result_listener import ResultListener
from executor_service.storage import MessageStorage


def main():
    script_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    ExecutorService(script_queue=script_queue, result_queue=result_queue).start()

    storage = MessageStorage(script_queue=script_queue)
    ResultListener(storage=storage, result_queue=result_queue).start()

    factory = ExecutorAdapterFactory(storage=storage)

    adapter = factory.create_new()
    print(adapter.put(Path("./generate_smth.py"), {'jopa': 1231231}).result().result)


if __name__ == "__main__":
    main()
