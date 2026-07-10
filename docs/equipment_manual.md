# Filling Machine Equipment Manual

## Equipment Overview

The filling machine automatically dispenses cream or filling material
into product containers.

The machine consists of:

- Material tank
- Filling nozzle
- Pressure control valve
- Weight sensor
- Conveyor
- Emergency stop switch
- Control panel

## Alarm E101: Material Tank Level Low

E101 indicates that the material level in the tank is below the
minimum operating threshold.

Required actions:

1. Stop automatic filling.
2. Check the material tank level.
3. Confirm that the material supply valve is open.
4. Refill the tank if necessary.
5. Restart the equipment after confirming stable material supply.

## Alarm E102: Filling Pressure Low

E102 indicates that the filling pressure is below the configured
operating range.

Possible checks:

1. Check the compressed air supply.
2. Confirm that the pressure control valve is open.
3. Inspect the filling nozzle for blockage.
4. Check for leakage in the air or material supply line.
5. Verify that the pressure sensor is operating correctly.

Do not restart continuous operation until the pressure has returned
to the normal operating range.

## Alarm E103: Weight Sensor Communication Error

E103 indicates that communication with the weight sensor has been
interrupted.

Required actions:

1. Stop the conveyor.
2. Check the weight sensor power supply.
3. Check the communication cable.
4. Inspect the PLC communication status.
5. Restart the weight sensor controller.
6. Contact maintenance personnel if the alarm remains active.

## Alarm E104: Emergency Stop Activated

E104 means that an emergency stop switch has been pressed.

Required actions:

1. Identify why the emergency stop was activated.
2. Remove any safety hazard.
3. Release the emergency stop switch.
4. Perform the equipment reset procedure.
5. Restart only after confirming that the work area is safe.

## Daily Inspection

Before starting production, the operator must confirm:

- No material leakage
- No nozzle blockage
- Normal compressed air pressure
- Normal weight sensor communication
- Conveyor operates smoothly
- Emergency stop switches operate correctly
- Guards and covers are installed
- No active alarm remains on the control panel

## Calibration

The weight sensor must be calibrated:

- Before the first production run after maintenance
- After replacing the weight sensor
- When repeated weight deviation is detected
- According to the scheduled monthly calibration plan

Calibration procedure:

1. Stop the conveyor.
2. Clean the weighing platform.
3. Remove all products from the platform.
4. Perform zero calibration.
5. Place the certified reference weight on the platform.
6. Perform span calibration.
7. Remove the reference weight.
8. Confirm that the displayed value returns to zero.
9. Record the calibration result.