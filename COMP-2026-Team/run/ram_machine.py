from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List

from .instructions import Instruction, Inc, Dec, GotoF, GotoB

def _get(regs: Dict[int, int], k: int) -> int:
    return regs.get(k, 0)

def _set(regs: Dict[int, int], k: int, v: int) -> None:
    # keep dict clean: don't store zeros
    if v == 0:
        regs.pop(k, None)
    else:
        regs[k] = v

@dataclass
class RAMState:
    pc: int
    regs: Dict[int, int]  # sparse registers: only non-zero stored

def initial_state(input_value: int) -> RAMState:
    """
    According to the course:
    - PC starts at 1
    - R0 contains the input
    - other registers are 0
    """
    regs: Dict[int, int] = {}
    if input_value != 0:
        regs[0] = input_value
    return RAMState(pc=1, regs=regs)

def is_halted(state: RAMState, program_len: int) -> bool:
    # Machine halts when PC > |P| or PC <= 0
    return state.pc > program_len or state.pc <= 0

def step(state: RAMState, program: List[Instruction]) -> RAMState:
    """
    Execute one instruction indicated by PC (1-indexed).
    Returns the new state.
    Assumes state is not halted.
    """
    pc = state.pc
    instr = program[pc - 1]  # because pc is 1-indexed
    regs = dict(state.regs)  # copy for immutability-like behavior

    # Default next PC is pc+1, but gotos can change it
    next_pc = pc + 1

    if isinstance(instr, Inc):
        k = instr.reg
        _set(regs, k, _get(regs, k) + 1)

    elif isinstance(instr, Dec):
        k = instr.reg
        v = _get(regs, k)
        # saturated decrement: v -· 1
        _set(regs, k, v - 1 if v > 0 else 0)

    elif isinstance(instr, GotoF):
        k = instr.reg
        if _get(regs, k) != 0:
            next_pc = pc + instr.offset  # forward jump

    elif isinstance(instr, GotoB):
        k = instr.reg
        if _get(regs, k) != 0:
            # backward jump with saturated subtraction on PC
            next_pc = pc - instr.offset
            if next_pc < 0:
                next_pc = 0  # equivalent to saturation leading to halt (pc <= 0)

    else:
        # should never happen
        raise RuntimeError(f"Unknown instruction type: {instr}")

    return RAMState(pc=next_pc, regs=regs)
