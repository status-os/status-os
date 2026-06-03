# Status OS Anchor v0.2

This patch begins the Status Anchor.

The Status Anchor is the local authority that remembers registered devices and runs task-resume decisions against them.

## File added

- `prototype/statusos_anchor.py`

## Local test

From the `prototype` folder:

```bash
python statusos_anchor.py init
python statusos_anchor.py register-device --file examples/devices.json
python statusos_anchor.py list-devices
python statusos_anchor.py decide --tasks examples/tasks.json
python statusos_anchor.py events
```

## What this proves

- the project now has a persistent local device registry,
- devices can be registered from JSON,
- registered devices can be listed,
- broker decisions can run against registered devices,
- decision events are written into a SQLite database,
- event records are hash-linked for tamper evidence.

## Database

Default database:

```text
statusos_anchor.db
```

This file is local runtime state and should not be committed.

## Limits

- local-only,
- no authentication yet,
- no remote execution yet,
- no mesh networking yet,
- no live polling yet,
- no dashboard integration yet.
