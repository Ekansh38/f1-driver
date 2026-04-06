# f1-driver

A top-down racing simulator in Python. Drive on custom circuits, tune your car physics, and record cryptographically signed lap times.

<table>
  <tr>
    <td><img src="READMEASSETS/moreassets/screenshot3.png"/></td>
    <td><img src="READMEASSETS/moreassets/screenshot4.png"/></td>
  </tr>
</table>

## Demo

**Driving and lap timer**

<video src="READMEASSETS/driving.mov" controls></video>

**Track switcher**

<video src="READMEASSETS/track-switcher.mov" controls></video>

**Car params**

<video src="READMEASSETS/car-params.mov" controls></video>

**Signed lap verification**

<video src="READMEASSETS/lap-signing.mov" controls></video>

## Features

- **Custom tracks** with a built-in track switcher
- **Tunable car physics** (acceleration, braking, grip, top speed) from an in-game params menu
- **Lap timer** with automatic finish-line detection
- **Signed lap times** using HMAC-SHA256. Lap strings are shareable and verifiable by anyone with the key
- **Multi-car** with 1 human driver and configurable AI opponents (built to be neural net ready)
- **Camera modes**: follow cam, fixed overhead, rotated cockpit view
- **Per-lap telemetry** recording

## Controls

| Key | Action |
|-----|--------|
| W / A / S / D | Accelerate / steer left / brake / steer right |
| R | Reset to start |
| C | Cycle camera mode |
| Tab | Track switcher |
| P | Car params menu |
| L | Signed laps panel |
| V | Verify a lap string |
| Escape | Pause |

## Signed Lap Times

Every lap completed with default car params gets signed automatically with HMAC-SHA256 and stored in the laps panel.

The signed string looks like:

```
01:23.456,gragram a3f9c2...
```

Press `L` to open the panel and copy a lap. Press `V` to verify any signed string (paste it in, hit Enter). The verifier confirms the lap time and track name. Laps with modified car params are tagged `[unofficial]`.

The key lives in `key.py` which is gitignored. In a real competitive setting it would live server-side.

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

Requires Python 3.11+ and pygame-ce (not vanilla pygame).

## Adding Tracks

Drop a folder into `tracks/` with a `track.png` and `data.json` (spawn coords, lap line, track name). The switcher picks it up automatically.
