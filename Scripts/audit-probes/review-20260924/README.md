# Дополнительные воспроизведения аудита 2026-09-24

[Отчёт](../../../Docs/Audit/TimeLearner-2026-09-24-review/README.md) и [сохранённые результаты](../../../Docs/Audit/TimeLearner-2026-09-24-review/evidence/probes-summary.json).

Это исследовательские контрпримеры, не зелёный regression gate. Exit 0 скрипта означает, что опыт выполнен; его вывод может демонстрировать ошибочное поведение. Полный Rdk/Console/cold replay не запускается. Production-файлы не меняются; результаты пишутся в build/audit-review-20260924.

## Python

Из корня репозитория, Python 3.10+:

```text
python -B Scripts/audit-probes/review-20260924/verifier_probes.py
python -B Scripts/audit-probes/review-20260924/metrics_probes.py
python -B -m unittest discover -s Bin/Configs/SpikeSamples/StructTrain/scripts/tests -v
```

verifier_probes вызывает реальные run_case/validator/overlay/salvage с временными файлами. Внешние Train/gate и Popen подменены: эти fixtures проверяют приёмку и происхождение данных, а не физику. Старый Asym50 flag берётся из tracked-файла. metrics_probes сравнивает реальный scorer Bin d2361191 и текущий; требует доступной локальной git-истории.

## C++ PostTune

```text
python -B Scripts/audit-probes/review-20260924/posttune_probes.py
```

Скрипт извлекает текущие FinalizePostTuneMid/UpdatePostTuneFreeRunPeak TL и Branch, а также soma accumulator из Branch ACalculate. Подменены framework, время и входной scalar signal. Для исторического среза 17854a4 извлекаются Finalize/Handle и соответствующие helper cpp/header. Тела production-методов не редактируются.

Build recipe записан для данной Windows-машины: MSVC 14.44.35207, Windows SDK 10.0.26100.0. На другой машине настройте toolchain либо скомпилируйте сгенерированные C++17-файлы своим компилятором. Сохраняются compiler logs, исходники и результаты; GTest не требуется.

## C++ Analyzer

```text
python -B Scripts/audit-probes/review-20260924/generate_analyzer_probe.py
```

После этого в x64 Developer PowerShell:

```powershell
cl /nologo /EHsc /std:c++17 build/audit-review-20260924/analyzer/analyzer-boundaries.cpp /Fo:build/audit-review-20260924/analyzer/analyzer-boundaries.obj /Fe:build/audit-review-20260924/analyzer/analyzer-boundaries.exe
& ./build/audit-review-20260924/analyzer/analyzer-boundaries.exe
```

Извлекаются реальные ACalculate, BeginTrial, AppendStim, IsPatternComplete, MaybeClassifyFire, AttributeNeuronToActiveTrial и ResetTrialState. Dataset identity/clock/edges — адаптеры; CloseTrial сохраняет наблюдаемые поля и вызывает настоящий ResetTrialState. I/O и scheduler не моделируются. Coincident sample advance/stimulus fixture проверяет условный переход, а не доказывает его частоту в настоящем Dataset.

Исторический и текущий analyzer-срезы для исходных A01–A04 сохранены как [analyzer-historical.cpp](../../../Docs/Audit/TimeLearner-2026-09-24-review/evidence/analyzer/analyzer-historical.cpp) и [analyzer-current.cpp](../../../Docs/Audit/TimeLearner-2026-09-24-review/evidence/analyzer/analyzer-current.cpp), со source hash. Их можно отдельно собрать C++17-компилятором.

Обычный набор GUI/CE/Branch остаётся в [родительском README](../README.md); A12 исключён из обязательного gate.

После remediation R01–R07 (2026-09-24): production Update/Finalize/analyzer изменены. Пересоберите probes и ожидайте, что прежние контрпримеры timeout/NaN/stale Success / incomplete_sample / branch_ltz_mode **перестанут** демонстрировать ошибочный mid/Success (exit 0 скрипта по-прежнему = «опыт выполнен», не quality PASS). См. [REMEDIATION_NOTES.ru.md](../../../Docs/Audit/TimeLearner-2026-09-24-review/REMEDIATION_NOTES.ru.md).
