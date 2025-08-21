# codex-4x-game

Prototype 4X (Explore, Expand, Exploit, Exterminate) strategy game built with Python, pygame, and pygame_gui.

## Install

```bash
pip install -r requirements.txt
```

`requirements.txt` selects the correct SDL binding for your interpreter:

- CPython installs **pygame ≥2.6**, which provides the `DIRECTION_LTR` flag
  needed by `pygame_gui`.
- Other interpreters (e.g. PyPy) install **pygame-ce ≥2.5.1**, a drop-in
  replacement.

Only one of these libraries should be present at a time.

## Run

```bash
python -m game.main
```

## Tests

```bash
pytest -q
```

## Lint/Format

```bash
ruff check .
black .
```
