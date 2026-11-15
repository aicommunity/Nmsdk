# LT overview: читаемый диапазон без растягивания до порога — 09.11.2026

Статус: **renderer source candidate, новые проверки и render не запускались**.
Base Root `85b1d24ab7e216285e90f5c65117b44cc35fb2c7`.
[Машинный source/image review](ChannelLTOverviewReadabilitySourceReview-20261109.json)
фиксирует Git bytes, существующий image QA, candidate blobs и14 literal test IDs.

## Что видно в уже опубликованной паре изображений

Локально просмотрены ровно два exact Git8bc PNG из исходного отчёта:

| Classic single / Soma1 | SHA256 |
|---|---|
| overview | `a0824f6970e735053ca135800d71c675541f2b36882040aa2f9575daac221d47` |
| measured-peak-01055-detail | `dddd6cf29d7db15a2cbbf9b54862ec52f392e69b53f251aa9c81110a3d9d91a3` |

Commit `8bc32a401e5b330597ee4f0328b6683f69ad6a7a`, каталог
`Reports/StructTrain/TimeLearner/s07-high-threshold-joint-visual-m40-a1`.
Копии для image QA byte-identical исходному Git и base85b. Это просмотр старых
изображений, а не локальный scientific render, новый численный анализ или
повторная приёмка всех views.

В overview в одной LT Y-оси видны порог100 и прижатая к нижней границе линия.
В **уже опубликованном single/detail** видно ненулевую изогнутую LT Potential
curve и individual native sample markers; подпись честно указывает threshold
outside local Y. Эта конкретная пара не поддерживает утверждение raw-zero LT.
Она показывает, что overview не позволяет различать малую форму сигнала при
таком масштабе. На burst raw values, другие рисунки и физиологический механизм
этот вывод автоматически не переносится; CSV здесь не разбирались.

Причина масштаба непосредственно видна в исходнике:
`channel_diagnostic_reports.py:54–57` добавляет threshold в values, по которым
`padded_limits` строит shared range последней панели. Детальный local=True путь
и раньше рассчитывал limits по локальным samples, не добавляя threshold.
Это достаточное source/image evidence визуального сжатия **single overview**;
недостающие runtime Ready/Init/calc traces для такого вывода не требуются.
Они по-прежнему не известны для отдельного вопроса причинности исполнения.

## Минимальная правка renderer

Изменяется только `Scripts/StructTrain/TimeLearner/channel_diagnostic_reports.py`:

1. Full-time overview/shared zoom строят LT Y из всех фактических записанных
   LT ordinates с обычным padding. Threshold больше не меняет этот диапазон.
   Полный временной domain и все LT samples, включая отрицательные excursions,
   сохраняются; нет normalization, resampling, замены units или предсказанной кривой.
2. Если actual threshold внутри отображённой оси, сохраняется его настоящая
   dashed reference line и подпись. Если он выше/ниже оси, line не рисуется:
   над LT panel явно написаны точное round-tripping binary64 значение и
   `above displayed Y` либо `below displayed Y`. Порог не переносится на край
   графика и не скрывается без объяснения.
3. Малый helper `lt_threshold_display(threshold, limits)` проверяет finite
   threshold/корректные bounds и возвращает reference metadata, не изменяя axis.
   Его числа — значения сохранённого порога; они не задают новый порог модели.
4. Отдельные local measured-peak и positive-lobe soma views сохраняют свои прежние
   ограничения. Общая цель blue Soma.SumPotential, samples, stimulus overlay,
   spike markers, packet scope и source Git verification не меняются.

`RENDERER_VERSION=3`; новый manifest schema3 содержит `renderer_version` и
`lt_axis_range_policy`. Каждый view сохраняет `lt_threshold_display` с source,
value/value_text, position, line_drawn и axis_range_policy, а также общий
`threshold_outside_displayed_Y`. Старый `threshold_outside_local_Y` сохранён
именно как local-only поле; его семантика не подменяется новой.
HTML объясняет диапазон по данным и отдельное отображение далёкого порога.

