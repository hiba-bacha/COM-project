from __future__ import annotations
import re
from typing import List, Tuple, Optional

from .instructions import Instruction, Inc, Dec, GotoF, GotoB
from .errors import SyntaxErrorInfo

_RE_REG = re.compile(r"^R(\d+)$")

def _normalize(s: str) -> str:
    """
    Normalize unicode variants often copied from PDFs:
    - '−' becomes '-'
    - '·' removed so '-·' becomes '-'
    """
    return s.replace("−", "-").replace("·", "").strip()

def _parse_reg(token: str) -> int:
    m = _RE_REG.match(token)
    if not m:
        raise ValueError(f"Register expected like R0, R1... got '{token}'")
    return int(m.group(1))

def parse_program_text(program_text: str) -> Tuple[List[Instruction], Optional[SyntaxErrorInfo]]:
    """
    Parse the whole program.
    Returns: (instructions, error_or_None)
    Line numbers start at 1.
    """
    instrs: List[Instruction] = []
    lines = program_text.splitlines()

    for lineno, raw in enumerate(lines, start=1):
        line = _normalize(raw)

        # allow empty lines and pure comments
        if not line or line.startswith("#"):
            continue

        # allow inline comments
        if "#" in line:
            line = _normalize(line.split("#", 1)[0])
            if not line:
                continue

        try:
            instrs.append(_parse_line(line))
        except Exception as e:
            return [], SyntaxErrorInfo(
                line=lineno,
                message=str(e),
                text=raw
            )

    return instrs, None

def _parse_line(line: str) -> Instruction:
    """
    Supported syntax:
    - Rk = Rk + 1
    - Rk = Rk - 1   (also accepts '-·' thanks to normalization)
    - if Rk then gotof x
    - if Rk then gotob x
    """
    parts = line.split()

    # INC / DEC
    # example: "R1 = R1 + 1"
    if len(parts) == 5 and parts[1] == "=" and parts[3] in {"+", "-"} and parts[4] == "1":
        left = parts[0]
        right = parts[2]
        op = parts[3]

        k1 = _parse_reg(left)
        k2 = _parse_reg(right)
        if k1 != k2:
            raise ValueError("Expected format: Rk = Rk ± 1 (same register on both sides)")

        if op == "+":
            return Inc(k1)
        else:
            return Dec(k1)

    # GOTOF / GOTOB
    # example: "if R0 then gotob 2"
    if len(parts) == 5 and parts[0] == "if" and parts[2] == "then" and parts[3] in {"gotof", "gotob"}:
        k = _parse_reg(parts[1])
        try:
            x = int(parts[4])
        except ValueError:
            raise ValueError("Jump offset must be an integer")
        if x <= 0:
            raise ValueError("Jump offset must be > 0")

        return GotoF(k, x) if parts[3] == "gotof" else GotoB(k, x)

    raise ValueError("Unknown instruction format")
