# Status OS v0.2 Anchor Patch

This patch advances Issue #2:

Build v0.2 Status Anchor service and live device registry.

## Adds

- `prototype/statusos_anchor.py`
- `prototype/README_ANCHOR_V0.2.md`

## Commit message

Add v0.2 Status Anchor prototype

## Test

```bash
cd prototype
python statusos_anchor.py init
python statusos_anchor.py register-device --file examples/devices.json
python statusos_anchor.py list-devices
python statusos_anchor.py decide --tasks examples/tasks.json
python statusos_anchor.py events
```

## Expected result

The anchor should:
- initialize a local SQLite database,
- register example devices,
- list known devices,
- run resume decisions,
- store hash-linked state events.
