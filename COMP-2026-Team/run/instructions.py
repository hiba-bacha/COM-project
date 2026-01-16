from __future__ import annotations
from dataclasses import dataclass
from typing import Union

# Rk = Rk + 1
@dataclass(frozen=True)
class Inc:
    reg: int  # k in Rk

# Rk = Rk -· 1  (saturated subtraction: never below 0)
@dataclass(frozen=True)
class Dec:
    reg: int

# if Rk then gotof x
@dataclass(frozen=True)
class GotoF:
    reg: int
    offset: int  # x > 0

# if Rk then gotob x
@dataclass(frozen=True)
class GotoB:
    reg: int
    offset: int  # x > 0

Instruction = Union[Inc, Dec, GotoF, GotoB]
