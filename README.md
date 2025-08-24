# codex-4x-game

Prototype turn-based 4X game built with pygame and pygame_gui. Found cities,
build improvements, and conquer your opponent.

## Requirements
- Python 3.11
- pygame >= 2.5.0
- pygame_gui >= 0.6.9

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running
```bash
python -m game.main
```

## Controls

- **W/A/S/D**: move selected unit
- **F**: found city
- **1-4**: build infrastructure (1 farm, 2 mine, 3 saw, 4 road)
- **Enter**: end turn
- **Q**: quit game
- **Shift + Left Click**: move entire soldier stack

### Win/Lose

You lose only when you have no cities and no settler units remaining. As long as
you control a city or a settler, the game continues.

Cities spend food to grow and automatically claim nearby tiles. Building
farms, mines, sawmills, and roads on claimed tiles boosts yields and can reduce
movement costs.
Production cannot be stockpiled; unused production is lost at the end of each turn.

## Tests
```bash
pytest -q
```

## Lint and Format
```bash
ruff check .
black .
```
