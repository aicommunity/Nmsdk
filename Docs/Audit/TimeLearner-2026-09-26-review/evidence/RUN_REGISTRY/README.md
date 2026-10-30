# RUN_REGISTRY — единый реестр путей к прогонам

План: [`../plans/PLAN_2026-10-25_dendrite_limits.md`](../../plans/PLAN_2026-10-25_dendrite_limits.md) §H3.

## Формат

Файл `runs.tsv` (TSV, одна строка = один run):

```
run_id	host	case	wave	status	src_path	offload_path	bytes	sha256_dir	moved_utc	note
```

- `src_path` — исходный каталог на хосте прогона (`…/runs/<id>` или `_work`).
- `offload_path` — после переноса: `/media/user/Data/TLAgent-offload/<host>/<date>/<id>` (или пусто).
- `status`: `active` | `done_local` | `offloaded` | `blocked_data_full`.

## Правила

1. Регистрировать run при старте волны (`active`) и при Done (`done_local`).
2. Offload только `done_local`, уже учтённых в сводке волны.
3. rsync → verify → unlink src; при ошибке verify исходник **не** удалять.
4. Если `/media/user/Data` free% &lt; **5** — `blocked_data_full`, см. `CAMPAIGN_STATUS_LATEST.md`.
5. Журналы NMSDK (`*.log`, `*Audit.log`, Dynamics): `archive_nmsdk_journals.sh` → `TLAgent-offload/journals/<host>/<date>/`; строки `jarch_*` в `runs.tsv`.
