from __future__ import annotations
import math
from typing import List, Tuple

from .instructions import Instruction, Inc, Dec, GotoF, GotoB

# --------------------------
# Cantor pairing (modified)
# <x,y> = 1 + y + (x+y)(x+y+1)/2
# Bijection N^2 -> N+ (never returns 0)
# --------------------------

def cantor_pair(x: int, y: int) -> int:
    if x < 0 or y < 0:
        raise ValueError("Cantor pair expects natural numbers (>= 0).")
    s = x + y
    return 1 + y + (s * (s + 1)) // 2

def cantor_unpair(z: int) -> Tuple[int, int]:
    """
    Inverse of cantor_pair for z in N+ (z >= 1).
    Returns (x,y) such that cantor_pair(x,y) = z.
    """
    if z <= 0:
        raise ValueError("cantor_unpair expects z in N+ (>= 1).")

    # We need to find s such that T_s < z <= T_{s+1}, where T_s = (s)(s+1)/2
    # With the modified formula, we can use:
    # z = 1 + y + T_{x+y}
    # Let w = z - 1, then w = y + T_s with s = x+y
    w = z - 1

    # Find s such that T_s <= w < T_{s+1}
    # Solve s(s+1)/2 <= w
    s = int((math.isqrt(8 * w + 1) - 1) // 2)
    T = (s * (s + 1)) // 2

    y = w - T
    x = s - y
    if x < 0:
        raise RuntimeError("Internal error while unpairing (x became negative).")
    return x, y

# --------------------------
# Sequence decoding:
# seq = <a1, <a2, <... <an, 0>...>>
# Stop when right part is 0
# --------------------------

def decode_sequence(seq_code: int) -> List[int]:
    """
    Decode a nested Cantor sequence ending with 0.
    Example: <5,<7,0>> -> [5,7]
    """
    if seq_code == 0:
        return []

    res: List[int] = []
    cur = seq_code
    while cur != 0:
        a, rest = cantor_unpair(cur)
        res.append(a)
        cur = rest
    return res

# --------------------------
# Instruction decoding via g(i)
# --------------------------

def decode_instruction(u: int) -> Instruction:
    """
    Decode one instruction integer u according to the course g(i).
    """
    if u < 0:
        raise ValueError("Instruction code must be >= 0.")

    r = u % 3

    # INC: u = 3k
    if r == 0:
        k = u // 3
        return Inc(k)

    # DEC: u = 3k + 1
    if r == 1:
        k = (u - 1) // 3
        return Dec(k)

    # JUMP: u = 3 * <b, <k,x>> - 1  (=> u % 3 == 2)
    # so t = (u+1)/3 = <b, <k,x>>
    t = (u + 1) // 3
    b, tmp = cantor_unpair(t)      # b in {0,1}
    k, x = cantor_unpair(tmp)

    if b not in (0, 1):
        raise ValueError(f"Invalid jump type b={b} decoded from {u}.")

    if x <= 0:
        # In the RAM model, offsets are positive
        raise ValueError(f"Invalid jump offset x={x} decoded from {u} (must be > 0).")

    return GotoF(k, x) if b == 0 else GotoB(k, x)

def decode_program(GP: int) -> List[Instruction]:
    """
    Decode a whole RAM program code G(P) into a list of Instruction.
    """
    codes = decode_sequence(GP)
    return [decode_instruction(u) for u in codes]
