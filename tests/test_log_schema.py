from dyno.log_schema import LOG_COLUMNS


def test_log_columns_are_fixed():
    assert LOG_COLUMNS == (
        "timestamp_utc",
        "torque_nm",
        "speed_rpm",
        "power_kw",
        "strain",
        "valve_setpoint",
        "pedal_voltage_a",
        "pedal_voltage_b",
        "run_state",
    )


def test_log_columns_are_unique():
    assert len(LOG_COLUMNS) == len(set(LOG_COLUMNS))
