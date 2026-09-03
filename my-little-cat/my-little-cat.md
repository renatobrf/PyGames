# My Little Cat - Escape the House!

A charming 16-bit style platformer game where you help a little cat escape from the house by jumping across furniture and avoiding obstacles.

## Game Features

- **16-bit Retro Graphics**: Authentic retro color palette and pixel-art style
- **3 Unique Levels**: Navigate through Living Room, Kitchen, and Bedroom
- **Platform Mechanics**: Jump between furniture pieces to reach the exit
- **Obstacles**: Avoid household items like vases, books, and lamps
- **Collectibles**: Gather fish treats for bonus points
- **Lives System**: 3 lives with invincibility frames after taking damage
- **Score Tracking**: Earn points for collectibles and level completion

## How to Play

### Installation

1. Ensure you have Python 3.x installed
2. Install pygame:
   ```bash
   pip install pygame
   # or on Windows:
   pip install pygame-ce
   ```

### Running the Game

```bash
cd pygame-my-little-cat
python my-little-cat.py
```

### Controls

- **Arrow Keys** or **WASD**: Move left/right
- **SPACE** or **UP Arrow** or **W**: Jump
- **ESC**: Quit game

### Objective

Help the little orange cat escape through all three rooms of the house:

1. **Living Room**: Navigate sofas, coffee tables, and TV stands
2. **Kitchen**: Jump across counters and kitchen islands
3. **Bedroom**: Climb over beds, dressers, and nightstands

Avoid red obstacles (they hurt!), collect blue fish treats for points, and reach the brown exit door in each level.

## Scoring System

- **Collectible (Fish Treat)**: 100 points
- **Level Completion**: 500 points
- **Game Completion**: 1000 bonus points

## Game Mechanics

- **Gravity & Physics**: Realistic jumping and falling mechanics
- **Collision Detection**: Precise platform and obstacle collision
- **Invincibility Frames**: 2 seconds of protection after taking damage (cat flashes)
- **Progressive Difficulty**: Each level introduces new platform layouts and obstacles

## Tips

- Take your time! There's no time limit
- Watch out for obstacles on platforms
- Collect all treats for maximum score
- Use the floor as a safe zone to plan your next jump
- The cat has 3 lives - use them wisely!

## Technical Details

- **Resolution**: 800x600 pixels
- **Frame Rate**: 60 FPS
- **Engine**: Pygame/Pygame-CE
- **Language**: Python 3.x

## Game States

1. **Start Screen**: Title, instructions, and game start
2. **Playing**: Active gameplay with HUD showing lives, score, and level
3. **Game Over**: Victory or defeat screen with final score and restart option

## Credits

Created with Pygame - A fun 16-bit platformer adventure!

Enjoy helping the little cat escape! 🐱