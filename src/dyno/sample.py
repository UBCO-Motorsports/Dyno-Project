from dataclasses import dataclass
from datetime import datetime

from dyno.power import mechanical_power_kw


@dataclass(frozen=True)
class Sample:
    timestamp_utc: datetime
    torque_nm: float
    speed_rpm: float
    strain: float
    valve_setpoint: float
    pedal_voltage_a: float
    pedal_voltage_b: float
    run_state: str

    def __post_init__(self) -> None:
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("timestamp_utc must include timezone")

    @property
    def power_kw(self) -> float:
        """Uses mechanical_power_kw. Not stored separately."""
        return mechanical_power_kw(self.torque_nm, self.speed_rpm)
