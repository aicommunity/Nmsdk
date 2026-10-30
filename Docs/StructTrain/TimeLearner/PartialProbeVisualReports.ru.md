# Графики неполных и невалидных native-проб

Рабочий подэтап `codex/timelearner-probe-diagnostics`, продолжение обязательных
[визуальных отчётов](VisualTestReports.ru.md). Он не меняет проверку обучения,
сертификаты и научный verdict.

## Явный режим

Обычный `--format probe` и schema-1 probe-set продолжают требовать полный
положительный primary audit. Для диагностики отдельной пробы:

```text
python3 -m Scripts.StructTrain.TimeLearner report probe.json --format probe-diagnostic --trace probe.csv --output NEW
```

Для набора schema 2 требует явное `observation_policy: complete_or_partial`:

```json
{"kind":"timelearner_probe_report_spec","schema_version":2,
 "observation_policy":"complete_or_partial",
 "trials":[{"trial_id":"ACTUAL_ID","packet":"probe.json","trace":"probe.csv"}]}
```

Команда остаётся `report spec.json --format probe-set --output NEW`. Portable
report-spec сохраняет policy; при повторном построении она не теряется.

## Что проверяется и показывается

- Полная валидная проба проходит прежний строгий audit даже в diagnostic mode.
  Этот режим не обходит ошибки положительного observation или неизвестную схему.
- Для неполной schema-3 observation проверяются identity/request/context,
  actual profile, заголовок и размерность CSV, sample count, конечные и строго
  возрастающие timestamps в окне. Это проверка структуры временного ряда,
  а не действительности peak assignment или сертификата.
- Показываются все сохранённые samples, реальные input samples и исходные soma
  values. Ненаблюдавшиеся промежутки и хвост выделяются серым; между пропусками
  линия не соединяется. Нет восстановления импульсов по ISI.
- NaN/Inf ординаты в явно невалидной пробе сохраняются в primary CSV и видны
  как разрывы; их позиции указаны в manifest. Они не превращаются в нули и не
  участвуют в Y limits. Нечисловой токен, NaN timestamp, ragged CSV или неверный
  count запрещают построение. Полная заявленно валидная проба с NaN отвергается
  прежним primary audit.
- Нет observation — нет придуманной кривой и абсолютной оси времени. Для
  header-only CSV сохраняются primary files и диагностический index; число
  наблюдённых soma неизвестно, а не равно нулю. Samples без observation context
  отвергаются. Это не подтверждение полноты измерения пустым placeholder.
- Общие Y limits набора вычисляются только по конечным исходным значениям.
  Крупные PNG 1920×960, SVG/PDF, overview/zoom/detail сохраняют прежний масштаб.
  Канал без конечных samples остаётся явно недоступным, без выдуманного Y-range.

## Состояния и доказательства

Schema-2 report хранит `trace_quality` отдельно от `primary_audit`: проверка
сырых CSV не меняет `valid_observation=false`. `observed_soma_count=null`
означает отсутствие observation context. Manifest набора разделяет известные
пары trial–soma, реально построенные кривые и trials с неизвестной размерностью.
`data_complete=false`, `visual_acceptance_complete=false` и null scientific
verdict не подменяются наличием HTML/PNG. Model revisions и raw hashes сохраняются.

Механическое выделение общего loader выполнено отдельным commit
`f2294039845b0305f66e94bb67044a8bebdbd7f1`: на Elder 15/15 прежних tests
без skips/errors. Новые адресные проверки используют реальные cancelled и
rejected packets обоих топологий и явно помеченные повреждённые копии. До
публикации результатов и визуального просмотра новый подэтап не принят.
Historical schema adapters и вся physics/frequency matrix остаются отдельными
требованиями полного плана.
