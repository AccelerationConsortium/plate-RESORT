# Changelog

All notable changes to this project will be documented in this file.

## [2.0.50] - 2025-10-31
### Added
- `diagnostics/xm430_simple_debug.py`: minimal two-mode (position mode 3, PWM pulse mode 16) script for direct tuning without advanced stall/plateau logic. Provides adjustable profile velocity/accel and current limit in position mode; short escalating PWM pulses (pulse, rest, check) until within tolerance.

### Notes
- Intended for quick manual torque/position experimentation. Use legacy `xm430_debug.py` for comprehensive near-target stall recovery features.

## [2.0.51] - 2025-10-31
### Added
- Utility flags in `xm430_simple_debug.py`: `--reboot` (soft device reboot) and `--motor-data` (single-line telemetry: position, raw current, voltage, temperature).
## [2.0.52] - 2025-10-31
### Changed
- Refactored `xm430_simple_debug.py` to remove CLI flags; now uses in-file `CONFIG` dict for port, baud, ID, action, and tuning values (simpler manual debugging workflow).

### Notes
- Set `CONFIG["ACTION"]` to `position`, `pwm_pulse`, `reboot`, or `data` then run: `python diagnostics/xm430_simple_debug.py`.
- Previous flag-based invocation retained in history; script now focused on rapid edit-run cycles.

## [2.0.53] - 2025-10-31
### Added

### Notes

## [2.0.54] - 2025-10-31
### Added
Added adaptive backoff near target: when a pulse produces a delta > `TOLERANCE * MAX_STEP_FACTOR` and error is within `SWITCH_ERROR`, PWM is reduced by `PWM_BACKOFF_STEP` (bounded by `PULSE_PWM_START`). This prevents large jumps >1.5x tolerance during final approach. Refactored long lines for lint compliance.

## [2.0.55] - 2025-10-31
### Added
- Adaptive backoff + stall detection in two-stage pulse phase (hard-coded factors for initial trial: 1.5 movement factor, 80 PWM backoff, stall after 6 low-motion pulses).
### Changed
- Stage 2 now stops early on stall instead of only hitting max pulses.

## [2.0.56] - 2025-10-31
### Added
- Integrated two-stage precise movement strategy into `PlateResort`: new methods `activate_hotel_precise` and `move_to_angle_precise` perform coarse position move then PWM pulse refinement with adaptive escalation, backoff and stall detection.
- New config keys in `config/defaults.yaml` under `resort:` for tuning: `enable_precise_move`, `switch_error`, `stage1_timeout`, `poll_interval`, `pulse_pwm_start`, `pwm_step`, `pwm_max`, `pulse_duration`, `pulse_rest`, `pulse_max`, `motion_threshold`, `stall_pulses`, `enable_backoff`, `max_step_factor`, `pwm_backoff_step`, `precise_log`.
### Notes
- Legacy `activate_hotel` retained (blind immediate command). Use `activate_hotel_precise` when confirmation within tolerance and controlled near-target approach are required.

## [2.0.57] - 2025-10-31
### Added
- Runtime tuning helpers `show_precise_params()` and `tune_precise(**updates)` to inspect and adjust precise movement parameters without editing YAML.
### Changed
- More conservative fallback defaults in `_precise_cfg` (lower start PWM, slower escalation, slightly larger switch error). Helps prevent aggressive overshoot when user override file lacks new keys.
### Notes
- `tune_precise` modifications are in-memory only; update `~/plate-resort-config/defaults.yaml` to persist across sessions.
## [2.0.58] - 2025-10-31
### Fixed
- Corrected misuse of control table address 32 (Velocity Limit) for torque/current limiting; now writes current limit to address 38 (`ADDR_CURRENT_LIMIT`).
- Ensured profile velocity (addr 112) and optional profile acceleration (addr 108) are re-applied after every operating mode switch in precise movement helper `_set_mode`.
### Changed
- Refactored comment for goal current register to clarify applicability only in Current / Current-based Position modes (0 or 5); harmless when written in Position mode (3).
- Wrapped long lines in `core.py` to satisfy lint width constraints.
### Notes
- Slower Stage 1 positioning can now be reliably tuned via `default_speed` (profile velocity) and `profile_acceleration` since writes persist after mode transitions.
- For further near-target refinement adjust `pulse_pwm_start`, `pwm_step`, and `pwm_backoff_step` in `defaults.yaml` or via `tune_precise()`.

### Notes
- Reboot performs protocol reboot then waits ~0.8s before exit; torque disabled during cleanup.
- Voltage reported as decoded 0.1V units; current is raw value (no mA conversion applied).


## [2.0.49] - 2025-10-30
### Added
- Diagnostics: Finish pulsed torque mode (`--finish-pulse-mode` + related flags) providing discrete short current pulses in finish Current Mode (0) as an alternative to continuous creep. Adaptive escalation of pulse current when motion below threshold; optional restore to holding mode.

