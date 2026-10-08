# Evidence bundle: выборочный Rs/Rm и D-ретест

`rsratio-evidence-20261008.tar.gz` содержит 219 компактных файлов выбранных запусков:

- `provenance.json`, input manifests, финальные `Train/Parameters_00.xml` и reset contracts;
- `TimeLearnerTrainingAudit.log`, `tipr_final.txt`, post-tune flags и выборочные gate CSV/debug outputs;
- stdout/stderr runner-логов с кодами завершения;
- извлечённые строки `ColdTipResistanceInit` для проверки начальных Rs и Rm;
- `build_and_revision.txt` с SHA root/Bin/PulseLib/Console.

В архив **не** включены объёмные `StatisticLog` и полные `EventsLog`. Полные отдельные run directories остаются на сервере в `/home/user/Nmsdk_RsRatio_20261008/Bin/Configs/SpikeSamples/StructTrain/_repro/runs/`, а batch logs — в `/home/user/Nmsdk_RsRatio_20261008/_audit_runs/rsratio_selective_20261008/logs/`.

SHA-256 архива: `649ea02de5f9c00ed46426f6134bd6362b78c6de4296ff0335b7ce74c78a5d32`.

Список членов без распаковки: `tar -tzf rsratio-evidence-20261008.tar.gz`.
