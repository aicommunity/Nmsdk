# Model-time autosave (Console) — порт из spike_classifier_preset

Дата: 2026-10-01.

## Источник

- Ветка `origin/spike_classifier_preset`, commit root **`3bae747`** (*Add console model-time autosave*).
- Rdk: `ProjectAutoSaveModelTimeInterval` в `UProject.h` / `UProject.cpp` (pointer preset `d27ba4c`).
- Описание: PulseLib `Docs/Analysis/NNeuronStructuralTrainingAudit.md` (§ ProjectAutoSaveModelTimeInterval).

**Не** мержить целиком classifier/AutoPreset — только autosave.

## Поведение

- XML `Project.ini` → `<General><ProjectAutoSaveModelTimeInterval>N</…>` — секунды **модельного** времени; `0` = выкл.
- `NeuroModelerConsole`: QTimer ~500 ms; при `modelTime >= nextSave` → `UApplication::SaveProject()` (Model + Parameters).
- States не обязательны для SoftCold poll Need/TipR.

## Ограничения

- `SaveProject()` может вернуть true при частичном fail — смотреть mtime файлов / лог.
- Не гарантия resume mid-train.
- GUI пока не обязан обрабатывать параметр.

## SoftCold harness

- Workdir: выставлять interval при soft-cold / prepare (не массово править архивы EXP).
- CLI: `--autosave-model-s N` в `posttune_verify.py` (default **10**; `0`=off).
- `repro_cold_lib.set_project_autosave_model_interval` + поле `project_autosave_model_time_interval` в `cold_reset_contract.json`.
- `wait_need0`: poll Need/TipR/L из Parameters; `AUTOSAVE_SEEN mtime=…` при обновлении Save; early-stop при Need=0 + TipR settled (или flag).
- Цель: читать Need/TipR из периодически сохранённых XML, early-exit при Done.

## Калибровка

| Interval (model-s) | Когда |
|--------------------|-------|
| 5–10 | SoftCold default / AmpNorm diagnostics |
| 20–30 | длинные Train (-t ≥ 900) если I/O Save заметно |
| 0 | отладка без mid-train Save |
