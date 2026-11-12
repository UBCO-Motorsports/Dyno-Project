from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from dyno.log_csv import read_log


def plot_run(csv_path: Path, png_path: Path) -> None:
    """Torque (N·m) and power (kW) against speed (rpm). Title is the CSV file name."""
    samples = read_log(csv_path)
    if not samples:
        raise ValueError("no samples")

    speed_rpm = [sample.speed_rpm for sample in samples]
    torque_nm = [sample.torque_nm for sample in samples]
    power_kw = [sample.power_kw for sample in samples]

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("speed (rpm)")
    ax1.set_ylabel("torque (N·m)")
    ax1.plot(speed_rpm, torque_nm, color="C0")

    ax2 = ax1.twinx()
    ax2.set_ylabel("power (kW)")
    ax2.plot(speed_rpm, power_kw, color="C1")

    fig.suptitle(csv_path.name)
    fig.tight_layout()
    fig.savefig(png_path)
    plt.close(fig)
