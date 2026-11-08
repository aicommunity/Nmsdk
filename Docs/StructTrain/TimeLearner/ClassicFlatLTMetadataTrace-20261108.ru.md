# Конкретные Classic LT-панели: цепочка Git metadata — 08.11.2026

Выполнена только локальная read-only проверка metadata и структурного XML из
Git. CSV не разбирались, сигналы не пересчитывались, PNG не строились/не
просматривались заново, модели не импортировались и серверы не читались.
**Причина flat LT panel остаётся неизвестной (`flat_cause=null`).**
Полные commit/path/blob/SHA/JSON pointers и границы доказательств:
[ClassicFlatLTMetadataTrace-20261108.json](ClassicFlatLTMetadataTrace-20261108.json).

## 1. К каким рисункам относится проверка

Из [исходного high-threshold отчёта](HighThresholdSinglePulseScientificReport-2026-11-07.ru.md)
взяты ровно три Classic Soma1 ссылки, сохранённые без изменения в main
`9a1098a1c76cbf7e7a275088475362931d36eb73`:

- `Classic-threshold-training100-retry32-burst-soma1-overview.png`;
- `Classic-threshold-training100-retry32-single-soma1-overview.png`;
- `Classic-threshold-training100-retry32-single-soma1-measured-peak-01055-detail.png`.

Их Git каталог —
`Reports/StructTrain/TimeLearner/s07-high-threshold-joint-visual-m40-a1`;
исходный visual evidence commit `8bc32a401e5b330597ee4f0328b6683f69ad6a7a`.
SHA каждого PNG сверён с original visual commit, main и сохранённым
`metadata/<case>/SHA256SUMS.json` для `soma-001/<view>.png`.
Metadata manifest связывает каждый view с Soma1 и соответствующим native source.
Это проверка цепочки bytes/ссылок, не новая визуальная или численная приёмка.

Каждый `<case>-source-reference.json` указывает на primary commit
`cd8d32168c3580948d0684f6ccad9f64f8527d94`, archive
`Reports/StructTrain/TimeLearner/s07-high-threshold-classic-normal-m40-a1/primary.tar.xz`,
member prefix `runs/Classic-threshold-training100-retry32-{burst,single}/native`.
Native archive: 6,265,296 compressed bytes, SHA256
`68ed19d2cc07afbd72336a25fc442bcdd31887dbec55ade32999101b74a4b872`.
У архива633 members; в этой узкой проверке15 выбранных JSON members сверены
с bundle sizes/SHA и execution.artifacts, где применимо. Полная прежняя
верификация633 файлов не исполнялась повторно и не выдаётся за новую проверку.
Все необходимые для этой metadata цепочки Git objects доступны локально.

## 2. Точный producer и renderer

`console-runtime.json#/source_closure` сохраняет:

| Роль | Фактическая source revision |
|---|---|
| compiled Root | `844b2789ea0c087c1a0f676d9584ce7b8a7a4d36` |
| compiled PulseLib | `1f97e4facc5bf03887bc337450190cc7b24c3ebf` |
| compiled Rdk | `10e9d05aa658dd2203c89bc84ba9166595b50014` |
| renderer tool | `360ed98641d89535363f472a577c6a6f9f7d3157` |

Native bundle также содержит tool Root9402e7… для того native/analysis задания;
это **не** подмена фактического renderer Root360ed…. Два проверенных renderer
modules совпадают с его сохранёнными `tool-source-hashes.json`. Нынешний Pulse88
source audit не принимается автоматически за исходник этого старого запуска:
его три LTZone files byte-equal фактическому Pulse1f97, NativeProbe.cpp отличается.

