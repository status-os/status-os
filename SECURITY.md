# Security Policy

Status OS is security-sensitive.

It maps devices, tasks, state, identity, and resume control. Treat all designs as hostile-network designs from the start.

## Security rules

1. Default deny.
2. Least privilege.
3. Explicit user consent for control.
4. No silent remote control.
5. No unverified state restore.
6. No trusted device without identity.
7. No kernel privilege unless required.
8. No AI authority over privileged system changes without explicit policy.
9. Logs should be tamper-evident.
10. Secrets should not be stored in task manifests.

## Threats

- unauthorized remote control,
- malicious device joining mesh,
- poisoned task manifest,
- replayed state event,
- false capability report,
- stolen device identity,
- compromised anchor,
- supply-chain attack,
- unsafe checkpoint restore,
- data leakage through logs.

## Initial mitigations

- local-only prototype,
- explicit allowlist of devices,
- hash-chain state ledger,
- no secrets in examples,
- clear blocked reasons,
- signed manifests later,
- reproducible builds later,
- SLSA-aligned supply-chain process later.

## Reporting

Do not publicly disclose serious vulnerabilities until maintainers can assess impact.
