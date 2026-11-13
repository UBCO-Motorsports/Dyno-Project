from dataclasses import dataclass


@dataclass(frozen=True)
class SignalDef:
    name: str
    start_bit: int
    length: int
    scale: float
    offset: float
    signed: bool
    little_endian: bool


def decode_signal(payload: bytes, signal: SignalDef) -> float:
    """Extract the integer and return integer * scale + offset."""
    if signal.length < 1 or signal.length > 16:
        raise ValueError(f"length must be 1..16, got {signal.length}")

    raw = _extract_raw(payload, signal.start_bit, signal.length, signal.little_endian)

    if signal.signed and raw & (1 << (signal.length - 1)):
        raw -= 1 << signal.length

    return raw * signal.scale + signal.offset


def _extract_raw(
    payload: bytes, start_bit: int, length: int, little_endian: bool
) -> int:
    if little_endian:
        return _extract_intel(payload, start_bit, length)

    if start_bit % 8 == 0 and length % 8 == 0:
        start_byte = start_bit // 8
        nbytes = length // 8
        if start_byte + nbytes > len(payload):
            raise ValueError("payload too short for signal")
        return int.from_bytes(payload[start_byte : start_byte + nbytes], "big")

    return _extract_motorola(payload, start_bit, length)


def _extract_intel(payload: bytes, start_bit: int, length: int) -> int:
    raw = 0
    for i in range(length):
        bit_pos = start_bit + i
        byte_idx = bit_pos // 8
        if byte_idx >= len(payload):
            raise ValueError("payload too short for signal")
        bit_idx = bit_pos % 8
        bit_val = (payload[byte_idx] >> bit_idx) & 1
        raw |= bit_val << i
    return raw


def _extract_motorola(payload: bytes, start_bit: int, length: int) -> int:
    raw = 0
    for i in range(length):
        bit_number = start_bit + i
        byte_idx = bit_number // 8
        if byte_idx >= len(payload):
            raise ValueError("payload too short for signal")
        bit_idx = 7 - (bit_number % 8)
        bit_val = (payload[byte_idx] >> bit_idx) & 1
        raw = (raw << 1) | bit_val
    return raw
