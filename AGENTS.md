# Velnio public App catalog

This repository may publish the generic Installer runtime, build recipe, metadata,
logos and documentation. Native integration code, integration ZIPs, source-material
archives, shared tokens, and container layers containing the integration stay private.

Supervisor pulls the PRIVATE ghcr.io/velnio/velnio-installer image using the user's
Home Assistant Registry credentials. The App receives no registry PAT and has no
GitHub token option. Never expose Docker API access, credentials in build arguments,
image layers, logs or this repository. Do not make withdrawn payloads public again.

Public CI tests the generic runtime and catalog only. Build contexts with native
payloads must stay private. Qualify both architectures against the exact private
release file map, install/no-op, backup and rollback tests before publishing a new
immutable image tag. Verify package visibility and anonymous denial before and after.

Before GitHub writes verify Un0kNow, target repository and Git authentication.
Preserve independently versioned R4, Health and SFTP entries.

Cross-repository ownership and architecture: [Velnio repository map](https://github.com/Velnio/velnio_pcb/blob/main/docs/repository-map.md) and [architecture overview](https://github.com/Velnio/velnio_pcb/blob/main/docs/architecture.md). Check current sources before relying on historical status.

## Working in this repository

- This is the public catalog: review `repository.yaml`, the affected App directory and its `config.json`, documentation and `tests/` together. Check each independent App/version rather than updating catalog entries as a group.
- Keep generic runtime/build inputs separate from native integration sources and private payloads. Changes to image references or release metadata do not prove image access, installation, rollback or a published release.

## Itsaplan task workflow

The VELN project is [Itsaplan](https://plan.richardbabjak.sk/mijoo/VELN). When a user asks you to implement a VELN issue, or a unique issue clearly matches the requested work, read that issue and its acceptance criteria, dependencies and relevant PRD/ADR before implementation. Search or ask when the match is ambiguous; do not pick an unrelated issue or change its status.

- Read the current project configuration and choose status columns by their state type, not hard-coded IDs or assumptions. Before starting the issue, move it to the current started state; respect WIP limits and any actual blockers. Work on one issue at a time.
- Mark the issue completed only after its requested scope and relevant verification are complete. If work is abandoned, use the project's canceled state. Do not leave an issue started when stopping; follow the tracker workflow if access or a transition is blocked and report the limitation.
- For unfinished work, add a concise comment explaining what remains and why; read activity first on a long-running issue to avoid duplicate comments. For fully completed work, do not add a routine comment. Distinguish planned, local, lab and live results and never claim unrun checks.
- Do not create issues, assign people or agents, mention users, change unrelated issues or launch work automatically unless requested. Mentions and assignments may trigger agents. Never put credentials, private customer information or sensitive operational data in issues or comments.
- If Itsaplan is unavailable or access is denied, do not invent or claim tracker updates; continue independent authorized work where possible and report the missing update. A direct user instruction takes precedence over these project conventions.
