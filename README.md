# Cicero

A Discord bot for managing a homelab k3s cluster — inspect pods, restart deployments, scale replicas, and audit every action, all from Discord slash commands.

## Stack

- [discord.py](https://discordpy.readthedocs.io/)
- [kubernetes](https://github.com/kubernetes-client/python) — official Python client for the k8s API
- [k3s](https://k3s.io/) — lightweight Kubernetes, single-node homelab
- `ruff` · `mypy` · `pytest` · `pre-commit` — linting, typing, tests, local hooks

## Roadmap

- [x] **M0** — Repo & tooling scaffolding
- [x] **M1** — Bot skeleton + `/status`
- [ ] **M2** — Read-only inspection (`/pods`, `/describe`, `/logs`, `/nodes`)
- [ ] **M3** — Role-based access control
- [ ] **M4** — Control commands (`/restart`, `/scale`)
- [ ] **M5** — Audit logging (SQLite, `/audit`)
- [ ] **M6** — Deploy the bot into the cluster with scoped RBAC
- [ ] **M7** — CI/CD hardening, optional `k3d` integration tests

## Getting started
For development:
```powershell
git clone git@github.com:lukasdo-git/cicero.git
cd cicero
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pre-commit install
cp .env.example .env   # fill in DISCORD_TOKEN and DISCORD_GUILD_ID
python -m cicero #to run the bot
```
For production use:
TBD

## CI

[![CI](https://github.com/lukasdo-git/cicero/actions/workflows/CI.yml/badge.svg?event=push)](https://github.com/lukasdo-git/cicero/actions/workflows/CI.yml)

Every push runs `ruff check`, `ruff format --check`, `mypy`, and `pytest`.
