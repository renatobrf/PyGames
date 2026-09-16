# Flight Radar — ATC Game

> A 16-bit inspired Air Traffic Control radar game built with Python and Pygame.

---

## Table of Contents

1. [Overview](#overview)
2. [Version History](#version-history)
3. [Requirements](#requirements)
4. [How to Run](#how-to-run)
5. [Gameplay](#gameplay)
   - [Objective](#objective)
   - [Controls](#controls)
   - [Scoring](#scoring)
   - [Game Over](#game-over)
6. [Visual Design](#visual-design)
7. [Architecture](#architecture)
   - [File Structure](#file-structure)
   - [Constants & Configuration](#constants--configuration)
   - [Game State Machine](#game-state-machine)
   - [Aircraft State Machine](#aircraft-state-machine)
   - [Classes](#classes)
   - [Functions](#functions)
   - [Main Loop](#main-loop)
8. [Difficulty Progression](#difficulty-progression)
9. [Color Palette](#color-palette)

---

## Overview

**Flight Radar** is a single-file retro arcade game where the player acts as an air traffic controller. Aircraft appear on the edge of a green phosphor radar display and slowly approach the center. The player must decide — in real time — whether to **accept** each flight for landing or **deny** it and send it on a reroute path. Fail to act in time and the aircraft reaches the center, counting as an incident and deducting points.

The aesthetic is inspired by 16-bit era games and classic CRT radar terminals: green-on-black color scheme, monospaced Courier New font, concentric range rings, a rotating sweep line with phosphor afterglow, and blinking aircraft markers.

---

## Version History

| Version | File | Key addition |
|---|---|---|
| v1 | `flight_radar.py` | Base game — radar, accept/deny, incident counter |
| v2 | `flight_radar_v2.py` | Points system, streak bonuses, score footer bar, `StreakBurst` overlay |
| v3 | `flight_radar_v3.py` | **Game Over** screen when score drops below zero; new-game / quit prompt; `new_game_state()` reset helper |

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
python flight_radar_v3.py
```

The game window opens at **800 × 700** pixels and runs at **60 FPS**.

---

## Gameplay

### Objective

Keep the radar clear and your score above zero. Aircraft spawn on the outer edge of the radar and move toward the center. You must respond to each flight before it reaches the center (0% distance remaining):

- **Accept** → the aircraft is cleared for landing and flies in quickly, then disappears. **+10 pts** (streak multiplier applies).
- **Deny** → the aircraft is rerouted, banking sideways and drifting back out of radar range. **+5 pts**.

If an aircraft reaches the center without being handled, it counts as an **incident** (**−20 pts**, streak reset). If your total score falls below zero, the game ends immediately.

### Controls

| Key | Action |
|---|---|
| `A` or `Enter` | Accept the selected aircraft (clear to land) |
| `D` | Deny the selected aircraft (reroute) |
| `Tab` | Cycle selection to the next approaching aircraft |
| `Q` or `Esc` | Quit the game (also works on the Game Over screen) |

The currently selected aircraft is highlighted in the **flight panel** and marked with a `▶` prefix in the traffic sidebar on the right.

#### Game Over screen controls

| Key | Action |
|---|---|
| `Y` | Start a new game (full reset) |
| `N`, `Esc`, or `Q` | Quit the application |

### Scoring

| Event | Points | Other effect |
|---|---|---|
| Aircraft accepted and landed | **+10** base (+ streak multiplier) | Streak counter +1 |
| Aircraft denied and rerouted | **+5** | Streak unchanged |
| Aircraft reaches center unhandled | **−20** | Streak reset to 0 |
| Every 5 consecutive accepts (streak milestone) | **+25 bonus** | `StreakBurst` banner shown |

The **SCORE** counter is shown in the top-left corner and in the score footer (turns red when negative).  
The **INCIDENTS** counter is shown in the top-right corner (turns red when greater than zero).

### Game Over

> **New in v3**

When your accumulated score drops below **0**, the game transitions to the `GAME_OVER` state:

- Simulation freezes (aircraft are no longer updated).
- A semi-transparent overlay is drawn on top of the frozen radar.
- A full statistics summary is displayed:
  - Final score, time played, cleared, rerouted, incidents, accuracy %, best streak.
- A **blinking prompt** (2 Hz) asks the player to choose:
  - **`[Y]` New Game** — resets all state and starts a fresh session.
  - **`[N]` Quit** — exits the application.

---

## Visual Design

The game simulates the look of an old analog radar terminal:

- **Background**: pure black with a dark green radar disc.
- **Sweep line**: a rotating green line at 1.2 rad/s with a fan-shaped phosphor glow trail behind it.
- **Range rings**: four concentric circles at 25, 50, 75, and 100 NM (nautical miles), labeled in dim green.
- **Crosshairs & compass rose**: N / S / E / W markers around the radar rim.
- **Aircraft markers**: a bright green `+` cross that blinks while approaching; a directional arrow triangle when landing; a dim circle with a ring when rerouting.
- **Phosphor trail**: each aircraft leaves a fading dot trail of up to 18 positions.
- **Flash effects**: expanding ring + text label (`CLEARED +10`, `REROUTED +5`, `INCIDENT!`) plays at the aircraft's position on state change.
- **HUD — top bar**: game title, live score (top-left, red if negative), incident count (top-right), traffic sidebar.
- **HUD — flight panel**: flight data (callsign, altitude, speed, proximity %, bearing), `[A] ACCEPT` and `[D] DENY` buttons, queue count.
- **HUD — score footer**: total score, cleared / rerouted / incidents counters, accuracy bar, streak dots, elapsed time.
- **Streak burst overlay**: full-width golden banner when a streak milestone is reached.
- **Game Over overlay** *(v3)*: dark semi-transparent backdrop, red alert border, stats block, blinking `[Y] / [N]` prompt.

---

## Architecture

### File Structure

```
flight-radar/
├── flight_radar.py          # v1 — base game
├── flight_radar_v2.py       # v2 — points & streak system
├── flight_radar_v3.py       # v3 — Game Over screen (current)
├── doc-flight-radar.md      # This document
└── prompt-flight-radar.txt  # Original design prompt (Portuguese)
```

### Constants & Configuration

Defined at the top of [`flight_radar_v3.py`](flight_radar_v3.py):

| Constant | Value | Description |
|---|---|---|
| `WIDTH`, `HEIGHT` | `800`, `700` | Window dimensions in pixels |
| `FPS` | `60` | Target frame rate |
| `RADAR_CX`, `RADAR_CY` | `400`, `295` | Radar center (screen coordinates) |
| `RADAR_RADIUS` | `270` | Radar circle radius in pixels |
| `CALLSIGNS` | list of 15 | Base callsign pool, randomized per spawn |
| `PTS_ACCEPT` | `10` | Points awarded for a landing |
| `PTS_DENY` | `5` | Points awarded for a reroute |
| `PTS_INCIDENT` | `−20` | Points deducted for an unhandled aircraft |
| `PTS_STREAK` | `25` | Bonus points at each streak milestone |
| `STREAK_MILESTONE` | `5` | Consecutive accepts needed for streak bonus |
| `GAME_PLAYING` | `"playing"` | Normal gameplay state |
| `GAME_OVER` | `"game_over"` | Score < 0 — game over screen active |

### Game State Machine

> **New in v3**

The top-level game session follows a two-state machine managed inside `main()`:

```
GAME_PLAYING ──[score < 0]──► GAME_OVER
GAME_OVER    ──[Y key]──────► GAME_PLAYING  (full reset via new_game_state())
GAME_OVER    ──[N/ESC/Q]───► exit
```

| State | Constant | Behavior |
|---|---|---|
| Playing | `GAME_PLAYING` | Normal simulation and input loop |
| Game Over | `GAME_OVER` | Simulation frozen; overlay rendered; Y/N input only |

### Aircraft State Machine

Each [`Aircraft`](flight_radar_v3.py:78) instance follows a linear state machine:

```
APPROACHING ──[accept]──► LANDING ──► GONE
            ──[deny]───► REROUTING ──► GONE
            ──[timeout]─► GONE  (incident, −20 pts)
```

| State | Constant | Behavior |
|---|---|---|
| Approaching | `STATE_APPROACHING` | Moves toward center at `approach_speed` px/frame |
| Landing | `STATE_LANDING` | Speeds up 3× toward center, then removed |
| Rerouting | `STATE_REROUTING` | Drifts sideways (`reroute_angle_delta`) and moves outward |
| Gone | `STATE_GONE` | Invisible; removed after `ttl` countdown |

### Classes

#### `Aircraft` — [`flight_radar_v3.py:78`](flight_radar_v3.py:78)

Represents a single aircraft on the radar.

| Attribute | Type | Description |
|---|---|---|
| `callsign` | `str` | Randomized ICAO-style flight ID |
| `altitude` | `int` | Random altitude 18,000–39,000 ft |
| `speed` | `int` | Random speed 280–520 kts |
| `angle` | `float` | Current bearing in radians (polar) |
| `dist` | `float` | Distance from radar center in pixels |
| `state` | `str` | Current aircraft state machine state |
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

#### `RadarSweep` — [`flight_radar_v3.py:192`](flight_radar_v3.py:192)

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

#### `ScoreState` — [`flight_radar_v3.py:222`](flight_radar_v3.py:222)

Tracks all scoring and session statistics.

| Attribute | Type | Description |
|---|---|---|
| `points` | `int` | Current total score (can be negative in v3) |
| `cleared` | `int` | Aircraft accepted and landed |
| `rerouted` | `int` | Aircraft denied and rerouted |
| `incidents` | `int` | Aircraft that reached center unhandled |
| `streak` | `int` | Consecutive accepts without an incident |
| `best_streak` | `int` | All-time best streak this session |
| `elapsed` | `float` | Total seconds played |
| `last_delta` | `int` | Last point change value (for float-up animation) |
| `delta_timer` | `float` | How long to display the delta label |

| Method / Property | Description |
|---|---|
| `add_accept()` | Awards `+10` pts (+ streak bonus); increments `cleared`; returns `True` if milestone hit |
| `add_deny()` | Awards `+5` pts; increments `rerouted`; streak unchanged |
| `add_incident()` | Deducts `20` pts with **no floor** (score can go negative); resets streak |
| `update(dt)` | Advances `elapsed` and counts down `delta_timer` |
| `accuracy` *(property)* | `cleared / (cleared + incidents) × 100`, returns `100.0` if no flights handled yet |
| `elapsed_str` *(property)* | Formatted `MM:SS` string |

> **v3 change**: `add_incident()` no longer clamps `points` at `0`. A negative score triggers `GAME_OVER` in the main loop.

---

#### `FlashEffect` — [`flight_radar_v3.py:502`](flight_radar_v3.py:502)

A short-lived expanding ring + label played when aircraft state changes.

| Attribute | Description |
|---|---|
| `x`, `y` | Screen position of the effect |
| `color` | RGB tuple; fades over lifetime |
| `label` | Text drawn above the ring (e.g. `"CLEARED +10"`) |
| `timer` | Starts at `1.0`, decrements at `1.8×` per second |
| `radius` | Starts at `4`, grows at `60 px/s` |

| Method | Description |
|---|---|
| `update(dt)` | Advances `timer` and `radius` |
| `draw(surface, font)` | Renders the fading ring and label |
| `is_dead()` | Returns `True` when `timer ≤ 0` |

---

#### `StreakBurst` — [`flight_radar_v3.py:529`](flight_radar_v3.py:529)

Full-width golden banner that briefly flashes when a streak milestone is reached.

| Attribute | Description |
|---|---|
| `timer` | Seconds remaining for the banner; `0.0` when inactive |
| `message` | Formatted string, e.g. `"★  STREAK ×5!  +25 BONUS  ★"` |

| Method | Description |
|---|---|
| `trigger(streak)` | Arms the burst with a message and sets `timer = 2.2 s` |
| `update(dt)` | Counts down `timer` |
| `draw(surface, font)` | Renders the semi-transparent backing rect and golden text |

---

### Functions

#### `draw_radar_bg(surface, font_small)` — [`flight_radar_v3.py:226`](flight_radar_v3.py:226)

Draws the static radar background:
- Four concentric range rings (25/50/75/100 NM).
- Horizontal and vertical crosshairs.
- Outer border circle in bright green.
- Compass rose labels: **N**, **S**, **E**, **W**.

---

#### `draw_top_bar(surface, fonts, score, aircraft_list, active_idx)` — [`flight_radar_v3.py:309`](flight_radar_v3.py:309)

Draws the top HUD strip:
- **Title**: `"AIR TRAFFIC CONTROL — RADAR v3.0"` centered.
- **Score** (top-left): `PTS: XXXXXX` in gold; turns red when `score.points < 0`.
- **Incidents** (top-right): red when `> 0`.
- **Traffic sidebar**: lists all non-GONE aircraft with callsign + state abbreviation; active aircraft marked with `▶` in amber.

---

#### `draw_flight_panel(surface, fonts, aircraft_list, active_idx)` — [`flight_radar_v3.py:351`](flight_radar_v3.py:351)

Draws the mid-screen flight-info panel:
- Callsign, altitude, speed of the selected aircraft.
- Proximity % and bearing.
- `[A] ACCEPT +10pts` and `[D] DENY +5pts` button widgets.
- Queue count and `[TAB] next` hint.
- **Idle message** when no aircraft are approaching.

---

#### `draw_score_footer(surface, fonts, score)` — [`flight_radar_v3.py:397`](flight_radar_v3.py:397)

Draws the bottom score bar (four columns):

| Column | Content |
|---|---|
| 1 | Total SCORE in large font (gold / red) + floating point-delta label |
| 2 | CLEARED / REROUTED / INCIDENTS counters |
| 3 | ACCURACY percentage + filled progress bar |
| 4 | STREAK multiplier + milestone dot indicators + BEST streak + elapsed TIME |

---

#### `draw_game_over(surface, fonts, score, blink_timer)` — [`flight_radar_v3.py:466`](flight_radar_v3.py:466)

> **New in v3**

Draws the Game Over overlay on top of the frozen radar:
- Semi-transparent black backdrop (`SRCALPHA` surface, alpha 210).
- Red alert border rectangle.
- Large **GAME OVER** title in `RED_ALERT` (52 pt bold).
- `"SCORE DROPPED BELOW ZERO — SECTOR LOST"` subtitle.
- Stats block: final score, time played, cleared, rerouted, incidents, accuracy %, best streak.
- **Blinking prompt** at ~2 Hz: `[Y]  NEW GAME          [N]  QUIT`.
- Dim hint line: `"press Y to restart or N / ESC to exit"`.

`blink_timer` is accumulated real time in seconds; the prompt visibility toggles on `int(blink_timer * 2) % 2 == 0`.

---

#### `new_game_state()` — [`flight_radar_v3.py:541`](flight_radar_v3.py:541)

> **New in v3**

Factory helper that resets **all** mutable session state:

```python
aircraft, effects, score, sweep, streak_burst, spawn_timer, spawn_interval, active_idx
    = new_game_state()
```

- Resets `Aircraft._id_counter` to `0`.
- Creates one initial `Aircraft()`.
- Returns fresh instances of `ScoreState`, `RadarSweep`, `StreakBurst`.
- Sets `spawn_timer = 0.0`, `spawn_interval = 5.0`, `active_idx = 0`.

Called both at startup and when the player presses `Y` on the Game Over screen.

---

#### `main()` — [`flight_radar_v3.py:553`](flight_radar_v3.py:553)

Entry point. Initializes Pygame, builds the font dictionary, and runs the game loop.

---

### Main Loop

Each frame (capped at 60 FPS via `clock.tick`):

```
1. Process events
   ├── QUIT → exit
   │
   ├── [GAME_OVER state]
   │   ├── K_y              → new_game_state(); GAME_PLAYING
   │   └── K_n / K_ESCAPE / K_q → exit
   │
   └── [GAME_PLAYING state]
       ├── K_ESCAPE / K_q   → exit
       ├── K_TAB            → cycle active_idx
       ├── K_a / K_RETURN   → accept selected aircraft (+10 pts, streak)
       └── K_d              → deny selected aircraft  (+5 pts)

2. [GAME_OVER] Render frozen radar + draw_game_over(); skip steps 3–6

3. Spawn logic
   └── if spawn_timer >= spawn_interval and active count < 6
       → append new Aircraft(); decrease spawn_interval (min 2.5 s)

4. Update
   ├── ScoreState.update(dt)
   ├── RadarSweep.update(dt)
   ├── StreakBurst.update(dt)
   ├── Aircraft.update(dt) for each aircraft
   │   └── detect APPROACHING→GONE without input → score.add_incident()
   └── FlashEffect.update(dt) for each effect

5. Prune
   ├── Remove dead Aircraft (is_dead())
   └── Remove dead FlashEffect (is_dead())

6. Check Game Over
   └── if score.points < 0 → game_state = GAME_OVER

7. Draw
   ├── screen.fill(BLACK)
   ├── Radar disc background (DARK_GREEN circle)
   ├── draw_radar_bg()        — rings, crosshairs, compass
   ├── RadarSweep.draw()      — sweep fan + leading line
   ├── Aircraft.draw()        — trails, icons, labels
   ├── FlashEffect.draw()     — expanding rings
   ├── draw_top_bar()         — title, score, incidents, sidebar
   ├── draw_flight_panel()    — flight data + action buttons
   ├── draw_score_footer()    — stats bar
   └── StreakBurst.draw()     — milestone overlay (top layer)
```

---

## Difficulty Progression

The game uses a single escalating parameter:

| Variable | Initial | Minimum | Change per spawn |
|---|---|---|---|
| `spawn_interval` | `5.0 s` | `2.5 s` | `−0.1 s` |

As more aircraft are cleared or rerouted, new ones arrive faster. Up to **6 aircraft** can be active on the radar simultaneously. Individual aircraft also vary in `approach_speed` (0.25–0.55 px/frame), so faster flights give less reaction time.

The **Game Over** condition adds a second pressure axis: every unhandled incident removes 20 points, meaning a run of missed aircraft will end the session regardless of time.

---

## Color Palette

All colors use the **phosphor green** spectrum on black, with gold accents for scores and red for danger:

| Name | RGB | Usage |
|---|---|---|
| `BLACK` | `(0, 0, 0)` | Window background |
| `DARK_GREEN` | `(0, 40, 0)` | Radar disc fill |
| `DIM_GREEN` | `(0, 60, 10)` | Range ring labels, idle text, stat labels |
| `MED_GREEN` | `(0, 100, 20)` | Range rings, crosshairs, rerouting aircraft, separators |
| `GREEN` | `(0, 200, 60)` | Sweep line, outer border ring, accept button border |
| `UI_GREEN` | `(0, 180, 50)` | Compass labels, secondary HUD text |
| `BRIGHT_GREEN` | `(100, 255, 120)` | Approaching aircraft icon, primary HUD text, CLEARED counter |
| `WHITE_GREEN` | `(180, 255, 180)` | Callsign labels on radar |
| `ALERT_GREEN` | `(180, 255, 80)` | Landing aircraft, selected aircraft in sidebar, blink prompt |
| `RED_ALERT` | `(220, 60, 60)` | Deny button, incident counter, Game Over title & border |
| `SCORE_GOLD` | `(255, 215, 50)` | Total score display, positive point delta |
| `SCORE_SILVER` | `(160, 200, 160)` | (reserved) |
| `SCORE_DIM` | `(60, 80, 60)` | Empty streak dots, zero-incident counter |
| `SCORE_RED` | `(200, 50, 50)` | Score display when negative, negative point delta |
| `SCORE_STREAK` | `(255, 180, 0)` | Streak value, milestone dots, StreakBurst banner |

---

*Generated from source: [`flight_radar_v3.py`](flight_radar_v3.py)*
