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


def test_little_endian_unaligned_start_bit_4_length_12():
    signal = SignalDef(
        name="example_bit_span",
        start_bit=4,
        length=12,
        scale=1.0,
        offset=0,
        signed=False,
        little_endian=True,
    )
    # Intel numbering: bit 0 is LSB of byte 0. Field covers payload bits 4..15.
    # Byte0 0xF0 = 0b11110000 → bits 4,5,6,7 = 1,1,1,1.
    # Byte1 0x0A = 0b00001010 → bits 8,9,10,11 = 0,1,0,1 (LSB..MSB within byte).
    # Raw LSB-first: bit0..3 from 1111, bit4..7 from 0101 → 0b1010_1111 = 175.
    # Off-by-one start_bit (5 instead of 4) would assemble 0b0101_0111 = 87 and fail here.
    assert decode_signal(bytes([0xF0, 0x0A]), signal) == 175.0


def test_big_endian_mid_byte_motorola_four_bits():
    signal = SignalDef(
        name="example_moto_nibble",
        start_bit=4,
        length=4,
        scale=3.0,
        offset=0,
        signed=False,
        little_endian=False,
    )
    # Motorola numbering: bit 0 is MSB of byte 0; bit n sits at byte n//8, bit 7-(n%8).
    # Single byte 0x35 = 0b00110101. Motorola bits 4..7 are Intel bits 3,2,1,0 = 0,1,0,1.
    # MSB-first raw = 0b0101 = 5 → 5 * 3 = 15 (not the byte-aligned from_bytes path).
    assert decode_signal(bytes([0x35]), signal) == 15.0


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
