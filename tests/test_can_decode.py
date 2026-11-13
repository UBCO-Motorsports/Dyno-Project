from dyno.can_decode import SignalDef, decode_signal


def test_little_endian_scale_and_offset():
    signal = SignalDef(
        name="example_speed",
        start_bit=0,
        length=16,
        scale=0.1,
        offset=0,
        signed=False,
        little_endian=True,
    )
    assert decode_signal(bytes([0xE8, 0x03]), signal) == 100.0


def test_little_endian_second_byte_start_bit_8():
    signal = SignalDef(
        name="example_aux",
        start_bit=8,
        length=8,
        scale=1.0,
        offset=5,
        signed=False,
        little_endian=True,
    )
    # Hand check: second byte is 0x0A (=10); 10 * 1 + 5 = 15
    assert decode_signal(bytes([0x00, 0x0A]), signal) == 15.0


def test_signed_eight_bit_negative_one():
    signal = SignalDef(
        name="example_signed",
        start_bit=0,
        length=8,
        scale=1.0,
        offset=0,
        signed=True,
        little_endian=True,
    )
    # 0xFF as signed 8-bit is -1 before scale/offset
    assert decode_signal(bytes([0xFF]), signal) == -1.0


def test_length_seventeen_rejected():
    signal = SignalDef(
        name="example_too_wide",
        start_bit=0,
        length=17,
        scale=1.0,
        offset=0,
        signed=False,
        little_endian=True,
    )
    try:
        decode_signal(bytes([0x00, 0x00, 0x00]), signal)
    except ValueError as exc:
        assert "length" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for length 17")


def test_big_endian_sixteen_bit_scale():
    signal = SignalDef(
        name="example_big_endian",
        start_bit=0,
        length=16,
        scale=0.1,
        offset=0,
        signed=False,
        little_endian=False,
    )
    # Hand check: big-endian 0x03 0xE8 → 0x03E8 = 3*256+232 = 1000 → *0.1 = 100.0
    assert decode_signal(bytes([0x03, 0xE8]), signal) == 100.0
