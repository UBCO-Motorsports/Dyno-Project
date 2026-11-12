#!/usr/bin/env bash
# Dyno safety guardrails — same checks as the "Guardrails" job in tests.yml.
# Fail closed on patterns that mean the laptop is acting like the safety system
# or opening live hardware from src/dyno.
set -euo pipefail
cd "$(dirname "$0")/.."

fail=0

if grep -rEn --include='*.py' \
  'serial\.Serial\(|can\.interface\.Bus\(|can\.Bus\(' \
  src/dyno 2>/dev/null; then
  echo "::error::src/dyno must not open serial ports or CAN buses directly (AGENTS.md safety boundary)"
  fail=1
fi

# Pedal / valve "drive" call sites that look like live hardware actuation.
if grep -rEn --include='*.py' \
  'tractive.?battery|spin_motor\(|drive_valve\(|set_valve_position\(' \
  src/dyno 2>/dev/null; then
  echo "::error::src/dyno must not drive the physical valve, spin the motor, or connect the tractive battery"
  fail=1
fi

if [ "$fail" -ne 0 ]; then
  exit 1
fi
echo "guardrails: ok"
