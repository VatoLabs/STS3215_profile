# Sanity checks for sts3215_profile.py (run: python -m pytest test_profile.py)
import math

import pytest

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


def test_register_edges():
    assert profile_accel(0, 50) == 50 * UNIT  # 0 acts as 50 at the factory cap too
    assert profile_accel(254, 50) == profile_accel(50, 254)  # the lower register wins either way
    assert profile_accel(0, 0) is None and profile_accel(1, 0) is None  # 85 = 0 is off whatever 41 says
    assert profile_accel(1, 254) == UNIT  # smallest setting


def test_max_setting_moving_goal_and_reversal():
    a, dt = profile_accel(254, 254), 0.002
    goals = [math.sin(2 * math.pi * 2 * k * dt) for k in range(1000)] + [-0.5] * 500  # 2 Hz sine, then a jump back
    x = internal_target(goals, a, dt)
    v = [(x[i + 1] - x[i]) / dt for i in range(len(x) - 1)]
    assert max(abs(v[i + 1] - v[i]) / dt for i in range(len(v) - 1)) <= a * (1 + 1e-9)
    assert abs(x[-1] + 0.5) < 1e-6


def test_smallest_setting_still_lands():
    a, dt = profile_accel(1, 254), 0.002
    x = internal_target([0.0] + [-0.3] * 3000, a, dt)  # 0.153 rad/s^2: 2.8 s to cover 0.3 rad
    assert abs(x[-1] + 0.3) < 1e-6
    assert all(-0.3 - 1e-6 <= xi <= 0.0 for xi in x)  # no overshoot (discretisation: < 1e-7 rad)


def test_cap_below_50_and_bad_values():
    assert profile_accel(25, 50) == 25 * UNIT  # measured: 3.5-4.0 rad/s^2 (rule 3.83)
    for bad in [(255, 254), (-1, 254), (254, 300), (12.5, 254), (None, 254)]:
        with pytest.raises((ValueError, TypeError)):
            profile_accel(*bad)
    assert internal_target([], profile_accel(254, 254), 0.002) == []
