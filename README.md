# f1-driver

A top-down racing simulator written in Python with pygame-ce. Drive on custom tracks, tune your car, and record cryptographically signed lap times.

![screenshot](./assets/Screenshot1.png)

---

## Features

- **Custom tracks** — multiple circuits with a built-in track switcher
- **Tunable car physics** — adjust acceleration, braking, grip, top speed, and more from an in-game params menu
- **Lap timer** — automatic detection with finish-line proximity check
- **Cryptographic lap authentication** — lap times are signed with HMAC-SHA256. Share a signed string and anyone with the key can verify it's legitimate and unmodified
- **Multi-car support** — 1 human driver + configurable AI opponents using a simple input interface (neural net drop-in ready)
- **Camera modes** — follow cam, fixed overhead, rotated cockpit view
- **Telemetry** — per-lap speed and input recording

---

## Controls

| Key | Action |
|-----|--------|
| W / A / S / D | Accelerate / steer left / brake / steer right |
| R | Reset car to start |
| C | Cycle camera mode |
| Tab | Open track switcher |
| P | Open car params menu |
| L | Open signed laps panel (copy a lap to clipboard) |
| V | Verify a signed lap string |
| Escape | Pause |

---

## Signed Lap Times

When you complete a lap with default car parameters, it is automatically signed with **HMAC-SHA256** and stored in the laps panel (`[L]`).

The signed string looks like:

```
01:23.456,gragram a3f9c2...
```

- Copy it with `[L]` → click the lap entry
- Verify any string with `[V]` → paste → Enter
- The verifier shows the lap time and track name if authentic
- Laps completed with modified car params are tagged `[unofficial]` and still signable, but clearly marked

The secret key lives in `key.py` (gitignored). In a competitive setting this would live server-side.

---

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

> Requires Python 3.11+ and pygame-ce (not pygame). The `requirements.txt` handles this.

---

## Adding Tracks

Drop a track folder into `tracks/` with a `track.png` and `data.json` (spawn point, lap line, track name). The switcher picks it up automatically.
