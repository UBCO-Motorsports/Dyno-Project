"""Thin tkinter operator window over OperatorSession."""

from __future__ import annotations

from datetime import UTC, datetime

from dyno.pedal import PedalLimits
from dyno.readout import OperatorSession
from dyno.run_state import TestRun
from dyno.sample import Sample

# Example limits from rig.example.toml — confirm on bench before real use.
_EXAMPLE_PEDAL_A = PedalLimits(minimum_v=0.5, maximum_v=4.5)
_EXAMPLE_PEDAL_B = PedalLimits(minimum_v=0.25, maximum_v=2.25)


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
    last_applied_var = tk.StringVar(value="Last applied: —")
    pedal_var = tk.StringVar()
    valve_var = tk.StringVar()

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

    manual = tk.Frame(root)
    manual.pack(padx=12, pady=4, fill=tk.X)
    tk.Label(manual, text="Pedal %").grid(row=0, column=0, sticky=tk.W)
    tk.Entry(manual, textvariable=pedal_var, width=8).grid(row=0, column=1, padx=(4, 12))
    tk.Label(manual, text="Valve").grid(row=0, column=2, sticky=tk.W)
    tk.Entry(manual, textvariable=valve_var, width=8).grid(row=0, column=3, padx=4)

    def on_apply() -> None:
        try:
            pedal_pct = float(pedal_var.get())
            valve = float(valve_var.get())
        except ValueError:
            status_var.set("Enter numeric pedal and valve values.")
            return
        try:
            session.manual_command(
                pedal_pct / 100.0,
                valve,
                _EXAMPLE_PEDAL_A,
                _EXAMPLE_PEDAL_B,
            )
        except ValueError as exc:
            status_var.set(str(exc))
            return
        status_var.set("")
        last_applied_var.set(
            f"Last applied: Pedal {pedal_pct:g}%  Valve {valve:g}"
        )

    tk.Button(manual, text="Apply", command=on_apply).grid(row=0, column=4, padx=8)
    tk.Label(root, textvariable=last_applied_var, anchor=tk.W).pack(padx=12, fill=tk.X)

    buttons = tk.Frame(root)
    buttons.pack(pady=8)
    tk.Button(buttons, text="Arm", width=8, command=on_arm).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Start", width=8, command=on_start).pack(side=tk.LEFT, padx=4)
    tk.Button(buttons, text="Stop", width=14, command=on_stop).pack(side=tk.LEFT, padx=4)

    refresh_readout()
    root.mainloop()


if __name__ == "__main__":
    main()