### Changed
- Diagnostics: Early stage advancement decoupled from stall logic; `--stage-advance-error` now advances immediately when residual error is between tolerance and threshold (no need to trigger a stall).
- Diagnostics: Simplified stall heuristic (no `--stall-error-threshold`); stall now means no improvement for `--stall-window` while still outside tolerance.
- Diagnostics: Automatic skip of remaining stages when already within tolerance of the final target after completing (or partially completing) an earlier stage (prints `[SKIP]`).

### Removed
- Diagnostics: Deprecated `--stall-error-threshold` argument (behavior superseded by simplified stall rule).

### Added Flags
- `--finish-pulse-mode`, `--finish-pulse-current-start`, `--finish-pulse-current-step`, `--finish-pulse-current-max`, `--finish-pulse-duration`, `--finish-pulse-rest`, `--finish-pulse-motion-threshold`, `--finish-pulse-max-pulses`, `--finish-pulse-abort-error-increase`, `--finish-pulse-restore-mode`.

### Notes
- `--finish-pulse-mode` and `--finish-current-creep` are mutually exclusive; choose one strategy for gentle final seating.
- Use pulses when you want deterministic short torque applications and clear observation windows between them; use creep for continuous low-to-high torque ramp.
- Existing plateau interventions (dither/pulse/surge/nudge/PWM/burst) unchanged.


## [2.0.25] - 2025-10-29

## [2.0.26] - 2025-10-30
## [2.0.27] - 2025-10-30
## [2.0.28] - 2025-10-30
## [2.0.47] - 2025-10-30
### Added
## [2.0.48] - 2025-10-30
### Added
- Diagnostics: Adaptive finish current creep feature (`--finish-current-creep` + related flags) enabling controlled final torque-only approach in Current Mode (0). Starts at low goal current and escalates in steps until motion meets threshold or target within tolerance; optional automatic restore to holding mode (default Mode 5).

### Flags
- `--finish-current-creep`: enable feature when using `--finish-mode 0`.
- `--finish-current-start`, `--finish-current-step`, `--finish-current-interval`, `--finish-current-max` for escalation control.
- `--finish-current-motion-threshold`: minimal angle delta per interval to consider motion; below this escalates current.
- `--finish-current-max-time`: safety cap on creep duration.
- `--finish-current-restore-mode`: restore to positional/holding mode after success (default 5; -1 disables restore).
- `--finish-current-abort-error-increase`: abort if error grows too much indicating runaway.

### Notes
- Use with two-stage move (Mode 3 coarse -> Mode 0 finish + creep) when very gentle final insertion torque is required without overshoot.
- If creep stalls at max current, consider reducing friction or allowing a higher `--finish-current-max` within safe thermal limits.

- Diagnostics: Optional reboot on start (`--reboot-on-start`, wait configurable via `--reboot-wait`) to clear certain transient/latched states before baseline reads.
- Post-reboot immediate hardware error status verification prints cleared (0x00) or persisting bits.

### Guidance
- Reboot helps for transient communication glitches, stale moving flags, or cleared overload bits that have already self-recovered. It does NOT replace a full power cycle for thermal shutdown or persistent overload due to real mechanical jam.
- Prefer power cycle if: temperature remains high (bit 0x02 repeatedly) or overload (0x10) reappears immediately after reboot.

### Notes
- Combine with `--preflight-hw-error-checks` to distinguish freshly latched errors from those that reboot clears.

### Fixed
- Diagnostics: corrected torque enable write (removed invalid unpack of return values in `xm430_debug.py`).

### Notes
- Re-run diagnostics to ensure torque enabling proceeds without ValueError.

## [2.0.29] - 2025-10-30

### Fixed
- Diagnostics: guarded against `None` present current (TypeError on `abs(None)`), corrected per-line current display when value is zero, and replaced summary max current with max absolute current.

### Added
- Peak torque phase reporting (timestamp, angle, error, current) in diagnostics summary.

### Notes
- Run: `python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 --operating-mode 5 --current-limit 1023 --goal-current 300 --profile-velocity 30 --profile-accel 10 --target-angle 190 --tolerance 2.0` and review Peak torque phase line.

### Fixed
- Corrected diagnostic script control table addresses for XM430 (voltage=144, temperature=146, moving=122).
- Added `--tolerance` parameter, early success exit, absolute current display.

### Notes
- Run with: `python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 --operating-mode 5 --current-limit 1023 --goal-current 300 --profile-velocity 30 --profile-accel 10 --target-angle 180 --tolerance 2.0`


### Added
- `diagnostics/xm430_debug.py` direct XM430-210-T motor diagnostic script for manual serial testing (operating mode, current limit, profile velocity/accel, stall heuristic, current/voltage/temp telemetry).

### Notes
- Use to evaluate heavy-load stall behavior outside Prefect. Run: `python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 --operating-mode 5 --goal-current 300 --current-limit 1023 --profile-velocity 50 --profile-accel 10 --target-angle 180`.

### Changed
- Restored legacy blind hotel activation: `activate_hotel` now immediately returns success after issuing goal position without polling / position verification. This matches earlier behavior where activation succeeded even if position feedback intermittently failed.

### Notes
- Remote flows relying on `activate_hotel` will no longer block or fail due to position read errors. Use a future diagnostic flow or `get_motor_health` to inspect position when available.

