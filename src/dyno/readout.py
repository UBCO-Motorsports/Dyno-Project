from dyno.sample import Sample


def readout_text(sample: Sample) -> str:
    """Three lines: Torque, Speed, Power, with units, plus the run state."""
    return (
        f"Torque: {sample.torque_nm:.2f} N·m\n"
        f"Speed: {sample.speed_rpm:.2f} rpm\n"
        f"Power: {sample.power_kw:.3f} kW\n"
        f"State: {sample.run_state}"
    )
