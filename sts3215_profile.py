# Reference: the STS3215 (firmware 3.10) acceleration profile, measured on a bench (so101-sysid, Oct-Nov 2026).
# The servo's position loop tracks an internal target that moves toward your goal at constant acceleration and
# brakes in time to stop on it. Feed the goals you send; simulate the servo tracking the returned target.
import math

UNIT = 100 * 2 * math.pi / 4096  # [rad/s^2] per register unit (100 encoder steps/s^2)


def profile_accel(acceleration, maximum_acceleration):
    """Registers 41 (Acceleration, RAM) and 85 (Maximum_Acceleration, EEPROM) -> rad/s^2. 0 acts as 50."""
    return UNIT * min(acceleration or 50, maximum_acceleration)


def internal_target(goals, accel, dt):
    """Goals [rad] sent every dt [s] -> the target the position loop tracks, one per goal."""
    x, v, out = goals[0], 0.0, []
    for g in goals:
        e = g - x
        brake = accel * dt * (math.sqrt(0.25 + 2 * abs(e) / (accel * dt * dt)) - 0.5)  # fastest speed that still stops
        v += max(-accel * dt, min(accel * dt, math.copysign(brake, e) - v))
        x += v * dt
        out.append(x)
    return out
