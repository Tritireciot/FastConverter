from multiprocessing import Queue


class ExecutorMessenger:
    
    def __init__(self):
        self.__script_queue = Queue()
        self.__result_queue = Queue()
    
    def put(self, message):
        self.__result_queue.put(message)