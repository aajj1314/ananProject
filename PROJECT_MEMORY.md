# Project Memory

## Snapshot
- Workspace: `/root/ananProject`
- Backup target: `/sdcard/Download/Turrit/ananProject`
- Local Python environment: `/root/ananProject/.venv`
- Primary backend entry: `/root/ananProject/backend/app/main.py`
- Primary frontend entry: `/root/ananProject/frontend/src/main.ts`

## Completed
- Phase 1 foundation complete.
- Phase 2 operations baseline complete and tested.
- Phase 3 business flow completion complete and tested.
- Phase 4 electronic fence rules and breach alerts complete and tested.

## Current Phase
- Phase 4 planning and implementation queue.
- Focus areas:
  - real map SDK integration
  - richer notification channels
  - operational health and metrics

## Resume Checklist
- Activate backend environment with `/root/ananProject/.venv/bin/python` or `/root/ananProject/.venv/bin/pytest`.
- Run tests from `/root/ananProject/backend` using `/root/ananProject/.venv/bin/pytest -q`.
- Review latest development log in `/root/ananProject/WORKLOG.md`.
- After finishing a phase, refresh backup under `/sdcard/Download/Turrit/ananProject`.

## Known Constraints
- Android `/sdcard` backup cannot store `.venv` symlinks reliably.
- Backup strategy for Android storage should exclude `.venv` and sync source files only.
- Redis is optional at runtime because cache falls back to in-memory behavior.

## Latest Verification
- `python3 -m compileall /root/ananProject/backend/app /root/ananProject/backend/tests` passed on 2026-04-10 after fence changes.
- `python3 -m compileall /root/ananProject/backend/app /root/ananProject/backend/tests` passed on 2026-04-10.
- `/root/ananProject/.venv/bin/pytest -q` passed with `2 passed` on 2026-04-10 after fence changes.
