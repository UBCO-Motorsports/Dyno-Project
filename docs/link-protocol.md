# Laptop–controller link protocol

The laptop and controller exchange one JSON object per line over USB serial.
Each line is UTF-8 JSON followed by a newline (\`\\n\`).

## Serial settings

- Baud rate: 115200
- Framing: one JSON object per line
- Encoding: UTF-8
- Line ending: newline (\`\\n\`)

## Messages

Every message contains \`type\` and \`seq\`. Sequence numbers are non-negative
integers. Track sequence numbers separately for each sending direction. A
receiver rejects repeated or older sequence numbers. A gap reports the number
of messages missed since the previous accepted sequence number.

| Direction | \`type\` | Fields |
| --- | --- | --- |
| laptop → controller | \`setpoint\` | \`seq\`, \`pedal_position\` (0–1), \`valve_setpoint\` |
| laptop → controller | \`heartbeat\` | \`seq\` |
| laptop → controller | \`acknowledge\` | \`seq\` (clears a latched safe state) |
| controller → laptop | \`sample\` | \`seq\`, \`controller_time_us\`, \`load_raw\`, \`speed_rpm\`, \`valve_position\`, \`pedal_voltage_a\`, \`pedal_voltage_b\`, \`state\` |
| controller → laptop | \`fault\` | \`seq\`, \`code\`, \`detail\` |

\`controller_time_us\` is the controller's monotonic sample timestamp in
microseconds. All channels in a sample frame refer to that same instant.

## Validation

Numeric fields must be finite numbers. Sequence numbers and
\`controller_time_us\` are non-negative integers. \`pedal_position\` must be in
the inclusive range 0–1. \`state\`, \`code\`, and \`detail\` are strings.

Unknown message types, missing fields, extra fields, invalid JSON, invalid
UTF-8, and fields with the wrong type are rejected with \`ValueError\`. The
shared cases in \`tests/contract/link_cases.json\` are the contract for the
Python laptop code and controller firmware.

## Heartbeat and safe behavior

The laptop sends heartbeat messages while it is operating. If the controller
does not receive a heartbeat within its configured timeout, it enters the safe
state and commands zero pedal voltage and zero torque, together with the
safe valve setpoint.

Issue #29 uses 0.5 seconds as an example timeout for tests. It is not an
approved hardware setting. Electrical and the safety owners must confirm the
timeout and safe behavior before the controller is used on the rig. The
physical meaning of the safe valve setpoint must come from Mechanical.
