"""Thin tkinter operator window over OperatorSession."""

from __future__ import annotations

from datetime import UTC, datetime

from dyno.readout import OperatorSession
from dyno.run_state import TestRun
from dyno.sample import Sample


def build_session(sample: Sample, safe_valve_setpoint: float) -> OperatorSession:
    """Session the window will hold."""
    return OperatorSession(
        run=TestRun(safe_valve_setpoint=safe_valve_setpoint),
        sample=sample,
    )


def main() -> None:
    import tkinter as tk

    sample = Sample(
        timestamp_utc=datetime.now(UTC),
        torque_nm=10,
        speed_rpm=1000,
        strain=0.001,
        valve_setpoint=0.2,
        pedal_voltage_a=0.5,
        pedal_voltage_b=0.5,
        run_state="idle",
    )
    session = build_session(sample, safe_valve_setpoint=0.0)

    root = tk.Tk()
    root.title("Dyno")

    readout_var = tk.StringVar()
    status_var = tk.StringVar()

    def refresh_readout() -> None:
        readout_var.set(session.text())

    def on_arm() -> None:
        session.arm()
        status_var.set("")
        refresh_readout()

    def on_start() -> None:
        try:
            session.start()
            status_var.set("")
        except ValueError as exc:
            status_var.set(str(exc))
        refresh_readout()

    def on_stop() -> None:
        session.stop()
        status_var.set("")
        refresh_readout()

    tk.Label(root, textvariable=readout_var, justify=tk.LEFT, anchor=tk.W).pack(
        padx=12, pady=12, fill=tk.X
    )
    tk.Label(root, textvariable=status_var, fg="red", anchor=tk.W).pack(
        padx=12, fill=tk.X
    )

    buttons = tk.Frame(root)
    buttons.pack(pady=8)
    tk.Button(buttons, text="Arm", width=8, command=on_arm).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Start", width=8, command=on_start).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Stop", width=8, command=on_stop).pack(side=tk.LEFT, padx=4)

    refresh_readout()
    root.mainloop()


if __name__ == "__main__":
    main()
