"""First-order motor and water-brake model for offline development.

The simulator implements the hardware ports (``ForceSource``, ``SpeedSource``,
``Valve``, ``PedalOutput``) so the supervisor can run against a deterministic
stand-in for the rig.

Model (ω in rad/s, ``fill`` and pedal position in 0–1):

- Motor torque: ``T_m = pedal_position × PEAK_TORQUE_NM``. Released pedals
  (#18 safe command, or ``torque_command_nm == 0`` with both voltages at zero)
  give ``pedal_position = 0``, so ``T_m = 0``. #43 manual control holds
  ``torque_command_nm == 0`` but uses non-zero pedal voltages for load.
- Brake torque: ``T_b = k × fill × ω²``
- Shaft dynamics: ``dω/dt = (T_m − T_b − c × ω) / J``
- Load cell: ``force_n = T_b / arm_length_m``

Time advances only through :meth:`DynoSimulator.step`; there is no wall-clock
waiting.

**Example defaults** (constructor arguments, not physical calibration):

- ``k = 6×10⁻⁴ N·m·s²/rad²``: at full pedal (150 N·m) and half fill, steady
  speed with ``c = 0`` is ``ω = sqrt(150 / (k×0.5)) ≈ 707 rad/s`` (~6750 rpm),
  below ``MAX_SPEED_RPM`` (7000).
- ``c = 0``: removes linear drag so behaviour tests can use the closed-form
  steady-state ``ω = sqrt(T_m / (k × fill))``.
- ``J = 0.1 kg·m²``: sets inertia so the explicit-Euler step with ``dt_s ≈ 0.01``
  reaches steady state within the test settle window without unstable ringing.
"""

from __future__ import annotations

import math

from dyno.limits import PEAK_TORQUE_NM
from dyno.pedal import PedalLimits
from dyno.run_state import RigCommand

_DEFAULT_K = 6e-4
_DEFAULT_C = 0.0
_DEFAULT_J = 0.1
_TWO_PI = 2.0 * math.pi


def _pedal_position_from_voltages(
    voltage_a: float,
    voltage_b: float,
    limits_a: PedalLimits,
    limits_b: PedalLimits,
) -> float:
    span_a = limits_a.maximum_v - limits_a.minimum_v
    span_b = limits_b.maximum_v - limits_b.minimum_v
    pos_a = (voltage_a - limits_a.minimum_v) / span_a
    pos_b = (voltage_b - limits_b.minimum_v) / span_b
    position = (pos_a + pos_b) / 2.0
    return max(0.0, min(1.0, position))


class DynoSimulator:
    """Explicit-Euler integrator for the simplified dyno plant."""

    def __init__(
        self,
        *,
        arm_length_m: float,
        k: float = _DEFAULT_K,
        c: float = _DEFAULT_C,
        J: float = _DEFAULT_J,
        pedal_limits_a: PedalLimits | None = None,
        pedal_limits_b: PedalLimits | None = None,
    ) -> None:
        if arm_length_m <= 0:
            raise ValueError("arm_length_m")
        if k <= 0 or J <= 0 or c < 0:
            raise ValueError("inertia or brake coefficients")
        self._arm_length_m = arm_length_m
        self._k = k
        self._c = c
        self._J = J
        self._pedal_a = pedal_limits_a or PedalLimits(0.5, 4.5)
        self._pedal_b = pedal_limits_b or PedalLimits(0.25, 2.25)

        self._omega_rad_s = 0.0
        self._fill = 0.0
        self._fill_setpoint = 0.0
        self._pedal_position = 0.0
        self._motor_torque_nm = 0.0
        self._channel_a = 0.0
        self._channel_b = 0.0

    def apply_command(self, command: RigCommand) -> None:
        """Apply an effective rig command (e.g. after :class:`~dyno.run_state.TestRun`)."""
        self._fill_setpoint = max(0.0, min(1.0, command.valve_setpoint))
        self._fill = self._fill_setpoint
        self._channel_a = command.pedal_voltage_a
        self._channel_b = command.pedal_voltage_b
        self._pedal_position = _pedal_position_from_voltages(
            command.pedal_voltage_a,
            command.pedal_voltage_b,
            self._pedal_a,
            self._pedal_b,
        )
        self._motor_torque_nm = self._pedal_position * PEAK_TORQUE_NM

    def step(self, dt_s: float) -> None:
        if dt_s <= 0 or not math.isfinite(dt_s):
            raise ValueError("dt_s")
        brake_torque_nm = self._k * self._fill * self._omega_rad_s**2
        net_torque_nm = self._motor_torque_nm - brake_torque_nm - self._c * self._omega_rad_s
        self._omega_rad_s += (net_torque_nm / self._J) * dt_s
        if self._omega_rad_s < 0:
            self._omega_rad_s = 0.0

    def force_n(self) -> float:
        brake_torque_nm = self._k * self._fill * self._omega_rad_s**2
        return brake_torque_nm / self._arm_length_m

    def speed_rpm(self) -> float:
        return self._omega_rad_s * 60.0 / _TWO_PI

    def set_setpoint(self, setpoint: float) -> None:
        self._fill_setpoint = max(0.0, min(1.0, setpoint))
        self._fill = self._fill_setpoint

    def position(self) -> float:
        return self._fill

    def set_voltages(self, channel_a: float, channel_b: float) -> None:
        self._channel_a = channel_a
        self._channel_b = channel_b
        self._pedal_position = _pedal_position_from_voltages(
            channel_a, channel_b, self._pedal_a, self._pedal_b
        )
        self._motor_torque_nm = self._pedal_position * PEAK_TORQUE_NM

    def voltages(self) -> tuple[float, float]:
        return (self._channel_a, self._channel_b)
