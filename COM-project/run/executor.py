from __future__ import annotations
from typing import List

from .api import ExecResult
from .instructions import Instruction
from .parser_text import parse_program_text
from .ram_machine import initial_state, is_halted, step

def execute(program: List[Instruction], input_value: int, max_steps: int = 100_000) -> ExecResult:
    """
    Execute a parsed RAM program on a given input.
    Returns ExecResult with status OK or TIMEOUT.
    Output convention: we return R1 (output register) as in the course model.
    """
    state = initial_state(input_value)
    steps = 0
    prog_len = len(program)

    while not is_halted(state, prog_len):
        if steps >= max_steps:
            return ExecResult(
                status="TIMEOUT",
                output=None,
                steps=steps,
                final_pc=state.pc,
                registers=state.regs,
                error=f"Maximum steps exceeded ({max_steps}). Program may diverge."
            )
        state = step(state, program)
        steps += 1

    # halted: output is R1 (register index 1)
    output = state.regs.get(1, 0)

    return ExecResult(
        status="OK",
        output=output,
        steps=steps,
        final_pc=state.pc,
        registers=state.regs,
        error=None
    )

def run_text(program_text: str, input_value: int, max_steps: int = 100_000) -> ExecResult:
    """
    Parse and execute a RAM program given as text.
    """
    program, err = parse_program_text(program_text)
    if err is not None:
        return ExecResult(
            status="SYNTAX_ERROR",
            output=None,
            steps=0,
            final_pc=None,
            registers=None,
            error=f"Line {err.line}: {err.message} | Text: {err.text}"
        )

    return execute(program, input_value, max_steps=max_steps)

def run_encoded(program_code: int, input_value: int, max_steps: int = 100_000) -> ExecResult:
    """
    Decode Godel-encoded program then execute it.
    """
    try:
        from .godel import decode_program
        program = decode_program(program_code)
    except Exception as e:
        return ExecResult(
            status="DECODE_ERROR",
            output=None,
            steps=0,
            final_pc=None,
            registers=None,
            error=str(e)
        )

    return execute(program, input_value, max_steps=max_steps)

