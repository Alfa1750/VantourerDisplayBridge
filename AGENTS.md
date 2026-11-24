# AGENTS.md — Working instructions for repository changes

These instructions apply to all work in this repository performed by ChatGPT or another coding assistant.

## Required working method

### 1. Work directly through GitHub
- Read and modify repository files directly through the connected GitHub integration (GitHub repository/content/commit operations).
- Do not hand work off to ChatGPT Work, Codex, a cloud computer, or a local coding agent.
- Do not require the user's PC, browser session, terminal, or development environment to remain open. GitHub changes are made through the repository connection.
- Do not claim background work continues after a response has been sent. Continue making changes during the active work session and report only work that has actually been completed.

### 2. Inspect before changing anything
At the start of every task:
- Confirm the repository, target branch, current branch HEAD, and relevant base/version.
- Read this file and the current `docs/PROJECT_STATUS.md` and `CHANGELOG.md`.
- Read all other relevant project documentation and source files before editing them.
- Check whether the requested behavior already exists and inspect suitable existing implementations, libraries, examples, and upstream documentation before writing new code.
- Preserve existing project decisions and explicitly recorded constraints. Do not silently reverse or bypass them.
- If a required file or fact cannot be retrieved, state that limitation; do not assume its contents.

### 3. Make controlled GitHub changes
- Work only on the explicitly selected development branch. Never change `main`, another branch, or a release tag unless the user explicitly asks.
- Make focused, reviewable changes. Avoid unrelated cleanup, formatting, renaming, or refactoring.
- Use the latest file/blob SHA for every update. Do not perform concurrent writes to the same file.
- Keep project documentation, status, and changelog consistent with the actual implementation.
- Record meaningful intermediate work in Git commits with clear messages.
- Do not merge branches, create release tags, or declare acceptance without the user's explicit approval.

### 4. Verify every repository change
After each write:
- Fetch the changed file again from the same branch and verify its contents.
- Record the resulting commit SHA and confirm the branch HEAD.
- Inspect the final diff/compare when multiple files have changed.
- Distinguish source review and static checks from actual builds, hardware tests, and runtime validation. Never claim a test ran unless it really ran.

### 5. Actions that always require explicit user permission
Never start or trigger:
- firmware builds, compilation, flashing, or device programming;
- package installation, dependency installation, or environment/configuration changes;
- background processes, services, or deployment actions;
- changes on the Raspberry Pi, Venus OS, Node-RED runtime, or other live systems;
- destructive cleanup, branch merges, or release/tag operations.

A request to implement code in GitHub authorizes only the scoped repository source/documentation changes. It does not authorize deployment or execution on the user's equipment.

### 6. Communication
- Do the research and repository work before returning to the user.
- Do not send progress messages, repeated plans, or premature completion notices.
- Contact the user when a physical action, test, decision, missing input, or explicit permission is genuinely required, or when the scoped work is completed.
- Report exact repositories, branches, files, commit IDs, and verification performed. State clearly what remains untested.

## Project-specific boundaries
- The SetupHelper package and its source must remain project-owned; external SetupHelper material is reference material only and must not be copied into this repository.
- Node-RED flows are independently maintained. Do not overwrite a live flow or assume a test-flow export is the user's production flow.
- Preserve the agreed separation between Raspberry Pi bridge, ESP32 firmware, Node-RED flows, and the separate JK-BMS monitor.
- Keep the independent version histories of the Pi package and ESP32 firmware distinct.
