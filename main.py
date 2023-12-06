from pathlib import Path
from executor_service.executor import ExecutorService


def main():
    executor_service = ExecutorService()
    executor_service.execute_script(Path("generate_smth.py"), "150")
    print(executor_service.output_queue.get())

if __name__ == "__main__":
    main()