## [2.0.24] - 2025-10-27
## [2.0.33] - 2025-10-30
## [2.0.34] - 2025-10-30
## [2.0.35] - 2025-10-30
## [2.0.36] - 2025-10-30

### Added
- Diagnostics: High-torque surge escalation (`--surge-enabled`) performing temporary current mode ramp (`--surge-start`, `--surge-max`, `--surge-step`, `--surge-hold`, `--surge-cool`) with safety gates (`--surge-temp-ceil`, `--surge-voltage-floor`) and optional plateau progress reset (`--surge-reset-progress`).

### Changed
- Plateau escalation order: dither -> pulse -> surge -> nudge.

### Notes
- Use surge after verifying temperature remains safely below thermal limits; surge attempts to reach near current limit briefly to overcome static friction.

### Added
- Diagnostics: `--keep-finish-mode` flag plus automatic restoration of original operating mode & torque state after finish-mode run (safety cleanup).
- Diagnostics: Nudge execution telemetry (`nudge_attempted`, `nudge_failed`) with warning-only failure path (no hard abort).

### Changed
- Diagnostics: Plateau nudge errors now emit `[NUDGE-WARN]` and allow script to continue to summary instead of leaving hardware in ambiguous state.

### Notes
- Use `--keep-finish-mode` if you want to stay in the finish operating mode for subsequent manual moves; otherwise mode auto-restores.


### Added
- Diagnostics: Finish-stage operating mode switch (`--finish-mode`) allowing transition (e.g., mode 5 -> 3) near final target once tolerance window reached.
- Diagnostics: Plateau detection (`--plateau-window`, `--plateau-delta`) with proactive in-loop nudge pattern (`--nudge-enabled`, `--nudge-pattern`, `--nudge-wait`) to overcome static friction before overall timeout.

### Changed
- Diagnostics: Final-stage logic now tracks progress separately from earlier stages; nudge executes immediately on plateau instead of only at timeout.

### Notes
- Example usage:
	`python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 \
	 --operating-mode 5 --current-limit 1023 --goal-current 750 \
	 --profile-velocity 70 --profile-accel 20 --pre-angle 95 \
	 --final-profile-velocity 25 --final-profile-accel 10 --target-angle 90 \
	 --ramp-final-current --ramp-step 25 --ramp-interval 1.0 --ramp-max 900 \
	 --ramp-min-error 3.0 --finish-mode 3 --finish-window 8 \
	 --nudge-enabled --nudge-pattern +1,-2,+1 --tolerance 2.0`

### Added
- Diagnostics: Adaptive final-stage current ramp (`--ramp-final-current`) with safety thresholds (temp, voltage) and adjustable parameters (`--ramp-step`, `--ramp-interval`, `--ramp-max`, `--ramp-min-error`, `--ramp-temp-ceil`, `--ramp-voltage-floor`).

### Notes
- Use together with `--pre-angle` and final profile overrides to approach target smoothly, then ramp torque only if small residual error persists.
- Example:
	`python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 \
		 --operating-mode 5 --current-limit 1023 --goal-current 750 \
		 --profile-velocity 70 --profile-accel 20 --pre-angle 95 \
		 --final-profile-velocity 25 --final-profile-accel 10 --target-angle 90 \
		 --ramp-final-current --ramp-step 25 --ramp-interval 1.0 --ramp-max 900 \
		 --ramp-min-error 3.0 --tolerance 2.0`
## [2.0.37] - 2025-10-30

### Added
- Diagnostics: `--plateau-all-stages` allows plateau detection & interventions (dither/pulse/surge/nudge) before final stage.
- Diagnostics: `--ramp-all-stages` permits adaptive current ramp during any stage (previously final stage only).
- Diagnostics: `--stage-advance-error` enables early promotion to next stage during a stall when residual error falls below a specified threshold but is still above tolerance.

### Changed
- Stall heuristic now optionally advances to next stage (if configured) to overcome load-induced stall rather than re-issuing the same intermediate goal indefinitely.
- Plateau intervention block generalized (no longer hard-wired to final stage when `--plateau-all-stages` is supplied).

