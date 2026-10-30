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
rejected packets, а также явно помеченные повреждённые копии. Реальный rejected
fixture имеет observation с нулём samples; отсутствие observation проверяется
отдельным synthetic wire control, а не объявляется новым native-наблюдением.
Добавлен actual Classic frozen trace с шестью soma из ранее опубликованного
pooled-full контроля: каждая soma получает отдельные крупные figures. Его
широкий timing tolerance служил transport/dimension control, а не доказательством
сходимости при default 0.02. На Elder первый diagnostic gate прошёл 22/22 tests
без skips/errors. Final renderer `9abd0b0049071eabc233cd644f7bfe3fd5dde7dc`
прошёл по 23/23 tests на обоих workers, включая actual six-soma control.
Пакеты: [Elder](../../../Reports/StructTrain/TimeLearner/s09-probe-diagnostics-elder1-a2/README.md)
`2aeafe06bd451fb6f5e2b9d0d9a483eea2bb4f2d`,
[M40](../../../Reports/StructTrain/TimeLearner/s09-probe-diagnostics-m40-a2/README.md)
`5bb64774268ef3815e457e0eda06a7c0e6254a84`.
Локально проверены 1162/609 первоначальных stored hashes; добавленные записи
agent visual review и обновлённые manifests содержат 1163/610 файлов.
Открыты четыре source-bound Poppler previews: actual partial Branch и soma 6
на каждом worker. Подписи читаемы, легенда не перекрывает axes, цензурированный
хвост явно неизвестен. Это scoped agent QA; human review не заявлен.
Приёмка данного адаптера не является полной визуальной приёмкой матрицы.
Historical schema adapters и вся physics/frequency matrix остаются отдельными
требованиями полного плана.

Последующее усиление: один конечный sample нельзя показывать только линией,
поскольку сегмента между двумя точками ещё нет. Для partial traces добавлены
различимые marker shapes soma/input; NaN по-прежнему разрывает данные. Отдельный
wire control обрезает реальный trace до одного отсчёта и проверяет наличие
обоих data markers внутри SVG axes, а не только существование файла.

Финальный renderer `71c41c341777901b494e2f1a4f2aa593349dbd01` сохраняет
обрезку самой waveform по рамке временного окна, но показывает целиком маркеры
всех попавших в окно отсчётов, включая крайние. A1 имел обрезанный рамкой
крайний marker; A2 снимал clipping со всей waveform и отклонён при проверке кода
из-за риска выхода других временных фрагментов за axes. Эти варианты сохранены
как история, не приняты как финальные визуальные результаты.

A3 прошёл 24/24 tests на каждом worker, без skips/errors/failures. SVG проверка
отдельно требует clipping waveform и отсутствие clipping у data markers.
Reports: Elder `36c8d662f5c5bcd8131369976d979ab7cb9bb785`,
M40 `244b9e252bb22d5a57f5804ae58b15c558be8bf6`;
проверены все 635 первоначальных stored hashes каждого пакета.
Просмотрены четыре Poppler previews: single-sample control и actual partial
Branch на обоих workers. Крайние glyphs целы, легенда и подписи читаемы,
неизмеренный хвост обозначен явно. Scoped agent review записан в каждом
`pdf-qa/agent-review.json`; после добавления записи manifest содержит 636 файлов.
Это не human review, не visual acceptance всей матрицы и не полный отчёт новых
repeat-boundary A3 native trials: для них полный набор графиков ещё требуется.
