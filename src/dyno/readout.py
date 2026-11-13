from dataclasses import dataclass, replace

from dyno.pedal import PedalLimits, pedal_voltages
from dyno.run_state import RigCommand, RunEvent, TestRun
from dyno.sample import Sample


def readout_text(sample: Sample) -> str:
    """Three lines: Torque, Speed, Power, with units, plus the run state."""
    return (
        f"Torque: {sample.torque_nm:.2f} N·m\n"
        f"Speed: {sample.speed_rpm:.2f} rpm\n"
        f"Power: {sample.power_kw:.3f} kW\n"
        f"State: {sample.run_state}"
    )


@dataclass
class OperatorSession:
    run: TestRun
    sample: Sample

    def arm(self) -> None:
        self.run.handle(RunEvent.ARM)

    def start(self) -> None:
        self.run.handle(RunEvent.START)

    def stop(self) -> None:
        self.run.handle(RunEvent.STOP)

    def text(self) -> str:
        display = replace(self.sample, run_state=self.run.state().value)
        return readout_text(display)

    def command(self, requested: RigCommand) -> RigCommand:
        return self.run.command(requested)

    def manual_command(
        self,
        pedal_position: float,
        valve_setpoint: float,
        a: PedalLimits,
        b: PedalLimits,
    ) -> RigCommand:
        """Build the command from one pedal position, then pass it through run.command()."""
        if not (0.0 <= pedal_position <= 1.0):
            raise ValueError("position must be between 0.0 and 1.0")
        if not (0.0 <= valve_setpoint <= 1.0):
            raise ValueError("valve setpoint must be between 0.0 and 1.0")
        voltage_a, voltage_b = pedal_voltages(pedal_position, a, b)
        requested = RigCommand(
            pedal_voltage_a=voltage_a,
            pedal_voltage_b=voltage_b,
            torque_command_nm=0,
            valve_setpoint=valve_setpoint,
        )
        return self.run.command(requested)
