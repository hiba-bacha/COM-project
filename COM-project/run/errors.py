from dataclasses import dataclass

@dataclass(frozen=True)
class SyntaxErrorInfo:
    line: int          # line number starting at 1
    message: str       # human readable error message
    text: str          # original line text