Новый диапазон — раскрытие уже записанного сигнала. Это не cropping LT данных
ради желаемого пика и не scientific/каузальный verdict. Дополнительный
threshold-context plot не создаётся автоматически: точное значение и сторона
оси доступны в каждой LT panel и metadata, старые context PNG сохраняются.

## Подготовленные проверки, пока без выполнения

В source добавлены четыре meaningful regression cases:

- Above/below threshold: сохраняются exact value/direction и не заявляется
  off-axis line; bounds переданного axis не меняются.
- Внутренний threshold и обе границы axis: настоящая reference line остаётся.
- NaN/Inf либо invalid axis: structured отказ вместо валидной подписи.
- Реальный high-threshold Classic corpus: full-time chart limits содержат все
  записанные LT values и исключают далёкий100; production render metadata и SVG
  содержат явное `Actual LT threshold 100 (above displayed Y)`. Тест не требует
  ненулевого burst значения и не создаёт новых физических observations.

AST inventory будущего scoped gate:

| Модуль | Test IDs |
|---|---:|
| test_channel_diagnostic_reports |4|
| test_channel_observation_scope |4|
| test_channel_positive_lobe |3|
| test_channel_lt_threshold_display |3|
| Всего |14|

По сравнению с base85b это **10 прежних IDs +4 новых =14**, без удалённых IDs.
В итоговых4 observation_scope cases один новый; остальные3 существовали ранее.
Полный Git AST set difference сохранён в JSON. Это только source inventory;
**14/14 PASS не заявляется**. Реальные unit/numerical
и rendering checks выполняются только на Linux сервере после source review.
Нужны Git-bound existing low Classic/Branch corpus, actual high Classic native
cd8d prefix, прежний maximum-replay corpus и соответствующие read-only ODB.
Каждый fixture/fingerprint берётся из реальных сохранённых файлов; новые
физические данные или placeholders для подготовки suite не генерируются.
Оба render test helpers используют
`TemporaryDirectory(dir=os.environ.get('TIMELEARNER_REPORT_TEST_DIR'))`.
При отсутствии legacy-переменной None выбирает уже установленный существующим
owned_python_job writable TMPDIR (`worker/tmp`), наследуемый validation process.
`TIMELEARNER_REPORT_TEST_DIR` **не объявляется validation fixture**; явный legacy
output env остаётся совместимым со своим прежним caller. В старом
positive-lobe helper меняется только эта строка, без изменения численных
assertions или10 старых test IDs. Используется существующая owned_python_job
python-validation pipeline/approved plot-venv; новый runner API, orchestrator
или TEMP program не создаётся.

После успешного gate production CLI остаётся прежним:

```text
python3 -B -m Scripts.StructTrain.TimeLearner.channel_diagnostic_reports <Git-restored-native>
  --source-reference <actual-source-reference.json>
  --repository <evidence-ODB> --output <fresh-owned-cache>
```

Требуются exact IDs/zero skips/errors/failures, source и primary bytes before/after,
явные backend/limits, owned closure/released lease и отдельная визуальная проверка
нового full-time LT overview, off-axis annotation и соответствующей detail.
Пока этого нет, ни layout новой аннотации, ни полная совместимость corpus не
объявляются runtime-принятыми. Полные scientific figures строятся только сервером.

## Что сохранено

Старые primary JSON/CSV/models, PNG и caches не переписывались; никаких
C++/physics/learner/lifecycle изменений и обращений к M40/Elder/Windows не было.
Августовские4/8–6/8 и threshold100 observations остаются в своих исходных областях.
[Предыдущий metadata trace](ClassicFlatLTMetadataTrace-20261108.ru.md) остаётся
исторической проверкой provenance и отсутствующих runtime полей. Его null
physical cause не препятствует нынешнему, более узкому выводу о масштабе
single overview. Новых raw-zero или causal graph-defect утверждений здесь нет.
