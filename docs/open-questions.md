# Open questions

The software issues can start without these answers. Hardware, limits that protect the rig, and any number marked TBC in an issue cannot be treated as final until the person named here has answered.

Write the answer in the **Answer** line. If they do not know yet, write `still open`, the date, and who you asked.

Confirmed already, so do not re-open these unless that person changes them:

- Peak torque is 150 N·m.
- Maximum speed is 7000 rpm.
- Power is capped below 80 kW. The calculator must not hide a reading above that cap.
- The absorber is direct-coupled by a shaft. The original proposal mentioned a chain drive; that is not the working assumption.
- Load control is automated: sweeps, holds, and lap replays.
- Strain is sampled at 10 Hz or faster.
- The log rate follows the slowest input. Speed arrives at the VCU message rate.
- The energy source is the vehicle tractive battery, not a bench supply.
- A procedure CSV describes throttle (pedal) and load. A separate log CSV is the recording of a run.

## Sensors — ask Owen and Alex

### 1. What measures torque on the reaction arm?

The requirements list a load cell (`torque = force × arm length`) and a separate strain gauge. The success notes say torque via the strain gauge. These might be one sensor or two.

- **Answer:**
- **Who / date:**

### 2. What is the reaction arm length, in metres?

- **Answer:**
- **Who / date:**

### 3. What accuracy is required for torque, speed, and strain?

- **Answer:**
- **Who / date:**

### 4. What engineering unit should the strain channel report?

For example microstrain, or force in newtons. Until this is answered, software keeps the strain channel separate from `torque_nm`.

- **Answer:**
- **Who / date:**

## Vehicle controls and electrical

### 5. Who holds the motor-controller and VCU CAN message definitions?

Do not guess message IDs, bit positions, or scaling.

- **Answer (name the person, and where the definitions live):**
- **Who / date:**

### 6. How does a bench test ask the motor for torque?

The project needs simulated pedal voltages into the VCU. Confirm whether an external CAN torque or speed command is also accepted.

- **Answer:**
- **Who / date:**

### 7. What are the minimum and maximum voltages for each pedal channel?

Electrical is providing the hardware that generates these two voltages. Example numbers in tests are not the car.

- **Answer:**
- **Who / date:**

### 8. How often does the VCU broadcast motor speed?

- **Answer (Hz, or the message period):**
- **Who / date:**

### 9. Who supervises use of the tractive battery for a dyno run?

- **Answer:**
- **Who / date:**

## Mechanical

### 10. Is the motor direct-coupled, and does the housing react through a fixed arm?

- **Answer:**
- **Who / date:**

### 11. Which valve command unloads the water brake?

Software tests inject this as `safe_valve_setpoint`. The physical meaning has to come from Mechanical.

- **Answer:**
- **Who / date:**

### 12. What valve setpoint units are used, and how close must achieved position stay to the command?

- **Answer:**
- **Who / date:**

## Safety sign-off

Software cannot replace guarding, the emergency stop, or high-voltage isolation.

### 13. Who signs mechanical guarding and the emergency stop?

- **Answer:**
- **Who / date:**

### 14. Who signs high-voltage isolation?

- **Answer:**
- **Who / date:**

## Procedure file

### 15. Is there a sample procedure CSV from a real session?

The software schema is fixed in the profile issues. If the real file differs, the parser changes only after this sample is attached to the issue.

- **Answer:**
- **Who / date:**
