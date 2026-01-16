from run.godel import cantor_pair, cantor_unpair, decode_sequence, decode_instruction
from run.instructions import Inc, Dec, GotoF, GotoB


def test_cantor_roundtrip():
    for x in range(6):
        for y in range(6):
            z = cantor_pair(x, y)
            xx, yy = cantor_unpair(z)
            assert (x, y) == (xx, yy)


def test_decode_sequence_simple():
    # <5, <7, 0>>
    code = cantor_pair(5, cantor_pair(7, 0))
    assert decode_sequence(code) == [5, 7]


def test_decode_instruction_inc_dec():
    assert decode_instruction(0) == Inc(0)      # 3*0
    assert decode_instruction(3) == Inc(1)      # 3*1
    assert decode_instruction(1) == Dec(0)      # 3*0+1
    assert decode_instruction(4) == Dec(1)      # 3*1+1


def test_decode_instruction_goto():
    # gotof: u = 3*<0,<k,x>> - 1
    k, x = 2, 5
    u_f = 3 * cantor_pair(0, cantor_pair(k, x)) - 1
    assert decode_instruction(u_f) == GotoF(k, x)

    # gotob: u = 3*<1,<k,x>> - 1
    u_b = 3 * cantor_pair(1, cantor_pair(k, x)) - 1
    assert decode_instruction(u_b) == GotoB(k, x)
