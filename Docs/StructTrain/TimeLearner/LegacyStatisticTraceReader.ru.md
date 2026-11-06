# Строгий адаптер числовых StatisticLog: постановка проверки

Новый production путь: `python -m Scripts.StructTrain.TimeLearner analyze INPUTS.json --format legacy-statistic-traces --output NEW.json`.
Это read-only описательный анализ, не обучение, калибровка или сертификат синхронности.

INPUTS: точная схема `kind=timelearner_legacy_statistic_inputs`, `schema_version=1`,
непустой массив `traces`. Каждая запись содержит только `id`, относительный `path`,
`layout`, положительный целый `width` и SHA256 исходного файла `sha256`.
Layout задаётся явно: `time-values` либо `index-time-values` с нумерацией от0.
Читатель не угадывает dialect и не ищет latest StatisticLog. Разные clocks
разных файлов не объявляются синхронизированными.

Проверяются точная размерность каждой строки, конечные числа, строго возрастающее
неотрицательное время, непрерывные индексы, hash и неизменность файла во время чтения.
Пустые/повреждённые строки не отбрасываются. Размерность произвольная, в том числе>4.
Summary хранит extrema/последний отсчёт каждого канала; отрицательные максимумы
не заменяются нулём. Ни peak assignment, ни отсутствие отклика не достраиваются.
Даже прочитанный полностью файл не доказывает полноту trial window: validity=unknown,
complete_observation_windows_verified=false, training_certificate=null,
classification_verified=false и evaluation_verdict=null.

## Основания semantic review AsymRm

Архивная точка Bin `f12f09ae1f7fc0a9af1d99be86d3a4002a3cf4aa`,
`Configs/SpikeSamples/StructTrain/SelectivityAsymRm/scripts/`:

- `analyze_peak_sync.py:analyze_train_dir` подставляет нули при отсутствии LastAbsDtTrace,
  затем классифицирует sync_ok по этим значениям. `overall_peak_verdict` может вернуть
  FORMULA_OK по совпадению L с формулой, даже при плохих измеренных пиках.
- `asymrm_train_common.py:all_non_ref_sync_ok` проверяет только имеющийся prefix
  через min(n_dend-1,len(vector)); неполный непустой вектор способен пройти.
- `parse_trace_tail_rows` пропускает повреждённые строки, выбирает ограниченный tail,
  а `load_trace_vectors` независимо выбирает последние строки разных файлов.
  Эти snapshots не доказывают одну revision, общую пробу или закрытое окно.
- `verify_element_params.py --no-inh` исключает только InhibitionCoeff2.5;
  это не доказательство полного отсутствия торможения или правильного effective graph.

Это выводы чтения исходников; старые скрипты не запускались. Исторические
измерения и результаты не пересматриваются. Старые29 Python-файлов пока не удалены:
перенос остальных функций и migration manifest остаются отдельной работой.
Новый адаптер закрывает только безопасное чтение числовых рядов, не заменяет все
специализированные физические анализаторы, native model readback или scorer.

В тестах сохранён реальный Git-preserved scalar Rdk trace из AxoneLengthDelayStudy
с полной привязкой к Bin commit/path/hash. Это только fixture формата:
не новая аксонная физика, не TimeLearner обучение и не scientific evidence.
Два dialects/размерности1,2,4,5 и все corruption/CLI negatives проверяются отдельно.
Численные проверки выполняются только на Elder/M40. Приёмка пока ожидается;
старый исторический PhaseA reader и его результаты не менялись.
