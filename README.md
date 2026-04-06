# f1-driver

A top-down racing simulator in Python. Drive on custom circuits, tune your car physics, and record cryptographically signed lap times.

<table>
  <tr>
    <td><img src="READMEASSETS/moreassets/screenshot1.png" width="400"/></td>
    <td><img src="READMEASSETS/moreassets/screenshot2.png" width="400"/></td>
  </tr>
  <tr>
    <td><img src="READMEASSETS/moreassets/screenshot3.png" width="400"/></td>
    <td><img src="READMEASSETS/moreassets/screenshot4.png" width="400"/></td>
  </tr>
</table>

## DEMO VIDEOS


https://github.com/user-attachments/assets/499fdbb9-c980-4e8d-aefd-d6083af5de17

https://github.com/user-attachments/assets/496d50dc-dacb-45b5-80d3-1cb2a6ce5ecd

https://github.com/user-attachments/assets/a502291a-9315-4b31-ba09-db75fe073751

https://github.com/user-attachments/assets/e4e8bdca-6612-42a9-a8dd-bb48eceeb83d


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
