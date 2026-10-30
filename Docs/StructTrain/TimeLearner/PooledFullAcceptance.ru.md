# Приёмка native completed state после pooled bindings / Default: 28.10.2026

Оба `s05-pooled-full-a3` завершились штатно. Проверенная исходная комбинация:

| Репозиторий | Tested SHA | Merge в develop, дерево файлов совпадает с tested |
|---|---|---|
| Root | `7fb92a4a57b9773ff56996cf2c7b8c75b2746cd8` | Закрываемая ветка `stage05/native-trained-state` обновляет точные gitlinks дочерних merge commits |
| PulseLib | `4919bac2bd359118b13310862e54bcd24492967d` | `caf19a343b62e96c5076e84b6c4c2710114128bc` |
| Rdk | `1223bcc18cf1ba106e8f8a17f20cce8c000c104d` | `1812624ff75c60f03ad57c10b379d3e3848590bc` |
| Bin | `f5e1d0200127223981daa71da22cf5ee02fdbc60` | Не менялся |

Child merges выполнены через `--no-ff` и опубликованы до корневого gitlink
commit. `git diff tested HEAD` в каждом дочернем репозитории пуст. Это не
перенос более поздней stopped-state или dynamic-domain реализации.

## Проверки и доступные свидетельства

| Worker | Выбранные maintained CTest suites | PulseLib parent | Python / первичные данные |
|---|---|---|---|
| Elder-1, Qt5/GCC11 | 4/4 passed | 397 cases: 387 pass, 10 skip, 0 failures/errors | 9/9 tests; 16 learned packages, 208 trial JSON/CSV |
| M40, Qt6/GCC13 | 4/4 passed | 397 cases: 387 pass, 10 skip, 0 failures/errors | 9/9 tests; 16 learned packages, 208 trial JSON/CSV |

Четыре suites: `PulseLib_StorageComponents`, `Test_UComponent_Properties`,
`Test_UComponent_Lifecycle`, `UContainer_Components`. Это полный проход этих
maintained groups, а не утверждение о запуске всех CTest targets проекта.
Десять skips: восемь opt-in compatibility cases и два свежепроцессных helpers;
они не подтверждают пропущенное поведение. Там, где требуется, parent cases
реально запускают helpers и проверяют результаты.

Git-пакеты:

- [Elder-1](../../../Reports/StructTrain/TimeLearner/s05-pooled-full-elder1/README.md),
  commit `abfe546f8070c85acf1a73c40a8d8837fcc1bd12`.
- [M40](../../../Reports/StructTrain/TimeLearner/s05-pooled-full-m40/README.md),
  commit `9beb55673fa934c308dcdf050876d70c823ea84c`.

На каждой стороне опубликованы runtime/reuse manifests, post-run source closure,
все parent/child XML, журналы, модели и исходные наблюдения. Post-run source
closure равна build closure; executable SHA256 не изменился. Локально проверены
по 1859 stored hashes и 1857 raw gzip payloads, всего 3718 / 3714.

A3 использует неизменённый A2 runtime после preparation-only ошибки launch;
эта связь явно записана. Прежние A1 остаются interrupted_by_user. Pre-fix
full failures и audit-default baseline failures сохраняются как отдельные
исторические попытки. Новое успешное свидетельство не переписывает их исходы.

## Что именно принимается

Устранённый Rdk pooled direct-source / Copy defect, явный Default audit flag
обоих learner и tested native completed solo-state export/import с их ранее
опубликованными addressed, ASan, rollback и cross-host проверками. Пятнадцать
переносов, отказавших в pre-fix full runs, теперь проходят maintained suite.

Это не весь этап 4 или 5. Recognition/conversion, PostTune/calibration, вся
физическая матрица, runner/migration и научные эксперименты остаются открытыми.
Количество пакетов не означает столько Exact trainings: native certificates
содержат реальные residuals и допускают SearchUnresolved. Независимый auditor
подтверждает согласованность данных, не научную разделимость. ControllerVersion=2
ещё не рекомендуется для всей матрицы. Августовские 4/8–6/8 этим не отменяются;
серия D не возобновлялась.
