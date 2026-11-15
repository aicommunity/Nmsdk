# Условная диагностика объявленных временных масштабов

Перенос двух связанных аудиторов из Bin прошёл общий набор143/143 на M40 и143/143 на Elder:67 wire +39 collector +30 новых диагностик +7 lossless ConfigDocument. Source `4e9aff7b72d3cc2460c6d9c886e0f2d7e39d5277`. [Квитанция M40](DeclaredTimeScalesScript143M40A2Verification.json), [квитанция Elder](DeclaredTimeScalesScript143ElderA1Verification.json) подтверждают exact IDs/CLI/log/JUnit, десять actual Bin Project.ini blobs, source/fixture bytes до/после, закрытие owned groups и освобождение leases. Старые entrypoints удалены без wrappers в Bin `8cb6dba07b30432272984c8ce3136b48ad06f064`; это перенос активной функции, а не удаление научных данных. [Migration record](DeclaredTimeScaleAuditorMigration.json) содержит точные Git-источники и проверку области изменения. Точное происхождение,
caller search и список30 тестов находятся в
[DeclaredTimeScalePortPreparation.json](DeclaredTimeScalePortPreparation.json).

Первый прогон143 на M40 source76 дал142 PASS/1 ERROR: ветвевой `import subprocess` делал это имя local для всего main, из-за чего handler ошибки no-overwrite сам завершался UnboundLocalError. Исправление удаляет только этот import, используя общий module binding. [Отрицательная квитанция](DeclaredTimeScalesScript143M40A1NegativeVerification.json) сохранена; ошибка не скрыта повторным успешным прогоном. Повторный M40 и Elder использовали одинаковые143 IDs и один source4e9. Python3.10/3.12 печатают разные формы test description; reader сопоставляет фактически напечатанное имя с единственным declared ID, сохраняя raw logs.

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

Набор содержит 30 новых meaningful tests: реальные numeric tags/attributes,
неизвестные clock/defaults, зарегистрированные образы, empty/invalid modes,
конечность произведения/обратной величины, границы, frozen snapshot hash,
symlinks/size budget, переносимый Git discovery и production CLI. На обоих
серверах пройден gate вместе с 7 существующими lossless ConfigDocument tests и
декларированным корпусом 10 реальных Project.ini. Полная адресная
script-only регрессия — 143 = 67 wire + 39 collector + 30 новых + 7 parser.
Локально допускаются только source/AST/Git/JSON проверки; C++ и модели в scope
этого переноса не входят.

После source/migration review и двухсерверной приёмки удалены ровно два
entrypoints, без wrappers и сохранения исторических копий в current tree.
Полные source SHA, blob IDs, last-path commits и пути зафиксированы в
[migration record](DeclaredTimeScaleAuditorMigration.json). Исходная
[preparation](DeclaredTimeScalePortPreparation.json) остаётся снимком подготовки.
Единственный исполняемый caller — импорт tree-аудитором step-аудитора; других
совпадений в Pulse/Rdk нет. Dated inventories и raw Reports остаются historical
snapshots; две ссылки в историческом audit-документе теперь указывают на
полный Git source commit. Старые исследовательские JSON/CSV сохраняются.
Manifest содержит 356 записей: 352 retired и 4 moved_to_root; complete=false.
Это адресный перенос двух аудиторов, без приёмки всего этапа9 или научной серии.

Весь новый manifest356 проверен production history CLI на M40: evidence `b553f9c7f253c2dcc09cd992bad4059dd9d555e5`, [независимая квитанция](DeclaredTimeScaleMigration356M40A2Verification.json). Проверены исходные Git blobs всех356 записей, отсутствие старых путей, четыре Root replacements и сохранность первых354 записей. Сравнение производится по canonical Git bytes; неуспешная проверка materialized preimages в private worktree не объявляется успешной и не заменяется предположением о CRLF.

Первый preflight356 отказал до CLI и до создания kernel unit: непреднамеренный import без `-B` создал восемь ignored pyc в projection инструмента, strict source snapshot их отклонил. [Отрицательная квитанция](DeclaredTimeScaleMigration356M40A1NegativeVerification.json), evidence `0f85945acba4027aa402bbb40b528b6f83e406e1` сохраняют0 checks, исходные cache identities и erratum неточного lease note: kernel closure в этом отказе не было и не утверждается. Повтор использует fresh Git projection и `-B`, без ослабления guard, удаления failure evidence или запуска исторических скриптов.
