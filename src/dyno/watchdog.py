from dyno.run_state import RigCommand


def heartbeat_expired(last_seen_s: float, now_s: float, timeout_s: float) -> bool:
    """True when now_s - last_seen_s is greater than timeout_s."""
    if timeout_s <= 0:
        raise ValueError("invalid timeout")
    if now_s < last_seen_s:
        raise ValueError("clock went backwards")
    return (now_s - last_seen_s) > timeout_s


def command_for_heartbeat(
    last_seen_s: float,
    now_s: float,
    timeout_s: float,
    requested: RigCommand,
    safe_valve_setpoint: float,
) -> RigCommand:
    """If the heartbeat has expired, return the safe command. Otherwise return requested."""
    if heartbeat_expired(last_seen_s, now_s, timeout_s):
        return RigCommand(
            pedal_voltage_a=0,
            pedal_voltage_b=0,
            torque_command_nm=0,
            valve_setpoint=safe_valve_setpoint,
        )
    return requested