### Notes
- Example heavy-load run leveraging new flags:
	`python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 \
		--operating-mode 5 --current-limit 1023 --goal-current 800 \
		--profile-velocity 70 --profile-accel 20 --pre-angle 95 \
		--final-profile-velocity 35 --final-profile-accel 12 --target-angle 90 \
		--ramp-final-current --ramp-all-stages --ramp-step 30 --ramp-interval 0.9 --ramp-max 1000 \
		--ramp-min-error 12.0 --plateau-all-stages --plateau-window 2.0 --plateau-delta 0.12 \
		--dither-enabled --pulse-enabled --surge-enabled --surge-start 900 --surge-max 1020 --surge-step 30 \
		--stage-advance-error 15.0 --nudge-enabled --tolerance 2.0`

	Use `--stage-advance-error` cautiously: set it lower than the expected residual error after coarse positioning but high enough to avoid premature advancement when large error remains.
	## [2.0.38] - 2025-10-30

	### Added
	- Diagnostics: `--plateau-cooldown` to suppress repeated plateau intervention spam; waits configurable seconds before re-running full dither/pulse/surge/nudge chain.
	- Diagnostics: Plateau skip reason aggregation in summary (`cooldown_active`, `nudge_disabled_or_already_done`).

	### Changed
	- Ramp abort messages for temperature/voltage now printed once per condition (de-duplicated logging).
	- Plateau detection logic refactored to compute condition + cooldown separately for clarity.

	### Notes
	- If plateau still persists just above tolerance, consider reducing `--tolerance` slightly or increasing `--nudge-amplitude` (future flag) — for now adjust `--nudge-pattern` magnitudes cautiously.
	## [2.0.39] - 2025-10-30

	### Added
	- Diagnostics: PWM proportional nudge feature (`--pwm-nudge-enabled`) switches temporarily to PWM Mode (16) and applies a PWM value proportional to residual error (`--pwm-nudge-kp`, limited by `--pwm-nudge-max`) to break static friction.
	- Safety & control flags: `--pwm-nudge-duration`, `--pwm-nudge-cooldown`, `--pwm-nudge-temp-ceil`, `--pwm-nudge-voltage-floor` for gating and spacing interventions.

	### Changed
	- Plateau intervention sequence optionally ends with PWM proportional nudge if enabled, after surge/nudge steps.
	- Summary now reports PWM nudge execution status and applied PWM value.

	### Notes
	- Suggested initial tuning: `--pwm-nudge-kp 30.0 --pwm-nudge-duration 0.25 --pwm-nudge-cooldown 5.0`.
	- Increase `--pwm-nudge-kp` gradually; watch temperature and hardware error bits (overload) for risk.
	## [2.0.40] - 2025-10-30

	- Diagnostics: Micro nudge feature (`--micro-nudge-enabled`, `--micro-nudge-kp`, `--micro-nudge-max-step`, `--micro-nudge-disable-below-error`, `--micro-nudge-wait`) providing gentle proportional position corrections when near-target plateau persists.

	## [2.0.43] - 2025-10-30
	### Changed
	- Diagnostics: Burst defaults tuned to prior effective parameters (`--burst-start-current 372`, `--burst-max-current 560`, `--burst-hold-max-time 3.0`, unchanged `--burst-current-step 30`, `--burst-motion-threshold 0.25`).
	- Diagnostics: Unlimited burst cycles supported when `--burst-max-cycles <= 0`; script will continue executing short cycles until success, safety abort, or ineffective improvement.

	### Added
	- Per-cycle improvement evaluation remains; unlimited mode respects `--burst-improvement-threshold` for early exit when adequate progress achieved.

	### Notes
	- Use `--burst-max-cycles 0` to allow sustained near-target torque probing without manually setting a high cycle count.
	- Diagnostics: Plateau minimum error gate (`--plateau-min-error`) suppresses heavy escalation (dither/pulse/surge/nudge/PWM) for very small residual errors; micro nudge still allowed.
	Refined burst nudge into short, gated multi-cycle behavior:
	- Added near-target gating flag `--burst-trigger-max-error` (default 15°) so burst only engages after stall close to target.
	- Introduced cycle controls: `--burst-max-cycles`, `--burst-cycle-hold`, `--burst-cycle-gap`, `--burst-ramp-max-steps` for short controlled ramps.
	- Added improvement threshold `--burst-improvement-threshold` to stop early when effective progress achieved.
	- Ensures restoration of operating mode between cycles and safety checks each cycle.
	- Provides per-cycle improvement logging.

	### Changed
	- Plateau block now evaluates `heavy_allowed` based on residual error vs `--plateau-min-error` before executing heavy interventions.
	- Micro nudge execution recorded via skip reason list (`micro_nudge_executed`).

	### Notes
	- Suggested initial micro nudge tuning: `--micro-nudge-kp 0.35 --micro-nudge-max-step 0.8 --plateau-min-error 3.0`.
	- If chatter occurs near target, raise `--micro-nudge-disable-below-error` or increase `--plateau-min-error`.
	## [2.0.41] - 2025-10-30

	### Added
	- Diagnostics: Burst nudge feature (`--burst-nudge-enabled`) implementing a ramp-to-motion-and-hold strategy. Temporarily switches to Current Mode (0), ramps current in steps (`--burst-start-current`, `--burst-current-step`, `--burst-max-current`, `--burst-step-interval`) until a minimal motion threshold (`--burst-motion-threshold`) is detected, then holds current while monitoring residual error (`--burst-hold-max-time`, `--burst-hold-interval`). Safety gating via temperature and voltage (`--burst-temp-ceil`, `--burst-voltage-floor`) and a freeze guard (`--burst-freeze-error`) to avoid unnecessary torque when already near target.

	### Changed
	- Plateau intervention sequence now optionally ends with Burst nudge after PWM nudge when enabled and residual error remains above freeze threshold.
	- Summary reports burst outcome (`Burst nudge executed successfully`, incomplete or failed reason) and safety abort reasons.

	### Notes
	- Suggested initial tuning for gentle correction: `--burst-start-current 120 --burst-current-step 30 --burst-max-current 950 --burst-motion-threshold 0.25 --burst-hold-max-time 4.0`.
	- If ramp reaches max without motion, outcome shows `no_motion`; consider increasing `--burst-current-step` or verifying mechanical load.
	- Use with micro nudge + plateau gating: `--micro-nudge-enabled --plateau-min-error 3.0 --burst-freeze-error 2.5` to reserve burst for moderately stuck cases.
