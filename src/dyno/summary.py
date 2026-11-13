from dataclasses import dataclass

from dyno.sample import Sample


@dataclass(frozen=True)
class ChannelSummary:
    minimum: float
    maximum: float
    mean: float


@dataclass(frozen=True)
class LogSummary:
    torque_nm: ChannelSummary
    speed_rpm: ChannelSummary
    power_kw: ChannelSummary


def _channel_summary(values: list[float]) -> ChannelSummary:
    return ChannelSummary(
        minimum=min(values),
        maximum=max(values),
        mean=sum(values) / len(values),
    )


def summarise(samples: list[Sample]) -> LogSummary:
    """Arithmetic mean. Empty input raises ValueError."""
    if not samples:
        raise ValueError("empty")

    torque_values = [s.torque_nm for s in samples]
    speed_values = [s.speed_rpm for s in samples]
    power_values = [s.power_kw for s in samples]

    return LogSummary(
        torque_nm=_channel_summary(torque_values),
        speed_rpm=_channel_summary(speed_values),
        power_kw=_channel_summary(power_values),
    )
