# Status OS

**Status OS is a distributed capability broker for human workflow continuity.**

Core thesis:

> The device should no longer be the center of computing. The task should be the center. The OS should know where that task can safely live, pause, stream, migrate, or resume.

Status OS is not a replacement Linux distribution at the start. It begins as a Linux-first orchestration layer that maps devices, tasks, state, trust, and resume modes across a local or global device mesh.

## Purpose

Status OS exists to:

- extend the useful life of old hardware,
- reduce unnecessary device replacement,
- make workflows continuous across phones, tablets, laptops, desktops, and servers,
- make strong machines available to weak devices safely,
- give AI and humans a shared task-state layer,
- support citizens, governments, companies, clients, schools, families, and public infrastructure with smoother machine usability.

## First principle

Every device should contribute according to its capability.

A weak device should not be discarded. It may become a terminal, viewer, controller, dashboard, document station, secure identity point, or remote access surface.

A strong device should not be isolated. It may become a compute anchor for AI, graphics, trading, engineering, science, education, and public service workflows.

## Resume modes

Status OS classifies every task into one or more valid resume modes:

- **Native** — run directly on the current device.
- **Remote** — control a task still running on another device.
- **Stream** — receive rendered video/audio from a stronger machine.
- **Checkpoint** — freeze and restore a compatible workload.
- **View-only** — inspect task status safely without controlling it.
- **Stasis** — task remains paused or preserved on its current host.
- **Blocked** — device lacks permission, hardware, security, network, or compatibility.

## First objective

Build a broker that answers one question:

> What can this device safely resume right now?

## MVP architecture

- **Status Anchor**: dedicated machine or service that maps trusted devices, tasks, state, and hashes.
- **Status Agent**: small program running on each machine to report capabilities.
- **Task Registry**: declares workflow requirements.
- **Capability Broker**: decides valid resume modes.
- **State Ledger**: append-only hash chain of task-state transitions.
- **Image Map**: content-addressed map of files, configs, snapshots, and checkpoints.
- **Resume UI**: simple dashboard showing what can continue on the current device.

## Repository layout

```text
docs/               project documents and architecture
governance/         contribution, security, and governance documents
prototype/          first local proof-of-concept
```

## Prototype

Run the prototype:

```bash
cd prototype
python statusos_agent.py --out examples/this-device.json
python statusos_broker.py --devices examples/devices.json --tasks examples/tasks.json
```

The broker returns allowed resume modes for each device/task combination.

## Status

Genesis kit. Concept and prototype seed.