## [2.0.32] - 2025-10-30
## [2.0.44] - 2025-10-30
### Added
- Diagnostics: Communication fault detection. Counts consecutive NaN position reads and performs a one-time soft torque cycle reset after 5 polls; aborts with guidance if still NaN after additional 5.

### Changed
- Summary and inline fault messages clarify when a hard power cycle is recommended.
### Notes
- Use `--show-errors` to surface hardware error status bits; persistent NaN without error bits typically indicates cabling / power / ID mismatch.
- Diagnostics: Two-stage move support via `--pre-angle` then final target.
- Diagnostics: Optional slower final approach overrides with `--final-profile-velocity` and `--final-profile-accel`.
	`python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 \
		 --operating-mode 5 --current-limit 1023 --goal-current 800 \
		 --profile-velocity 70 --profile-accel 20 --pre-angle 95 \

### Added
  - `--burst-expand-increment` raw increment added to the active burst max.
  - `--burst-expand-max` ceiling for escalation (defaults to current limit or 1023).
### Changed
- Burst loop now tracks `active` max current and escalates cautiously after ineffective cycles, respecting thermal/voltage safety offsets (`temp >= burst_temp_ceil - 2`, `voltage < burst_voltage_floor + 0.2` blocks expansion).
- Summary reports final escalated max and number of expansion steps.

### Notes
- Use: `--burst-nudge-enabled --burst-expand-enabled --burst-max-cycles 0` for persistent near-target torque probing with automatic escalation.
- Initial tuning suggestion: keep `--burst-expand-increment` moderate (30–50) to observe thermal response; raise only if repeated cycles remain ineffective.
- If oscillations regress (negative improvement), expansions will trigger when below threshold; consider slightly increasing `--burst-improvement-threshold` to force faster escalation.
## [2.0.31] - 2025-10-30

### Added
- Diagnostics: Hardware Error Status (addr 70) read each poll; optional decoded output with `--show-errors`.
- Diagnostics: Per-line display of `hwErr=0x..` when present; summary lists distinct hardware error codes observed.

### Notes
- Use with `--show-errors` to identify overload (bit 0x10), voltage (0x01), or thermal (0x02) conditions contributing to near-target stall.

## [2.0.30] - 2025-10-30

### Added
- Diagnostics: `--ping` flag to verify motor ID / model number before further operations.
- Diagnostics: `--verbose` flag to print register read failures (result/error codes) for debugging missing telemetry.
- Diagnostics: Early abort if all initial position reads are NaN/None (likely wiring, power, or incorrect ID).

### Notes
- Use `python diagnostics/xm430_debug.py --port COM3 --baud 57600 --id 1 --ping` to confirm connectivity. If ping fails, inspect cabling and power. If ping succeeds but telemetry is None, run with `--verbose` to see failing addresses.

### Added
- README note detailing redeployment options: branch ref vs commit hash (Option B) and clarifying that commit pinning resolved previous missing entrypoint path issues.

### Notes
- Documentation-only change. Prefer `PLATE_RESORT_GIT_COMMIT=$(git rev-parse HEAD)` before `plate-resort-deploy` for reproducible deployments.

## [2.0.23] - 2025-10-27

### Fixed
- `deploy.py` now uses `GitRepository(reference=PLATE_RESORT_GIT_REF)` when no commit SHA is provided instead of cloning a default path blindly, preventing missing entrypoint errors on non-main branches.

### Notes
- Set `PLATE_RESORT_GIT_COMMIT` to pin a specific commit (takes precedence over ref).

## [2.0.22] - 2025-10-27

### Changed
- Major README overhaul: removed duplicate/inconsistent sections; consolidated Quick Start, client setup (interactive vs example script), configuration overrides, troubleshooting table.

### Added
- Explicit documentation of `client-requirements.txt` and `plate_resort/client/env.sh` usage.

### Notes
- No functional code changes; documentation only.

## [2.0.21] - 2025-10-27

### Added
- Restored minimal interactive CLI at `plate_resort/client/interactive.py` supporting local and remote Prefect submissions (commands: connect, activate <hotel>, position, stop, disconnect).

### Notes
- Console script `plate-resort-interactive` now functions again for both modes; remote requires PREFECT_API_URL and PREFECT_API_KEY.

## [2.0.20] - 2025-10-27

### Changed
- Flows (`activate_hotel`, `go_home`, `move_to_angle`, `set_speed`, `get_motor_health`, `get_current_position`, `emergency_stop`) no longer auto-disconnect or release torque after completion. Connection remains active to keep motor locked unless the explicit `disconnect` flow is run.

### Removed
- Deprecated local hardware test scripts and example chaining script from `tests/`.
- Pi-specific venv setup doc (`docs/pi-venv-prefect-setup.md`) superseded by simpler deployment approach.
- Legacy installer scripts (`install.sh`, `bootstrap_pi.sh`) replaced by direct venv + plate-resort-deploy instructions in README.

### Added
- Relocated client example to `plate_resort/client/example_prefect_client.py`.
- Added `plate_resort/client/env.sh` for quick environment variable export.

### Notes
- Ensures motor holds position continuously between operations. Use `disconnect` flow to intentionally release torque and close port.


## [2.0.19] - 2025-10-27

### Changed
- Consolidated client examples into `tests/example_prefect_client.py` demonstrating sequential hotel activation (A→D) with completion waits after each activation.
- Removed older verbose scripts (`test_orchestrator_connect_activate.py`, `example_chain_hotels.py`).

### Notes
- Waiting is optional; core orchestrator functions remain non-blocking unless `orchestrator.wait()` is invoked.

## [2.0.18] - 2025-10-27

### Added
- `orchestrator.wait(flow_run)` helper for optional blocking until a flow run reaches a final state (polling Prefect Cloud).
- Example chaining script `tests/example_chain_hotels.py` demonstrating sequential hotel activation (A→D) in blocking and non-blocking modes.

### Notes
- Non-blocking behavior remains default; blocking is opt-in for safety-critical sequences.
- Minimal example script for connect + activate remains unchanged.

## [2.0.17] - 2025-10-27

### Changed
- Cleaned and refocused `README.md` on Prefect Cloud orchestration: clarified remote workflow submission uses Prefect deployments and the Pi process worker; removed legacy REST/keygen notes section.
- Added explicit references to setup scripts (`install.sh`, `bootstrap_pi.sh`) and systemd unit usage for persistent worker.

### Notes
- Environment override `PLATE_RESORT_POOL` documented; systemd unit and installer continue to auto-deploy when Prefect env vars are present.
## [2.0.5] - 2025-10-16
## [2.0.6] - 2025-10-16
## [2.0.11] - 2025-10-21

## [2.0.12] - 2025-10-21

## [2.0.13] - 2025-10-21

## [2.0.14] - 2025-10-21

## [2.0.15] - 2025-10-21

### Fixed
- Corrected `GitRepository` initialization (uses `url=` not `repo_url=`) and added
	local path presence warning to help diagnose layout mismatches.

### Notes
- Set `PLATE_RESORT_GIT_COMMIT` to a commit containing `plate-resort-multiple/plate_resort/workflows/flows.py` before redeploy.

### Added
- Commit pinning support in `deploy.py` via `PLATE_RESORT_GIT_COMMIT` (uses GitRepository storage).

### Changed
- Improved warnings when a commit SHA is not supplied (falls back to default branch).

### Notes
- For reproducible deployments: `export PLATE_RESORT_GIT_COMMIT=$(git rev-parse HEAD)` then run `plate-resort-deploy`.

### Fixed
- Corrected Prefect Cloud deployment entrypoint path to include top-level folder
	`plate-resort-multiple/` so remote cloning resolves `flows.py`.

### Notes
- Redeploy with `plate-resort-deploy` to register fixed entrypoints.

### Added
- Remote Git repository source in `deploy.py` using `flow.from_source` to satisfy Prefect Cloud requirement for image or storage without building a container image.

### Changed
- Deployment script now prints git ref (env `PLATE_RESORT_GIT_REF`, default `main`).

### Notes
- Use `export PLATE_RESORT_GIT_REF=<branch-or-tag>` before `plate-resort-deploy` to pin a version.
- No container image needed; worker clones repo directly.

### Fixed
- Removed unsupported `entrypoint` argument from `Flow.deploy` calls (Prefect 3.4.23 API does not accept it).

### Notes
- Run `plate-resort-deploy` again to register flows without error.

## [2.0.16] - 2025-10-23

### Notes
- Operational status: the persistent worker and key deployments (connect, activate-hotel) are exercising correctly in Prefect Cloud — activation and connection flows submit and run as expected.
- Known issue: `get-position` has intermittently crashed in a small number of runs (observed as CRASHED). This is documented and intentionally left unfixed for now; core functionality (connect, activate-hotel) prioritized.


## [2.0.10] - 2025-10-21

### Fixed
- `deploy.py` now handles Prefect Flow objects correctly (uses `flow.fn` instead of passing Flow object to `inspect.getsourcefile`), preventing TypeError during deployment.

### Notes
- Re-run `plate-resort-deploy` after upgrading to register deployments successfully.

## [2.0.9] - 2025-10-21

### Changed
- `PlateResort.connect` now accepts optional overrides: `device`, `baudrate`, `motor_id` for flow parameter pass-through.

### Removed
- Console script entries for deleted artifacts (`plate-resort-demo`, `plate-resort-update`).

### Notes
- Function-based Prefect flows can now supply connection parameters safely without signature mismatch crashes.

## [2.0.8] - 2025-10-21

### Removed
- Legacy artifacts: `plate_resort/utils/keygen.py`, `plate_resort/utils/update.py`, `plate_resort/client/demo.py`, temporary `test_counter` Prefect flow method, duplicate `is_connected`.
- Legacy config search path entry for `resort_config.yaml`.

### Changed
- `.gitignore` now ignores `archived/`, `archived_gui/`, and `verify_prefect.py` (archives retained locally).
- Clarified hotel angle computation comment in `defaults.yaml`.
- Consolidated single `is_connected` method.

### Notes
- Archives preserved for reference but excluded from change tracking; consider moving to separate branch in future.

## [2.0.7] - 2025-10-16

### Fixed
- Deployment failures due to Prefect attempting to read a non-existent script path (`/home/pi/plate_resort/core.py`). Added explicit module entrypoints in `deploy.py` so flows are resolved from `plate_resort.workflows.flows:<function>` rather than inferred file paths.

### Added
- Deployment output now prints each flow's entrypoint string along with s  Stored in directory: /tmp/pip-ephem-wheel-cache-8mgnby2f/wheels/0b/aa/c0/11eecf10bed573525c496e7254c0e4a38ec0a80e991cc2e583
Successfully built plate-resort
Installing collected packages: pyserial, websockets, uvloop, urllib3, typing-extensions, sniffio, pyyaml, python-dotenv, idna, httptools, h11, dynamixel-sdk, click, charset_normalizer, certifi, annotated-types, uvicorn, typing-inspection, requests, pydantic-core, anyio, watchfiles, starlette, pydantic, fastapi, plate-resort
Successfully installed annotated-types-0.7.0 anyio-4.11.0 certifi-2025.10.5 charset_normalizer-3.4.4 click-8.3.0 dynamixel-sdk-3.8.4 fastapi-0.119.1 h11-0.16.0 httptools-0.7.1 idna-3.11 plate-resort-2.0.0 pydantic-2.12.3 pydantic-core-2.41.4 pyserial-3.5 python-dotenv-1.1.1 pyyaml-6.0.3 requests-2.32.5 sniffio-1.3.1 starlette-0.48.0 typing-extensions-4.15.0 typing-inspection-0.4.2 urllib3-2.5.0 uvicorn-0.38.0 uvloop-0.22.1 watchfiles-1.1.1 websockets-15.0.1
-bash: plate-resort-deploy: command not found
-bash: prefect: command not found
-bash: prefect: command not foundource file.

### Notes
- If stale `deploy.py` persists, fully uninstall (`pip uninstall -y plate-resort`), remove any `plate_resort*` directories in the venv `site-packages`, then reinstall with `--force-refresh`.


### Added
- `install.sh` flags: `--force-refresh` (delete venv + no pip cache), `--ref <git-ref>` (override branch/tag/commit for install).

### Changed
- Installer now prints the git ref used for clarity.
- Force refresh bypasses wheel and HTTP caches to ensure latest remote commit is fetched.

### Notes
- Use `--force-refresh` when suspecting stale artifacts or cached wheels.
- `--ref` enables pinning to a release tag or commit SHA for reproducible setups.


### Added
- Debug instrumentation in `plate_resort.workflows.deploy` to print source file path for each flow function during deployment.

### Fixed
- Began addressing Prefect deployment import path mismatch (`FileNotFoundError: /home/pi/plate_resort/core.py`). The package installs under `site-packages/plate_resort/` but Prefect attempted to load a filesystem path as if it were a loose script. Debug output will help confirm correct `site-packages` path on the Raspberry Pi.

### Notes
- If Prefect still resolves `/home/pi/plate_resort/core.py`, ensure the virtual environment has the package installed (not just a partial copy) and that `plate_resort` is not shadowed by a directory named `plate_resort` in `$HOME`. Remove/rename any stray `$HOME/plate_resort/` directory to avoid import shadowing.

## [2.0.4] - 2025-10-16

### Removed
- Orphaned `plate-resort-keygen` console script entry from `pyproject.toml` (legacy REST/key generation utility fully retired).

### Changed
- Updated `README.md` to reflect Prefect-only architecture and environment variable based authentication (removed residual keygen / REST references).
 - Simplified `install.sh`; now auto-deploys flows and starts worker when Prefect env vars are present.
 - Bumped package version to 2.0.4.

### Notes
- Key generation is no longer part of the workflow; use Prefect Cloud API credentials via environment variables.

## [2.0.3] - 2025-10-16

### Added
- `bootstrap_pi.sh` script for end-to-end fresh Raspberry Pi setup (clone, venv, deploy Prefect flows, start worker).
- `verify_prefect.py` diagnostic script to confirm Prefect Cloud connectivity, work pool presence, deployments, and recent flow runs.

### Changed
- Pinned Prefect dependency to `prefect==3.4.23` for stable flow deployment behavior.

### Notes
- Future Prefect upgrades should edit pin deliberately; run `verify_prefect.py` after any upgrade.

## [2.0.1] - 2025-10-15

### Fixed
- Resolved Prefect Cloud flow crash (SignatureMismatchError) by removing extraneous parameters from remote `connect` deployment submission.
- Updated `orchestrator.connect()` to call `run_deployment(name="connect/connect")` without a parameter dict (method flow expects only `self`).

### Notes
- Other flows (activate-hotel, move-to-angle, etc.) retain parameters matching their method signatures.
- No breaking API changes; remote client now successfully submits `connect` without crashing.

## [2.1.0] - 2025-01-XX

## [2.0.2] - 2025-10-15

### Changed
- Removed `@flow` decorators from `PlateResort` class methods to eliminate signature mismatches.
- Deployments now source only function-based flows in `plate_resort/workflows/flows.py`.
- `deploy.py` refactored to use explicit function list (`FUNCTION_FLOWS`).
- `orchestrator.connect` restored to accept device/baud/motor parameters for the function flow.

### Fixed
- Resolved repeated CRASHED flow runs caused by method-based deployments passing unexpected parameters.

### Notes
- Class still usable locally; Prefect orchestration isolated to stateless function flows.


### Added
- Prefect v3 integration for workflow orchestration
- `prefect_flows/device.py` - Prefect flows for device control
- `prefect_flows/orchestrator.py` - Remote flow execution functions
- `prefect_flows/README.md` - Setup and usage documentation

### Changed
- Added Prefect>=3.0.0 to dependencies
- REST API remains available but Prefect is now the recommended approach

### Notes
- Prefect provides better observability, retry logic, and async execution
- No breaking changes - REST API still functional for backward compatibility

## [2.0.0] - 2025-10-07

### 🎉 Major Release: Pip Package + Automatic Setup

**BREAKING CHANGES:**
- Complete transformation to pip-installable package
- Simplified installation and usage
- Archived all legacy installers

### 🆕 New Package Structure
- **pip installable**: `pip install git+https://github.com/...`
- **Command line tools**: `plate-resort-server`, `plate-resort-client`, `plate-resort-setup`
- **Professional package**: `plate_resort` Python package
- **Automatic setup**: System dependencies, USB permissions, API keys

