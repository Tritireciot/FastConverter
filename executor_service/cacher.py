from pathlib import Path
from types import CodeType


class ScriptCacher:

    def __init__(self) -> None:
        self.__script_storage: dict[Path, CodeType] = {}
    
    def get_script_code(self, script_path: Path) -> CodeType:
        return self.__script_storage.get(script_path, self.__cache_script(script_path))
    
    def __cache_script(self, script_path: Path) -> CodeType:
        with open(script_path.resolve()) as script:
            code = script.read()
        try:
            compiled_code = compile(code, '<inline>', 'exec')
            self.__script_storage[script_path] = compiled_code
            return compiled_code
        except Exception as e: #TODO найти возможные ошибки
            pass