Actual auxiliary producer —
[`App/NeuroModelerConsole/TimeLearnerProbeChannelDiagnostics.h`](https://github.com/aicommunity/Nmsdk/blob/844b2789ea0c087c1a0f676d9584ce7b8a7a4d36/App/NeuroModelerConsole/TimeLearnerProbeChannelDiagnostics.h#L34).
На :37 он получает `NPulseLTZoneCommon`, на :38 требует nonnull;
на :39–40 записывает descriptor из GetCompClassName. На :57–61 читает
**напрямую `zone->Potential.GetData()`**, требует finite и сохраняет рядом
LT Output. Здесь нет cast к sibling NPulseLTZone и fallback нулём при
отсутствующем источнике. Диагностический observer не вызывает Calculate/Reset/Build.

`TimeLearnerProbeJob.cpp:183` создаёт observer; :201–203 вызывает его из существующего
onSample после `evidence.Sample(sample)`; :217 сохраняет `probe_diagnostics_1.json`.
В actual raw descriptor записаны `$.LTZone.Potential`, component_class
`NPulseLTZoneThreshold`, units=`model_units_SI_unverified`,
phase=`native_after_children`. Producer маркирует запись complete.
Это source/metadata binding; per-tick выполнение LT component им не измеряется.

Renderer
[`channel_diagnostic_reports.py:32–52`](https://github.com/aicommunity/Nmsdk/blob/360ed98641d89535363f472a577c6a6f9f7d3157/Scripts/StructTrain/TimeLearner/channel_diagnostic_reports.py#L32)
читает этот файл, находит index descriptor по path и берёт соответствующую
колонку `samples[].values`. Панель называется `Recorded LT decision potential`.
Threshold извлекается из actual initial-state node LTZone; отсутствующий path
не заменяется `.get(...,0)`. В этой проверке ordinates массива не анализировались.

## 3. Что подтверждает сохранённая модель

Для burst и single совпадают полные identity dictionaries source-import,
initial-state, final-state и сохранённого stopped native graph. Зафиксированная
model revision: `913bd90b0a27697f237f08771db1b9431db64a86ac5d43a192f7610a80d71d04`.
Это равенство опубликованных структурных описаний, не новый native import.

| Свойство | Доказательство в опубликованных metadata |
|---|---|
| LT image/class label | `identity.model.nodes[path=$.LTZone].class = NPulseLTZoneThreshold`; такой же diagnostic descriptor и XML Class |
| C++ implementation | compiled NPulseLibrary регистрирует это имя через `new NPulseLTZoneThreshold`; saved class definition kind=`native_required`. Отдельный per-object runtime RTTI/typeid не сохранён |
| LTMembrane | parent LTMembraneClassName пустой; ни узла `$.LTMembrane`, ни его descendants нет; saved XML также без него |
| Activity | LTZone Activity parameter=true, source XML Activity=1; это snapshot, не журнал флага на каждом sample |
| Clock/threshold | LTZone frequency_hz=`2000`; effective-models сообщает Threshold100, encoded parameter сохранён отдельно в JSON trace |
| Child order | в parent child_order Soma1..Soma4 идут перед LTZone; затем PosGenerator/NegGenerator. Такой же порядок в saved XML Components |
| Inputs links | восемь property_pointer bindings Soma1..4.Exc/InhChannel.Output → LTZone:Inputs, slots0..7 |
| Feedback links | четыре bindings LTZone.Output → Soma1..4.InputFeedbackSignal |
| Cache pointer | root cache содержит cached_ltzone=`$.LTZone`; это не запись active calculation cache membership |

GetCompClassName, graph.class и XML Class идентифицируют registered image.
Согласованная регистрация в compiled source уточняет ожидаемый C++ класс, но
не заменяет независимую запись RTTI конкретного объекта. Это различие сохраняется
в машинном отчёте; названия произвольных пользовательских images не принимаются
за universal class whitelist.

В фактическом Pulse1f97 `NPulseLTZoneThreshold` использует inherited Potential:
Common::ACalculate суммирует Inputs, применяет averaging, пишет Potential и
вызывает Threshold::ACalculate2; CheckPulseOn сравнивает Potential с Threshold.
Эти LTZone исходники проверены byte-equal Pulse88. Поэтому metadata/source
цепочка не подтверждает гипотезу, что эта Threshold реализация игнорирует Potential.
Отдельная LT-мембранная RC-инерция отсутствует в **этом сохранённом графе**;
это не утверждение, что отсутствует вся body/synaptic динамика.

## 4. Чего эта публикация не фиксирует

В initial/final semantic nodes и source native XML нет отдельных runtime
`InitFlag` или `Ready`. Published graph содержит Activity, child_order, Inputs
bindings и cached_ltzone; actual вызов ACalculate, активный cache membership и
их порядок на каждом отсчёте отдельно не записаны. Поле phase — метка producer
boundary, а не per-component execution trace.

Stopped package и neuron archive имеют dynamic_checkpoint=false; initial-state
также dynamics_checkpoint=false. XML State содержит Potential/Inputs и другие
динамические поля, но это не делает его исполняемым checkpoint той конкретной
sample phase. Сохранённые state values здесь не используются для объяснения
плоской панели. Корректность нового import/Reset/Calculate из них не выводится.

`record_spikes=false` записан в probe configuration. Он не означает zero physical
spikes и сам по себе не выключает LT. Auxiliary diagnostics имеют собственное
сохранение LT Output/event history. Их значения в этой metadata проверке не
переоценивались; прошлые наблюдения отчёта остаются в исходной области.

Следовательно, нет доказательства wrong cast/fallback zero, отсутствующей
LT Inputs связи или отдельной LTMembrane в этих snapshots. Но нет и достаточных
данных, чтобы выбрать причину flat panel: lifecycle/calc-state и прямое
сопоставление comparator inputs в момент samples остаются неизвестными.
`flat_cause=null`; graph/physics defect и scientific causality не подтверждены.

## 5. Следующая необходимая запись, только после отдельного review

Для сужения причины нужны связанные с тем же source/моделью и sample phase
runtime Ready/Init/Activity, фактическое выполнение LT ACalculate/active cache,
и comparator input/readback вместе с soma/zone signals. Missing read должен
отказаться либо стать unknown, а не 0. Новая инструментальная запись может быть
отдельным owned серверным заданием, но **не** перезапуском старого evidence и
не незаметной правкой физики. Этим документом она не реализована/не запущена.

Исходные JSON/CSV/models/PNG, positive blue Soma.SumPotential, threshold100
наблюдения и августовские визуально подтверждённые4/8–6/8 не изменены. Ни один
новый максимум, единицы SI, response mechanism или training verdict здесь не
вычислялся. Краткая карта общего source dataflow остаётся в
[LTSomaSignalSourceAudit-20261108.ru.md](LTSomaSignalSourceAudit-20261108.ru.md).
