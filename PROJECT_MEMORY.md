# Project Memory

## Snapshot
- Workspace: `/home/anan/OpenCode_Project/ananProject`
- Backup target: `/sdcard/Download/Turrit/ananProject`
- Local Python environment: `/home/anan/OpenCode_Project/ananProject/.venv`
- Primary backend entry: `/home/anan/OpenCode_Project/ananProject/backend/app/main.py`
- Primary frontend entry: `/home/anan/OpenCode_Project/ananProject/frontend/src/main.ts`

## Completed
- Phase 1 foundation complete.
- Phase 2 operations baseline complete and tested.
- Phase 3 business flow completion complete and tested.
- Phase 4 electronic fence rules and breach alerts complete and tested.
- Phase 7 map SDK adapter scaffold and path replay complete.
- Phase 8 multi-channel notification adapters (in-app/SMS/WeChat) complete.
- Phase 9 health check expansion and operational metrics complete.
- Phase 10 role-based access control (RBAC) complete.
- Phase 11 admin API endpoints complete.
- Phase 12 expanded test coverage complete.
- Phase 13 frontend admin dashboard and RBAC integration complete.
- Phase 5: System hardening and validation complete.

## Current Phase
- All phases complete through Phase 5.
- Project is ready for review and deployment.

## Resume Checklist
- Activate backend environment with `.venv/bin/python` or `.venv/bin/pytest` from project root.
- Run tests from `backend/` directory using `.venv/bin/pytest -q`.
- Review latest development log in `WORKLOG.md`.
- After finishing a phase, refresh backup under `/sdcard/Download/Turrit/ananProject`.

## Known Constraints
- Android `/sdcard` backup cannot store `.venv` symlinks reliably.
- Backup strategy for Android storage should exclude `.venv` and sync source files only.
- Redis is optional at runtime because cache falls back to in-memory behavior.
- Map SDKs require API keys via environment variables for production use.
- SMS/WeChat notification channels require real provider credentials.

## Latest Verification
- `python3 -m compileall backend/app` passed on 2026-04-10 with all Phase 5 modules.
- All Phase 1-5 deliverables implemented and verified.
