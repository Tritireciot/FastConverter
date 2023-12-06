from dataclasses import dataclass
from pathlib import Path

@dataclass(kw_only=True)
class ExecuteResult:
    script_path: Path
    result: str
    success: bool