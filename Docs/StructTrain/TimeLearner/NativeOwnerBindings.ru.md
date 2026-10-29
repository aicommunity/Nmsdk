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
Новая отдельная публикация этого Elder результата ещё требуется.

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

На workers запущен адресный gate: owner construction/import, 12 editor controls,
старые native editor regressions 2/20 кГц и cold training controls.
Пока он не завершён, editor fix считается исправленным в коде, а не принятым.
`owner_binding_evidence.py` проверяет матрицу 12 primary readbacks и реальные
boundary probe JSON/CSV. Повреждённые числа, подмена статуса, schema, hash,
источника или metadata запрещают положительный validation result.
Научный verdict этим модулем не формируется.

Runtime control flags, внешнее снятие IsNeedToTrain через связанный сигнал,
diagnostic output bindings, production recognition/PostTune wiring и полная
матрица всех lifecycle/storage режимов остаются отдельными пунктами полного
плана. Этот source не покрывается прежним full gate c7266dcb и не принят в develop.
