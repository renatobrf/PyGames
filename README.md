# PyGames

A collection of small games and interactive prototypes built with [Pygame](https://www.pygame.org/). The repository currently contains two 16-bit adventure games and four 8-bit market simulations.

## Requirements

- Python 3
- Pygame

Install Pygame in the active Python environment:

```bash
python -m pip install pygame
```

## Projects

### `pygame-8bits`

Retro-style market and trading experiments:

- **Market Stocks** (`market_game.py`): move through the market, collect profit and boost items, avoid crashes, and manage your portfolio and lives.
- **Stock Trading Simulator** (`trading-simulator.py`): buy and sell shares while following a live candlestick chart and portfolio value.
- **Stock Predictor** (`stock-prediction.py`): observe a simulated price history and make short-term market predictions.
- **Agricultural Commodities Trader** (`commodities-trader-v2.py`): trade soybeans, corn, rice, beans, wheat, cotton, milk, and eggs as prices fluctuate.

Run a game from its folder:

```bash
cd pygame-8bits
python market_game.py
python trading-simulator.py
python stock-prediction.py
python commodities-trader-v2.py
```

Controls vary by prototype. `market_game.py` uses the arrow keys and `R` to restart after game over. The trading prototypes primarily use the mouse; `commodities-trader-v2.py` also supports `Esc` to quit and `1`, `5`, and `0` to select trade quantities.

### `pygame-16bits`

Two versions of **As Aventuras da Helena**:

- `as-aventuras-da-helena.py`: a single underwater obstacle course. Use the arrow keys to reach the exit; press `R` after winning or losing to play again.
- `as-aventuras-da-helena-parte2.py`: a jungle-themed version with an intro menu, animated animals, and start/exit buttons. Use `WASD` or the arrow keys to move, and click the screen after winning or losing to return to the menu.

Run either version from its folder:

```bash
cd pygame-16bits
python as-aventuras-da-helena.py
python as-aventuras-da-helena-parte2.py
```

## Repository Status

`flight-radar/` and `my-little-cat/` are reserved for future projects and are currently empty.

## Notes

The games are standalone prototypes and do not require external art or data files. Configuration and design prompts for some prototypes are kept alongside their source code in the relevant project folder.
