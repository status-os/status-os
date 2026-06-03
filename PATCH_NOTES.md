# Status OS Dashboard v0.1 Patch

This patch advances Issue #1: Build v0.1 local Status Anchor dashboard.

## Add

- `prototype/statusos_dashboard.py`
- `prototype/README_DASHBOARD_V0.1.md`

## Run

From the `prototype` folder:

```bash
python statusos_dashboard.py --devices examples/devices.json --tasks examples/tasks.json
```

Open:

```text
http://127.0.0.1:8765
```

## Shows

- device list,
- task list,
- task state,
- host device,
- resume mode,
- blocked/stasis reason,
- ledger event hash.

## Limits

- local-only,
- no authentication,
- no remote execution,
- no persistent database,
- no live device polling yet.

## Commit message

Add v0.1 local Status Anchor dashboard

Initial dashboard prototype prepared.

Adds:
- local-only web dashboard
- device/task/resume-mode table
- blocked/stasis reasons
- ledger event hash preview

Patch:
status-os-v0.1-dashboard-patch.zip

Run:
python prototype/statusos_dashboard.py --devices prototype/examples/devices.json --tasks prototype/examples/tasks.json

Open:
http://127.0.0.1:8765

Scope:
- local-only
- no authentication yet
- no remote execution yet
