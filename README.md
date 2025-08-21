# codex-4x-game

Prototype 4X (Explore, Expand, Exploit, Exterminate) strategy game built with Python, pygame, and pygame_gui.

## Install

```bash
pip install -r requirements.txt
```

Requires `pygame` **2.6.0** or newer to satisfy `pygame_gui`.

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
