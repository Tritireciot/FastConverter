import ast
from pathlib import Path
from types import CodeType
from typing import Any

from executor_service.common.lazy_default_dict import LazyCodeCache
from executor_service.dto import CachedCodeType


class RemoveImportTransformer(ast.NodeTransformer):
    def __init__(self, imports: list[ast.Import | ast.ImportFrom], functions: dict[str, CodeType]):
        self.imports = imports
        self.functions = functions

    def visit_Import(self, node: ast.Import) -> Any:
        self.imports.append(node)
        return None

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Any:
        self.imports.append(node)
        return None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        self.functions[node.name] = compile(ast.unparse(node), '<inline>', 'exec')
        return self.generic_visit(node)


class ScriptCacher:
    def __init__(self) -> None:
        self.__script_storage: LazyCodeCache = LazyCodeCache(self.cache_script)

    def get_script_code(self, script_path: Path) -> CachedCodeType:
        return self.__script_storage[script_path]

    def cache_script(self, script_path: Path) -> CachedCodeType:
        with open(script_path.resolve()) as script:
            code_tree = ast.parse(script.read(), mode="exec")
        imports: list[ast.Import | ast.ImportFrom] = []
        functions: dict[str, CodeType] = {}
        RemoveImportTransformer(imports, functions).visit(code_tree)
        try:
            return CachedCodeType(
                code=compile(code_tree, script_path.absolute(), 'exec'),
                imports=imports, functions=functions)
        except Exception as e:  # TODO найти возможные ошибки
            pass
