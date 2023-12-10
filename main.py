from pathlib import Path
from executor_service.executor import ExecutorService


def main():
    executor_service = ExecutorService()
    executor_service.start()
    executor_service.execute_script(Path("generate_smth.py"), "150")
    print(executor_service.get_result())
    executor_service.execute_script(Path("generate_smth_2.py"), "150")
    print(executor_service.get_result())

if __name__ == "__main__":
    main()