### ✨ New Features
- One-line installation with automatic setup
- Command-line tools for server and client
- Automatic USB permissions and system configuration
- Professional Python package structure
- pip-based dependency management

### 🗂️ Archived Components
- Legacy bash installers (install.sh, update.sh)
- Standalone server/ and client/ directories
- Manual setup scripts and GUI components
- All deprecated files moved to archived/

### 🔧 Installation Methods
- **Recommended**: `curl ... | bash` (pip + auto-setup)
- **Manual**: `pip install ...` + `plate-resort-setup`
- **Development**: `pip install -e .` for local development

### 📦 Package Contents
- `plate_resort.core` - Motor control logic
- `plate_resort.server` - FastAPI REST API
- `plate_resort.client` - Client library and CLI
- `plate_resort.setup` - System setup automation
- `plate_resort.keygen` - API key management

### 🎯 Usage Simplification
- **Server**: `plate-resort-server` (instead of bash scripts)
- **Client**: `plate-resort-client --host IP` (consistent CLI)
- **Setup**: `plate-resort-setup` (automated system config)
- **Keys**: `plate-resort-keygen` (secure key generation)

### 🚀 Deployment Ready
- Works on any Python 3.8+ system
- Automatic Raspberry Pi detection and setup
- Professional dependency management
- Clean separation of server/client concerns

