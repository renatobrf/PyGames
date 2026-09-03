# Flight Radar — ATC Game

> A 16-bit inspired Air Traffic Control radar game built with Python and Pygame.

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [How to Run](#how-to-run)
4. [Gameplay](#gameplay)
   - [Objective](#objective)
   - [Controls](#controls)
   - [Scoring](#scoring)
5. [Visual Design](#visual-design)
6. [Architecture](#architecture)
   - [File Structure](#file-structure)
   - [Constants & Configuration](#constants--configuration)
   - [State Machine](#state-machine)
   - [Classes](#classes)
   - [Functions](#functions)
   - [Main Loop](#main-loop)
7. [Difficulty Progression](#difficulty-progression)
8. [Color Palette](#color-palette)

---

## Overview

**Flight Radar** is a single-file retro arcade game where the player acts as an air traffic controller. Aircraft appear on the edge of a green phosphor radar display and slowly approach the center. The player must decide — in real time — whether to **accept** each flight for landing or **deny** it and send it on a reroute path. Fail to act in time and the aircraft reaches the center, counting as an incident.

The aesthetic is inspired by 16-bit era games and classic CRT radar terminals: green-on-black color scheme, monospaced Courier New font, concentric range rings, a rotating sweep line with phosphor afterglow, and blinking aircraft markers.

---

## Requirements

| Dependency | Version |
|---|---|
| Python | 3.10 or newer |
| Pygame / pygame-ce | 2.x |

Install Pygame if not already present:

```bash
pip install pygame
# or for pygame-ce
pip install pygame-ce
```

---

## How to Run

```bash
cd flight-radar
python flight_radar.py
```

The game window opens at **800 × 650** pixels and runs at **60 FPS**.

---

## Gameplay

### Objective

Keep the radar clear. Aircraft spawn on the outer edge of the radar and move toward the center. You must respond to each flight before it reaches the center (0% distance remaining):

- **Accept** → the aircraft is cleared for landing and flies in quickly, then disappears.
- **Deny** → the aircraft is rerouted, banking sideways and drifting back out of radar range.

If an aircraft reaches the center without being handled, it counts as an **incident**.

### Controls

| Key | Action |
|---|---|
| `A` or `Enter` | Accept the selected aircraft (clear to land) |
| `D` | Deny the selected aircraft (reroute) |
| `Tab` | Cycle selection to the next approaching aircraft |
| `Q` or `Esc` | Quit the game |

The currently selected aircraft is highlighted in the **bottom HUD panel** and marked with a `▶` prefix in the traffic sidebar on the right.

### Scoring

| Event | Effect |
|---|---|
| Aircraft accepted and landed | **+1 Cleared** |
| Aircraft denied and rerouted | No score change |
| Aircraft reaches center unhandled | **+1 Incident** |

The **CLEARED** counter is shown in the top-left corner.  
The **INCIDENTS** counter is shown in the top-right corner (turns red when greater than zero).

---

## Visual Design

The game simulates the look of an old analog radar terminal:

- **Background**: pure black with a dark green radar disc.
- **Sweep line**: a rotating green line at 1.2 rad/s with a fan-shaped phosphor glow trail behind it.
- **Range rings**: four concentric circles at 25, 50, 75, and 100 NM (nautical miles), labeled in dim green.
- **Crosshairs & compass rose**: N / S / E / W markers around the radar rim.
- **Aircraft markers**: a bright green `+` cross that blinks while approaching; a directional arrow triangle when landing; a dim circle with a ring when rerouting.
- **Phosphor trail**: each aircraft leaves a fading dot trail of up to 18 positions.
- **Flash effects**: expanding ring + text label (`CLEARED`, `REROUTED`, `INCIDENT!`) plays at the aircraft's position on state change.
- **HUD panel**: a dark green strip at the bottom of the screen displays flight data, action buttons, and queue size.
- **Traffic sidebar**: top-right of the radar area lists all active aircraft with their callsign and state.

---

## Architecture

### File Structure

```
flight-radar/
├── flight_radar.py          # Complete game — single file
└── prompt-flight-radar.txt  # Original design prompt (Portuguese)
```

### Constants & Configuration

Defined at the top of [`flight_radar.py`](flight_radar.py):

| Constant | Value | Description |
|---|---|---|
| `WIDTH`, `HEIGHT` | `800`, `650` | Window dimensions in pixels |
| `FPS` | `60` | Target frame rate |
| `RADAR_CX`, `RADAR_CY` | `400`, `295` | Radar center (screen coordinates) |
| `RADAR_RADIUS` | `280` | Radar circle radius in pixels |
| `CALLSIGNS` | list of 10 | Base callsign pool, randomized per spawn |

### State Machine

Each [`Aircraft`](flight_radar.py:46) instance follows a linear state machine:

```
APPROACHING ──[accept]──► LANDING ──► GONE
            ──[deny]───► REROUTING ──► GONE
            ──[timeout]─► GONE  (incident)
```

| State | Constant | Behavior |
|---|---|---|
| Approaching | `STATE_APPROACHING` | Moves toward center at `approach_speed` px/frame |
| Landing | `STATE_LANDING` | Speeds up 3× toward center, then removed |
| Rerouting | `STATE_REROUTING` | Drifts sideways (`angle_delta`) and moves outward |
| Gone | `STATE_GONE` | Invisible; removed after `ttl` countdown |

### Classes

#### `Aircraft` — [`flight_radar.py:46`](flight_radar.py:46)

Represents a single aircraft on the radar.

| Attribute | Type | Description |
|---|---|---|
| `callsign` | `str` | Randomized ICAO-style flight ID |
| `altitude` | `int` | Random altitude 18,000–39,000 ft |
| `speed` | `int` | Random speed 280–520 kts |
| `angle` | `float` | Current bearing in radians (polar) |
| `dist` | `float` | Distance from radar center in pixels |
| `state` | `str` | Current state machine state |
| `approach_speed` | `float` | Pixels per frame toward center (0.25–0.55) |
| `reroute_angle_delta` | `float` | Angular drift rate when rerouting |
| `trail` | `list[tuple]` | Up to 18 past (x, y) positions for the phosphor trail |
| `blink_timer` | `float` | Drives the blinking animation while approaching |
| `ttl` | `float` | Time-to-live in seconds once in GONE state |

| Method | Description |
|---|---|
| `_update_pos()` | Converts polar `(angle, dist)` to Cartesian `(x, y)` |
| `polar_pos()` | Returns current `(x, y)` screen position |
| `update(dt)` | Advances position and trail each frame; handles state transitions |
| `accept()` | Transitions `APPROACHING → LANDING` |
| `deny()` | Transitions `APPROACHING → REROUTING` |
| `is_dead()` | Returns `True` when state is GONE and TTL has expired |
| `draw(surface)` | Renders trail, aircraft icon, and callsign label |

---

#### `RadarSweep` — [`flight_radar.py:192`](flight_radar.py:192)

Animates the rotating radar sweep line and its phosphor glow fan.

| Attribute | Description |
|---|---|
| `angle` | Current sweep angle in radians, incremented each frame |
| `speed` | Rotation speed: `1.2` rad/s |

| Method | Description |
|---|---|
| `update(dt)` | Advances `angle` by `speed * dt`, wraps at 2π |
| `draw(surface)` | Draws 30-step fan polygon trail + bright leading line |

---

#### `FlashEffect` — [`flight_radar.py:347`](flight_radar.py:347)

A short-lived expanding ring + label played when aircraft state changes.

| Attribute | Description |
|---|---|
| `x`, `y` | Screen position of the effect |
| `color` | RGB tuple; fades over lifetime |
| `label` | Text drawn above the ring (e.g. `"CLEARED"`) |
| `timer` | Starts at `1.0`, decrements at `1.8×` per second |
| `radius` | Starts at `4`, grows at `60 px/s` |

| Method | Description |
|---|---|
| `update(dt)` | Advances `timer` and `radius` |
| `draw(surface, font)` | Renders the fading ring and label |
| `is_dead()` | Returns `True` when `timer ≤ 0` |

---

### Functions

#### `draw_radar_bg(surface, font_small)` — [`flight_radar.py:231`](flight_radar.py:231)

Draws the static radar background:
- Four concentric range rings (25/50/75/100 NM).
- Horizontal and vertical crosshairs.
- Outer border circle in bright green.
- Compass rose labels: **N**, **S**, **E**, **W**.

#### `draw_hud(surface, fonts, aircraft_list, active_idx, score, misses)` — [`flight_radar.py:261`](flight_radar.py:261)

Draws the full HUD overlay:
- **Top bar**: game title, CLEARED count (top-left), INCIDENTS count (top-right).
- **Bottom panel**: flight data (callsign, altitude, speed, proximity %, bearing), `[A] ACCEPT` and `[D] DENY` buttons, queue count.
- **Traffic sidebar**: scrollable list of all active aircraft with their current state, active one marked with `▶`.
- **Idle message**: shown when no aircraft are approaching.

#### `main()` — [`flight_radar.py:376`](flight_radar.py:376)

Entry point. Initializes Pygame, creates fonts, and runs the game loop.

---

### Main Loop

Each frame (capped at 60 FPS via `clock.tick`):

```
1. Process events
   ├── QUIT / K_q / K_ESCAPE → exit
   ├── K_TAB                 → cycle active_idx
   ├── K_a / K_RETURN        → accept selected aircraft
   └── K_d                   → deny selected aircraft

2. Spawn logic
   └── if spawn_timer >= spawn_interval and active count < 6
       → append new Aircraft(); decrease spawn_interval (min 2.5 s)

3. Update
   ├── RadarSweep.update(dt)
   ├── Aircraft.update(dt) for each aircraft
   │   └── detect APPROACHING→GONE without input → misses++
   └── FlashEffect.update(dt) for each effect

4. Prune
   ├── Remove dead Aircraft (is_dead())
   └── Remove dead FlashEffect (is_dead())

5. Draw
   ├── screen.fill(BLACK)
   ├── Radar disc background (DARK_GREEN circle)
   ├── draw_radar_bg()   — rings, crosshairs, compass
   ├── RadarSweep.draw() — sweep fan + leading line
   ├── Aircraft.draw()   — trails, icons, labels
   ├── FlashEffect.draw()— expanding rings
   └── draw_hud()        — panels, buttons, sidebar
```

---

## Difficulty Progression

The game uses a single escalating parameter:

| Variable | Initial | Minimum | Change per spawn |
|---|---|---|---|
| `spawn_interval` | `5.0 s` | `2.5 s` | `−0.1 s` |

As more aircraft are cleared or rerouted, new ones arrive faster. Up to **6 aircraft** can be active on the radar simultaneously. Individual aircraft also vary in `approach_speed` (0.25–0.55 px/frame), so faster flights give less reaction time.

---

## Color Palette

All colors use the **phosphor green** spectrum on black, with a single red accent for alerts:

| Name | RGB | Usage |
|---|---|---|
| `BLACK` | `(0, 0, 0)` | Background |
| `DARK_GREEN` | `(0, 40, 0)` | Radar disc fill |
| `DIM_GREEN` | `(0, 60, 10)` | Range ring labels, idle text |
| `MED_GREEN` | `(0, 100, 20)` | Range rings, crosshairs, rerouting aircraft |
| `GREEN` | `(0, 200, 60)` | Sweep line, outer border ring, accept button border |
| `UI_GREEN` | `(0, 180, 50)` | Compass labels, secondary HUD text |
| `BRIGHT_GREEN` | `(100, 255, 120)` | Approaching aircraft icon, primary HUD text |
| `WHITE_GREEN` | `(180, 255, 180)` | Callsign labels |
| `ALERT_GREEN` | `(180, 255, 80)` | Landing aircraft, selected aircraft in sidebar |
| `RED_ALERT` | `(220, 60, 60)` | Deny button, incident counter |

---

*Generated from source: [`flight_radar.py`](flight_radar.py)*
