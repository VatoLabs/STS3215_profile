# The STS3215 tracks its own acceleration profile, not your goal

Vato Labs, measured 30 Oct to 1 Nov 2026. First bench measurement: 30 Oct 2026.

![A step on a load never fitted](accel_profile.png)

*Goal as logged; the single point at 29° is one intermediate logged sample of the step.*

**What.** The STS3215 servo in the SO-101 arm does not drive its position loop straight to the goal you send. It
moves an internal target toward the goal at constant acceleration, braking in time to stop on it, and the loop
follows that target. The acceleration comes from two registers:

**a = 100 steps/s² × min(Acceleration, Maximum_Acceleration)**, 0 acting as 50. One unit is 0.153 rad/s².
LeRobot writes 254 to both, which gives 38.96 rad/s².

**Evidence.** BAM's STS3215 model structure (Rhoban), fitted by us to BAM's public 12 V logs before we had any
bench data, and never fitted to the bench. Scored by mean absolute position error on a single-servo rod bench,
over BAM's four powered trajectories. LeRobot's arm settings (P=16, Acceleration 254) unless stated. Loads are
gravity torques.

| Data | Goal as sent | Through the profile |
|---|---|---|
| 5 loads 0-0.86 N·m (12 runs each) | 18.1-21.3 mrad | **6.5-10.1 mrad** |
| Held-out load 0.58 N·m (12 runs) | 18.1 | **7.1** (stock Menagerie: 68.3) |
| 0.19 N·m, P=32, Maximum_Acceleration 50 (5 runs, 5 trajectories) | 93.3 | **8.0** |

It is not just latency: the best constant delay on the goal as sent (20 ms) reaches only 15.5-17.4 mrad on the
same runs. Refitting the model on the five loads gives 5.2 mrad (0.30°) on the held-out one.

**Measured vs assumed.** The following are measured:

- Steps at cap 50 accelerate and brake at 6.6-7.0 rad/s² against 7.7 predicted. The velocity profile is a symmetric triangle with no cruise phase.
- Acceleration 0 behaves as 50 at both caps.
- The min() cap holds.

At 254 the motor saturates before the profile peaks, so only the start of each move shows it. Re-planning toward a moving goal is assumed, and it is our worst case. We never set a speed limit, so no cruise phase was tested.

**Fix.** Pass your goals through [`sts3215_profile.py`](sts3215_profile.py) (20 lines) and simulate the servo
tracking the result.

**Limits.** One servo so far; five more are being tested over the coming days. Firmware 3.10, one gain (P=16),
one day, on a bench rather than the arm. The held-out load lies inside the fitted range. The pass mark for it
was set after the five loads were run and before it was, and the one trajectory that switches torque off (free
fall, not modelled: 74 mrad) was excluded at that point. The full per-arm calibration tool is in development at Vato Labs.

**Credits.**
- [MetalSim](https://github.com/pulipakaa24/MetalSim) wrote down the same formula on 31 Oct and marked it inferred.
- [sts3215-firmware](https://github.com/0o8o0-blip/sts3215-firmware) implements a trapezoid profile and attributes the response delay to it.
- [BAM](https://github.com/Rhoban/bam) (arXiv 2410.08650) supplied the servo model.
- [LeRobot](https://github.com/huggingface/lerobot) sets the arm's registers.

## Use

```python
from sts3215_profile import profile_accel, internal_target
a = profile_accel(254, 254)                   # 38.96 rad/s^2, LeRobot's setting
target = internal_target(goals, a, dt=0.002)  # feed this to your simulated servo instead of the goals
```

## Cite

See [`CITATION.cff`](CITATION.cff). MIT licence.
