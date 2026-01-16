# tests/test_executor.py

from run.api import run_text


def test_simple_output():
    """
    Program that increments R1 five times.
    Expected output: 5
    """
    program = "R1 = R1 + 1\n" * 5
    result = run_text(program, input_value=0)

    assert result.status == "OK"
    assert result.output == 5


def test_timeout():
    """
    Infinite loop:
    R0 = R0 + 1
    if R0 then gotob 1
    """
    program = "R0 = R0 + 1\nif R0 then gotob 1"
    result = run_text(program, input_value=0, max_steps=50)

    assert result.status == "TIMEOUT"


def test_syntax_error():
    """
    Invalid syntax: different registers on INC
    """
    program = "R1 = R2 + 1"
    result = run_text(program, input_value=0)

    assert result.status == "SYNTAX_ERROR"
