# Условная диагностика объявленных временных масштабов

Это source-only перенос двух связанных аудиторов из Bin. Серверные проверки
ещё не выполнялись; старые entrypoints пока не удалены. Точное происхождение,
caller search и список 30 подготовленных тестов находятся в
[DeclaredTimeScalePortPreparation.json](DeclaredTimeScalePortPreparation.json).

Корневой модуль `Scripts/StructTrain/TimeLearner/declared_time_scales.py`
вычисляет условный `Q=C*R*f` только для явно заданных конечных положительных
факторов, конечного положительного произведения и обратной величины. Это
диагностика при предположении нулевой проводимости. Она не проверяет выбранный
интегратор, фактическую проводимость, effective model или storage. Во всех
результатах `integrator_stability_verdict` и `scientific_verdict` равны `null`;
применимость физики остаётся `unknown`. Название в `Class` может обозначать
зарегистрированный образ: whitelist C++ classes не используется.

## API и CLI

`audit_declared_pair(project_raw, parameters_raw, ...)` получает байты, которые
одновременно разбираются и хэшируются. `audit_case(...)` использует уже
существующее стабильное чтение regular non-symlink файлов из collector helper.
`audit_config_tree(...)` требует явного режима поиска: layout `matrix`
(`W*/inputs/*/Train/Parameters_00.xml`) либо `tracked-tree` по Git index.
Положение Bin относительно корневого репозитория не предполагается. Git HEAD
конфигов является отдельной метаданной и не подменяет хэш реально прочитанных
working-tree bytes. Атомарность нескольких файлов и loaded-code execution
этот отчёт не аттестует; для воспроизводимого запуска нужен отдельный pinned
source/owned-runner receipt.

```text
python -m Scripts.StructTrain.TimeLearner audit-time-scales \
  --config-root /absolute/config/tree --discovery tracked-tree \
  --output /existing/output/directory/report.json
```

Новый CLI пишет строгий JSON и не перезаписывает существующий output. Код 0
означает полное покрытие объявленной условной диагностикой; это не физическая
приёмка. Пустое либо неполное покрытие даёт код 2 с сохранёнными причинами.
Режим `--frequency-hz` явно помечен как hypothetical override и не объявляется
измеренной частотой. Недостающий Project.ini никогда не заменяется на 2000 Hz.

Clock связывается с единственным каналом `Project/Channels/<номер>` по точному
`ParametersFileName`. `GlobalTimeStep=0` использует только явно сохранённый
положительный `DefaultTimeStep`. Отсутствующие/дублирующиеся поля, неоднозначный
канал или `UseIndTimeStepFlag=1` оставляют clock неизвестным. Явный компонентный
`TimeStep` требует effective resolution и не подменяется global/override.
Как и прежний статический аудитор, перенос консервативно оставляет clock
неразрешённым для всего документа при любом сохранённом TimeStep, включая
ancestor/group: выбор наследования без effective readback не имитируется.

Парсер `ConfigDocument` сохраняет реальный диалект Rdk, включая `<00>`, UTF-8
BOM, комментарии и entities. Маленькое расширение Node предоставляет read-only
view уже разобранных attributes; editing semantics и lossless tests сохраняются.
Новый XML/regex document parser не добавлен.

## Ошибки и границы сравнения

Пустые параметры и отсутствие пригодных RC modes имеют `not_assessed`, а не
положительную классификацию. Неверные Capacity/Resistance не исчезают: их блоки
и причины остаются в отчёте, включая соседство с корректным mode. Проверяются
ноль, отрицательные/nonfinite значения, underflow/overflow произведения и
nonfinite reciprocal. Малформатный case не удаляет остальные cases дерева.

Одна явная политика `binary64-exact-declared-q-v1` использует точные сравнения
с 0.5/1/2 и относительный допуск 0 как для bands, так и для counters. Это
намеренно устраняет расхождение прежних двух скриптов около границ. Старые JSON,
CSV и выводы экспериментов не пересчитываются и не переписываются.

## Проверки и миграция

Подготовлены 30 новых meaningful tests: реальные numeric tags/attributes,
неизвестные clock/defaults, зарегистрированные образы, empty/invalid modes,
конечность произведения/обратной величины, границы, frozen snapshot hash,
symlinks/size budget, переносимый Git discovery и production CLI. Обязателен
серверный gate вместе с 7 существующими lossless ConfigDocument tests и
декларированным корпусом не менее 10 реальных Project.ini. Предлагаемая полная
script-only регрессия — 143 = 67 wire + 39 collector + 30 новых + 7 parser.
Локально допускаются только source/AST/Git/JSON проверки; C++ и модели в scope
этого переноса не входят.

До root review source/migration scope и серверной приёмки оба старых файла Bin
остаются на месте. После review удаляются ровно два entrypoints, без wrappers
и сохранения исторических копий в current tree. Полные source SHA, blob IDs,
пути и все 13 найденных точных текстовых ссылок зафиксированы в preparation.
Единственный исполняемый caller — импорт tree-аудитором step-аудитора; других
совпадений в Pulse/Rdk нет. Dated inventories и raw Reports остаются historical
snapshots; две ссылки в историческом audit-документе должны указывать на Git
history/migration record после удаления. Старые исследовательские JSON/CSV
сохраняются. Retirement и изменение gitlink Bin — отдельный последующий этап.
