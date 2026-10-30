# Offload TimeLearnerTrainingDynamics.log на `.17` (2026-10-22)

**Постановка.** На host `.17` soft-cold смотрит Avail **корня** `/` (≥80 ГиБ). На момент проверки корень был свободен (~156 ГиБ Avail, 28 % used), но том **Data** (`/media/user/Data`, 3.6 ТиБ) держал ~796 ГиБ под `TLAgent-20261020/runs`, в основном из‑за гигантских `Train/TimeLearnerTrainingDynamics.log` завершённых E2/G1 workdirs (типично десятки ГиБ на run, до ~87 ГиБ). Цель — **не удалять** логи, нужные для возможного разбора траектории Train, а **перенести** их в каталог offload на том же Data-диске с манифестом, оставив в workdir компактные артефакты анализа (audit / flag / Model / Test).

**Иерархия** к cold-результатам не менялась: перенос касается только файла Dynamics; Trainer×Mode / Span / NeuronModel / Mod остаются в исходных workdirs.

## Что сделано

| Поле | Значение |
|------|----------|
| Host | `.17` (`10.245.1.17`) |
| Источник | `/media/user/Data/TLAgent-20261020/runs/**/Train/TimeLearnerTrainingDynamics.log` (>50 МиБ) |
| Назначение | `/media/user/Data/TLAgent-offload/dynamics-logs-20261022/` (пути относительно `runs/` сохранены) |
| Манифест | `…/dynamics-logs-20261022/MANIFEST.tsv` |
| README | `…/dynamics-logs-20261022/README.ru.md` |
| Объём переноса | ~99+ файлов, порядка **~680+ ГиБ** (mv на том же FS; сжатие mid-size gzip в фоне) |
| Не трогали | активный E1.2 (`scratch/E1_2`), H2 TipR/KeepDone summaries (`h2_*summary.json`, `h2_result.json`) |

**Оставлено в workdir:** `TimeLearnerTrainingAudit.log`, `posttune_complete.flag`, `Model_00.xml` / `Parameters_00.xml`, Test CSV/gate, provenance / H2 JSON.

**Восстановление:** см. README в каталоге offload (`gunzip` / `mv` обратно в `runs/<rel>`).

## Параллель на `.17`

Пока offload шёл, на `.17` уже выполнялась нога **E1.2 noreset** (20 пачек) через `e1_2_repeatability.py`; локально — `run-reset`. G1 RERUN не запускался.

## Вердикт по диску

Корень `/` **не** был в зоне STOP (<80 ГиБ). Offload упорядочил Data и упростил `runs/`; полное освобождение Data зависит от фонового `gzip` mid-size логов (файлы ≥20 ГиБ оставлены несжатыми, чтобы не блокировать I/O). Долг `DEBT-disk-offload-policy` остаётся операционным правилом перед новым cold.