## [1.4.0] - 2025-10-07 (Archived)

### Removed
- Docker references and configuration
- Raspberry Pi specific deployment scripts

### Changed
- Simplified deployment approach
- Direct Python execution without containers

### Added
- CHANGELOG.md for tracking version history
- .gitignore file to prevent cache/temp files in repo

### Removed
- Redundant GUI implementations (gui.py, touchscreen_app.py, app.py)
- Redundant launcher scripts and duplicate implementations
- Duplicate test file from root directory (dxl_keyboard_test.py)
- Python cache directories (__pycache__)

### Changed
- Updated README.md to reflect cleaned project structure
- Simplified file organization following copilot-instructions

## [1.2.0] - 2025-09-10

### Added
- Disconnect and reconnect functionality to web API endpoints
- Connection control buttons in web interface (Disconnect/Reconnect)
- `is_connected()` method to PlateResort class for connection status checking
- Enhanced error handling for connection states
- Active hotel display logic improvements

### Fixed
- Emergency stop recovery - system no longer freezes after emergency stop
- Active hotel display now correctly shows current hotel (A, B, C, D, Home, Moving)
- Connection state management and status reporting

## [1.1.0] - 2025-09-10

### Added
- Professional web-based GUI with Bootstrap styling
- Fullscreen support optimized for 7" touchscreen (800x480)
- Live motor health monitoring with real-time updates
- Debug panel with live data logging
- Simplified deployment with automated dependency management
- Automated startup scripts and desktop integration
- Clean repo structure with organized test files

### Changed
- Migrated from Tkinter to Flask web-based GUI
- Moved all test files to `test_scripts/` directory
- Simplified deployment to single web GUI service
- Updated documentation for new architecture

### Removed
- Legacy GUI implementations (gui.py, touchscreen_app.py)
- Duplicate launcher scripts
- Emoji usage for professional lab environment

## [1.0.0] - 2025-09-10

### Added
- Initial PlateResort class with YAML configuration
- Dynamixel motor control with health monitoring
- Hotel position management (A, B, C, D)
- Emergency stop functionality
- Basic motor health reporting
- Raspberry Pi deployment scripts
- Raspberry Pi deployment scripts
