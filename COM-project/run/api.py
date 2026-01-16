from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict
from .errors import SyntaxErrorInfo

@dataclass(frozen=True)
class SyntaxResult:
    ok: bool
    error: Optional[SyntaxErrorInfo] = None

@dataclass(frozen=True)
class ExecResult:
    status: str  # "OK" | "SYNTAX_ERROR" | "TIMEOUT" | "DECODE_ERROR" | "RUNTIME_ERROR"
    output: Optional[int] = None
    steps: int = 0
    final_pc: Optional[int] = None
    registers: Optional[Dict[int, int]] = None
    error: Optional[str] = None

def check_syntax(program_text: str) -> SyntaxResult:
    from .syntax import check_syntax as _check_syntax
    return _check_syntax(program_text)

def run_text(program_text: str, input_value: int, max_steps: int = 100_000) -> ExecResult:
    from .executor import run_text as _run_text
    return _run_text(program_text, input_value, max_steps=max_steps)

def run_encoded(program_code: int, input_value: int, max_steps: int = 100_000) -> ExecResult:
    from .executor import run_encoded as _run_encoded
    return _run_encoded(program_code, input_value, max_steps=max_steps)
