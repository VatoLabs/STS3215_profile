# Sanity checks for sts3215_profile.py (run: python -m pytest test_profile.py)
import math

from sts3215_profile import UNIT, internal_target, profile_accel


def test_registers():
    assert math.isclose(profile_accel(254, 254), 38.96, abs_tol=0.01)  # LeRobot's setting
    assert profile_accel(0, 254) == profile_accel(50, 254)  # 0 acts as 50
    assert profile_accel(254, 50) == 50 * UNIT  # min() cap


def test_step_reaches_goal_within_accel_limit():
    a, dt = profile_accel(254, 254), 0.002
    goals = [0.0] * 10 + [0.75] * 500
    x = internal_target(goals, a, dt)
    assert abs(x[-1] - 0.75) < 1e-6
    v = [(x[i + 1] - x[i]) / dt for i in range(len(x) - 1)]
    assert max(abs(v[i + 1] - v[i]) / dt for i in range(len(v) - 1)) <= a * (1 + 1e-9)


def test_max_acceleration_zero_switches_profile_off():
    assert profile_accel(254, 0) is None
    assert internal_target([0.0, 1.0, 1.0], None, 0.002) == [0.0, 1.0, 1.0]
