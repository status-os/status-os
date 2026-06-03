# Contributing

Status OS welcomes technical and non-technical contributions.

## Good first contributions

- test the prototype on old hardware,
- improve device capability detection,
- add task manifest examples,
- document remote desktop tools,
- document Syncthing/WireGuard setup,
- design dashboard mockups,
- write accessibility requirements,
- add security threat models,
- translate documentation.

## Development principles

- Keep modules small.
- Keep privilege low.
- Do not put policy in the kernel.
- Use append-only logs for state transitions.
- Use hashes to verify state.
- Explain why a task is blocked.
- Prefer safe stasis over unsafe resume.

## Pull request standard

A good pull request includes:

- what changed,
- why it changed,
- how it was tested,
- security impact,
- compatibility impact,
- old hardware impact.

## Code style

Prototype code should be readable before it is clever.
