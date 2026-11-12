from dataclasses import dataclass, replace

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
