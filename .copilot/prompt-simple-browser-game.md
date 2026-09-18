# 🌐 Simple Browser Game — Prompt Collection

A set of ready-to-use prompts for building simple browser games using **vanilla HTML5, CSS3, and JavaScript** (no frameworks, no bundlers — just open the file in a browser and play).

Each prompt is self-contained and produces a single `.html` file. The output style mirrors the retro/indie spirit of this repository.

---

## How to Use

Copy any prompt below and paste it into a Bob session. The expected output file is shown at the top of each prompt.

---

## 🕹️ Example 1 — Asteroid Dodger

> **Output:** `browser-asteroid-dodger/index.html`

```
Help me build a simple browser game called "Asteroid Dodger" using a single HTML file
with vanilla JavaScript and the HTML5 Canvas API. No external libraries.

Game concept:
- The player controls a small spaceship at the bottom of the screen
- Asteroids fall from the top at increasing speed
- The player moves left/right to avoid them (arrow keys or A/D)
- The game tracks a score (seconds survived) shown in the top-right corner
- A high score is kept in localStorage and displayed on the Game Over screen
- Difficulty ramps up every 10 seconds (more asteroids, faster fall speed)

Visual style:
- Dark space background (near-black)
- Spaceship drawn with Canvas shapes (no image assets required)
- Asteroids are irregular grey/brown polygons drawn procedurally
- Retro pixel font via Google Fonts ("Press Start 2P")
- Minimal colour palette: white, grey, orange (thrust glow), red (explosion)

Screens:
1. Start screen — title, high score, "Press SPACE or Tap to Start" prompt
2. Game screen — live score (top right), lives indicator (top left, 3 lives)
3. Game Over screen — final score, high score, restart button

Controls:
- Desktop: ← / → or A / D to move; SPACE to start / restart
- Mobile: left/right tap zones on screen to move (touch events)

Additional requirements:
- Invincibility frames (1.5 s) after a hit, with a flicker effect on the ship
- Simple particle explosion when an asteroid is destroyed or hits the ship
- Background star field (50 static stars, subtle parallax at 0.3× ship speed)
- Responsive canvas: fills the viewport, capped at 480 × 720 (portrait)

Output: browser-asteroid-dodger/index.html
```

---

## 🐸 Example 2 — Frog Crossing

> **Output:** `browser-frog-crossing/index.html`

```
Help me build a browser game called "Frog Crossing" — a Frogger-inspired clone —
using a single HTML file with vanilla JavaScript and the HTML5 Canvas API.
No external libraries or image assets; everything is drawn with Canvas 2D shapes.

Game concept:
- The frog starts at the bottom of the screen and must reach the top (the river bank)
- The screen is divided into horizontal lanes:
    • Bottom safe zone (frog start)
    • 3 road lanes — cars and trucks move left or right at different speeds
    • Middle safe zone (median strip)
    • 3 river lanes — logs and lily pads move left or right; frog rides them
    • Top safe zone (goal — 5 lily-pad slots the frog must fill to win)
- One life lost if hit by a vehicle or if frog falls in the river without a platform
- 3 lives total; score increases by 100 pts per successful crossing + 10 pts/sec remaining

Visual style:
- Flat retro colour blocks per lane (asphalt grey, grass green, river blue)
- Frog is a simple green rounded square with eyes; vehicles are coloured rectangles
- Logs are brown rounded rectangles; lily pads are dark green circles
- Retro pixel font ("Press Start 2P" via Google Fonts)
- Smooth movement: frog hops one grid cell per keypress with a short lerp animation

Screens:
1. Start screen — title, best score (localStorage), "SPACE / Tap to Start"
2. Game screen — score (top left), lives (top right), level number
3. Level complete — brief "LEVEL CLEAR" flash, difficulty increases for next level
4. Game Over screen — final score, best score, Restart button

Controls:
- Desktop: ↑ ↓ ← → or W A S D
- Mobile: swipe gestures (up/down/left/right) to hop

Additional requirements:
- Timer bar below the score — player has 30 s per crossing or loses a life
- Level progression: each level adds one more lane entity and speeds up by 10 %
- Frog drowning animation (shrink + fade) and road-kill animation (red flash)
- Responsive canvas: fills viewport, capped at 480 × 640 (portrait)

Output: browser-frog-crossing/index.html
```

---

## 💡 Tips for Implementation

When Bob generates the game, keep these conventions in mind:

| Topic | Recommendation |
|---|---|
| **Canvas setup** | Use `devicePixelRatio` scaling for crisp rendering on retina screens |
| **Game loop** | `requestAnimationFrame` with a fixed `deltaTime` cap (max 100 ms) |
| **Font loading** | Wait for `document.fonts.ready` before starting the render loop |
| **Mobile input** | Add both `touchstart` / `touchend` and `pointerdown` listeners |
| **localStorage** | Wrap in try/catch — Safari private mode throws on quota |
| **Single file** | Inline all CSS in `<style>` and all JS in `<script>` — zero dependencies |
| **Colour palette** | Limit to 5–7 colours for a coherent retro aesthetic |

---

## 📂 Suggested Folder Layout

```
pygames/
├── browser-asteroid-dodger/
│   └── index.html          ← Example 1 output
├── browser-frog-crossing/
│   └── index.html          ← Example 2 output
└── prompt-simple-browser-game.md   ← this file
```

---

*Generated by Bob — Your AI Software Engineer*
