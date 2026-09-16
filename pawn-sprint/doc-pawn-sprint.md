# Pawn Sprint — Game Documentation

> A 16-bit styled pawn-racing board game built with Python & Pygame.

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [How to Run](#how-to-run)
4. [Game Rules](#game-rules)
5. [Controls](#controls)
6. [AI Opponent](#ai-opponent)
7. [Code Architecture](#code-architecture)
8. [Visual Style](#visual-style)
9. [File Structure](#file-structure)

---

## Overview

**Pawn Sprint** is a single-player strategic board game that uses the standard chess board (8×8) and pawn movement rules. The player controls the **White** pawns and races against an **AI** opponent controlling the **Black** pawns.

**Goal:** Be the first player to advance any one of your pawns to the opposite back rank.

- White pawns must reach **row 8** (Black's back rank).
- Black pawns must reach **row 1** (White's back rank).

---

## Requirements

| Dependency | Version |
|------------|---------|
| Python     | 3.10+   |
| Pygame     | 2.x     |

Install Pygame if not already installed:

```bash
pip install pygame
```

---

## How to Run

```bash
cd pawn-sprint
python pawn_sprint.py
```

The game window opens at **720 × 760 px** and runs at 60 FPS.

---

## Game Rules

### Board Setup

- Standard 8×8 chessboard.
- **White pawns** are placed on rank 2 (row index 6) — all 8 pawns.
- **Black pawns** are placed on rank 7 (row index 1) — all 8 pawns.

### Movement

Pawns move exactly as in chess:

| Action | Description |
|--------|-------------|
| **Forward** | One square straight ahead (no double-step from the start). |
| **Capture** | One square diagonally forward onto an enemy pawn. |
| **En passant** | Not implemented (out of scope for this racing variant). |
| **Promotion** | Reaching the back rank wins the game immediately. |

### Win Conditions

The game ends when **any one** of the following occurs:

1. A **White pawn** reaches row 0 (rank 8 from White's perspective) → **White wins**.
2. A **Black pawn** reaches row 7 (rank 1 from White's perspective) → **Black wins**.
3. A player has **no legal moves** remaining → the **opponent wins**.

### Turn Order

- White always moves first.
- Turns alternate between White (Human) and Black (AI).
- The AI takes a brief "thinking" pause (`0.5 s`) before executing its move to feel natural.

---

## Controls

| Input | Action |
|-------|--------|
| **Left-click** on own pawn | Select the pawn; valid target squares are highlighted. |
| **Left-click** on highlighted square | Execute the move. |
| **Left-click** on empty/enemy square | Deselect current pawn. |
| **R key** | Restart the game. |
| **NEW GAME button** | Restart the game (on screen). |
| **ESC key** | Quit the game. |

### Highlight Legend

| Colour | Meaning |
|--------|---------|
| 🟡 Yellow | Currently selected pawn |
| 🟢 Green | Valid forward move |
| 🔴 Red | Valid diagonal capture |

---

## AI Opponent

The AI uses the **Minimax algorithm with Alpha-Beta pruning** to select its best move each turn.

### Parameters

| Parameter | Value |
|-----------|-------|
| Algorithm | Minimax + Alpha-Beta pruning |
| Search depth | 4 ply |
| Evaluation function | Pawn advancement score |
| Move ordering | Random shuffle (prevents robotic repetition) |

### Evaluation Heuristic

The static board evaluation function scores positions based on **pawn advancement**:

```
score = Σ (row * 2) for each Black pawn
      − Σ ((7 − row) * 2) for each White pawn
```

- Positive score → better for Black (AI).
- Negative score → better for White (Human).

The `INF` terminal scores (`±10,000`) reward winning sooner and punish losing sooner via a depth-adjusted bonus.

### Difficulty

At depth 4 the AI plays solidly: it advances aggressively, captures opportunistically, and blocks the human's most advanced pawns. It is beatable with careful play but provides a meaningful challenge.

---

## Code Architecture

```
pawn_sprint.py
├── Constants & Colours          # window size, CELL size, 16-bit palette
├── board_to_px() / px_to_board()  # coordinate conversion helpers
├── draw_pawn()                  # vector-drawn pawn glyph (no image files needed)
├── Board                        # game-state model
│   ├── grid[row][col]           # 8×8 matrix of (player, pawn_id) or None
│   ├── legal_moves(player)      # generates all valid moves for a side
│   ├── move(fc,fr,tc,tr)        # mutates the board
│   ├── copy()                   # deep copy for tree search
│   └── check_win()              # detects terminal states
├── evaluate(board)              # heuristic score for minimax
├── minimax(...)                 # recursive alpha-beta search
├── ai_best_move(board)          # picks the best move for BLACK
├── PawnAnim                     # smooth ease-in/out animation for a single move
├── Button                       # simple hover+click UI button
└── PawnSprint                   # main game class
    ├── _new_game()              # resets all state
    ├── handle_events()          # mouse clicks, keyboard, button
    ├── update()                 # animation tick, AI trigger
    ├── draw()                   # full render pipeline
    │   ├── _draw_board()        # squares + coordinate labels
    │   ├── _draw_highlights()   # selected + legal-target overlays
    │   ├── _draw_pieces()       # static pawn rendering
    │   ├── _draw_ui()           # title bar, turn indicator, buttons
    │   └── _draw_victory()      # win overlay panel
    └── run()                    # main game loop (60 FPS)
```

---

## Visual Style

The game adopts a **16-bit retro aesthetic** achieved entirely through code (no external image assets):

- **Colour palette** — warm wood tones for the board, deep navy background, golden title text, bright accent colours.
- **Pawn glyphs** — procedurally drawn with circles and ellipses: head, neck, base, and a specular shine dot.
- **Smooth animation** — ease-in/out interpolation (smoothstep) for pawn movement.
- **Pixel-art border** — double-stroke rectangular border on the victory panel.
- **Monospaced font** — Courier New for a retro terminal/pixel-font feel.

---

## File Structure

```
pawn-sprint/
├── pawn_sprint.py          # Game source code
├── doc-pawn-sprint.md      # This documentation
└── prompt-pawn-sprint.txt  # Original design brief
```

---

## Known Limitations / Possible Enhancements

| Feature | Status |
|---------|--------|
| En passant | Not implemented |
| Sound effects | Not implemented |
| Two-player (human vs human) mode | Not implemented |
| Difficulty levels (depth control) | Not implemented |
| Saved high scores / move history | Not implemented |
| Animated capture flash | Not implemented |

Feel free to extend the project — the `Board` class is cleanly separated from the rendering and AI layers, making enhancements straightforward.
