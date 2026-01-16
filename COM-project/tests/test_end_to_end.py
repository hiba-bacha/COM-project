# tests/test_end_to_end.py

from run.api import run_text, run_encoded
from run.godel import cantor_pair


def encode_instruction_inc(k: int) -> int:
    # INC Rk -> 3k
    return 3 * k


def encode_instruction_dec(k: int) -> int:
    # DEC Rk -> 3k + 1
    return 3 * k + 1


def encode_instruction_gotof(k: int, x: int) -> int:
    # gotof -> 3*<0,<k,x>> - 1
    return 3 * cantor_pair(0, cantor_pair(k, x)) - 1


def encode_instruction_gotob(k: int, x: int) -> int:
    # gotob -> 3*<1,<k,x>> - 1
    return 3 * cantor_pair(1, cantor_pair(k, x)) - 1


def encode_program(instr_codes: list[int]) -> int:
    """
    Build G(P) = <a1, <a2, <... <an, 0>...>>
    using the same Cantor pairing as in run.godel
    """
    code = 0
    for a in reversed(instr_codes):
        code = cantor_pair(a, code)
    return code


def test_end_to_end_simple_incs():
    # Text program: increment R1 five times => output should be 5
    program_text = "R1 = R1 + 1\n" * 5

    # Encoded program: [INC(]()
