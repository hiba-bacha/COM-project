from __future__ import annotations
from .api import SyntaxResult
from .parser_text import parse_program_text

def check_syntax(program_text: str) -> SyntaxResult:
    """
    Syntax checking only (no execution).
    Must report the line containing a syntax error (if any).
    """
    _, err = parse_program_text(program_text)
    if err is None:
        return SyntaxResult(ok=True, error=None)
    return SyntaxResult(ok=False, error=err)
