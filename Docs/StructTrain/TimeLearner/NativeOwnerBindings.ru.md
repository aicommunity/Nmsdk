# Владение параметрами при native construction/import/edit

Рабочий подэтап этапов 4–6. Это согласование learner с действующей семантикой
Rdk, а не запрет связанных параметров и не новая физическая модель.

## Два разных механизма Rdk

`IsConnected` / `SetPointer`: значение читается из подключённого источника;
`SetDataDirect` не применяет предложенное локальное значение. Входной vector
коллектор собирает scalar outputs. Vector-to-vector SetPointer не является
этим протоколом. `UsesExternalDataSource` — другой механизм: запись может быть
передана внешнему источнику. Нельзя считать эти способы взаимозаменяемыми.

Для обоих механизмов native ownership использует правило:

```text
before changing the physical model:
    collect all metadata values required by the candidate
    for every externally supplied field:
        require current readback == candidate value

after verified physical commit:
    verify mirror values again
    write only changed locally owned fields
    leave matching external fields connected and do not write their sources
```

Конфликт обозначается `native_model_owner_assignment_is_external:<property>`.
Это специализированная диагностика; bool Build/Reset/Calculate не меняется.
Новые Calculate/Build внутри контроллера не добавлены.

## Проверенные дефекты и границы

Construction/import исправлены в PulseLib `cbbf56ce541027ef8e07d6be7a1841cf513b2b8e`:
проверка actual private preview либо подготовленного import выполняется до
замены живых детей. M40 ASan: 16/16 controls и независимое чтение 16 primary
JSON. Пакет `s04-owner-bindings-m40`, commit
`1c55f903d9d30e1367a30461c5f5f7b1a92f30c3`, 467 stored / 465 raw hashes проверены.
На Elder normal та же Core implementation прошла 16 controls в editor-baseline A1.
Этот Elder контроль включён в baseline package 2c08b5b4 ниже.

Editor baseline root `03fd6e4704859ea5b84db0f20b122b8bf068a121`, PulseLib
Core cbbf56ce: на Elder normal и M40 ASan по 12 controls — 6 matching pass и
6 ожидаемых conflict failures. Primary JSON показывают `Applied`, изменение
physical model revision и старое значение связанного owner поля. Воспроизведены
`DendriteLength`, `NumSynapse`, `TipSynapseResistance` для обеих топологий.
Источники SetPointer не перезаписывались: дефект — несогласованная metadata.

Первый editor fixture root `bf22a1fcf164bc0073978c4a2515f1ec486f0d25`
не выполнял предварительную пробу и отклонялся корректной защитой
`native_edit_requires_consumed_probe_boundary`. Все 12 таких failures — ошибки
постановки теста, не подтверждение исследуемого дефекта. В A2 выполняется
полная native проба, наблюдение проверяется и забирается перед редактированием.

## Исправление editor

PulseLib `0ca75b3e5b7354ee801645d5d0d73b3f942cb645`, root
`796a73075b930d634c905355541e47187aed6f5f`: общий visitor трёх параметрических
векторов используется для preflight и последующего зеркалирования.
Native editor уже требует `preview parameters == requested` и точного
совпадения live readback с requested; поэтому проверяется весь candidate,
а не приблизительная оценка либо unclipped сопротивление.

Обе реализации ApplyNativeParameters выполняют preflight до physical editor.
При Applied зеркалирование не пишет в внешние источники. Кэши обученных Rs/L
обновляются из подтверждённых значений. Обычные изменяемые локальные параметры
продолжают работать; совпадающее read-only поле не мешает менять другое поле.

Поздняя смена источника из callback может дать Failed с
`modelMayHaveChanged=true`; этот подэтап не объявляет весь внешний callback
транзакцией с гарантированным rollback.

## Приёмка и оставшаяся работа

На обоих workers завершён адресный gate: **46/46 native без skips/failures**
(16 construction/import, 12 editor bindings, 14 editor regressions, 4 cold
training). Elder normal, M40 ASan. По 2/2 Python tests из native source прошли;
дополнительный auditor source 07e66559a4030537ed24605fcdb676838b94b257 также
прошёл по 2/2 tests и связывает pre-edit модель с первичной boundary пробой.
На каждом worker проверены 12 complete probes / 4332 samples.

Fixed пакеты: [Elder](../../../Reports/StructTrain/TimeLearner/s04-editor-fixed-elder1/README.md)
073b2906e6926f026f9a2c55ee1b69475f49a9ff и
[M40](../../../Reports/StructTrain/TimeLearner/s04-editor-fixed-m40/README.md)
37e6326c98bcd74d859ff3381acf90514763905a; по 530 stored / 528 raw hashes
проверены локально. Baseline: 2c08b5b4c0a2fb7f359a31609e13d8d6a73f2d13 /
1e9e52f225b6cec1b5b8cde51b30b65c7abdd869, по 331 stored / 329 raw hashes.
Elder пакет после пересечения двух локальных Git index operations восстановлен
из точного evidence commit; все hashes повторно проверены. История не переписана.
`owner_binding_evidence.py` проверяет матрицу 12 primary readbacks и реальные
boundary probe JSON/CSV. Повреждённые числа, подмена статуса, schema, hash,
источника или metadata запрещают положительный validation result.
Научный verdict этим модулем не формируется.

Runtime control flags, внешнее снятие IsNeedToTrain через связанный сигнал,
diagnostic output bindings, production recognition/PostTune wiring и полная
матрица всех lifecycle/storage режимов остаются отдельными пунктами полного
плана. Этот source не покрывается прежним full gate c7266dcb и не принят в develop.
