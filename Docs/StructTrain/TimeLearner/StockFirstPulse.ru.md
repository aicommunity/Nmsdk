# Первый импульс и несколько максимумов: измеренный контрпример

07.11.2026. **В проверенном Classic candidate три положительных локальных
максимума возникают до второго реального входного импульса.** Поэтому
равенство «число локальных максимумов = число входных импульсов» не является
общим свойством используемой stock-модели. Это не разрешает автоматически
выбирать один из пиков или принимать прежнюю invalid-пробу как valid.

## Данные и границы вывода

Исследованы первые invalid-пробы двух low/Retry Train, четыре входа,2000Гц,
N1, CapturedPerInput, fixed threshold0.0117, без дополнительной LTMembrane.
[Полный точный replay](StockWaveReplay.ru.md) после import/native Reset
воспроизвёл все входные и соматические отсчёты. Теперь production-аудитор
повторно проверил весь CSV, реальные onsets и записанные волны; анализирован
только открытый справа участок до второго фактического импульса.

| Модель и выбранный канал | Максимумов до второго импульса | Задержки от первого импульса | Амплитуды над native baseline |
|---|---:|---|---|
|Classic, input0 / soma0|3|1.5,17,38.5мс|0.09811046;0.23209749;0.03053042|
|Branch, input2 / soma0|1|20мс|0.01185933|

Второй импульс приходит через80мс после первого. Все перечисленные максимумы
внутренние и выше исходного minimum1e-6. Граничный максимум за пределами
участка не достраивается. В Branch input2 означает выбранную точку подключения;
здесь рассматривается первый импульс pulse0, не назначение целевого pulse2.
Число максимумов полной пачки остаётся12 для Classic и7 для Branch.
Потенциал указан в model units, принадлежность к SI не установлена.

Classic показывает, что несколько максимумов могут появиться ещё до следующего
предъявления. Для Branch эта проверка не объясняет поздние слабые максимумы:
одного максимума в раннем участке недостаточно для вывода обо всём хвосте.
Ни источник обратной связи, ни численная природа колебаний этим не установлены.
Отсутствие LT markers не означает отсутствие спайков: producer их не записывает.

## Графики с достаточным увеличением

[Полная проверка cache](StockWaveReplayVisualVerification.json): пять
trial/soma pairs,251 view; для каждой пары полный1.8с обзор и36 непрерывных
50мс shared-Y увеличений, без прореживания. Дополнительные peak details
показывают примерно10мс с отдельными native отсчётами. Полный cache761файл /
43520390B находится на M40, шесть выбранных PNG — в Git.
[Ручная QA](StockWaveReplaySelectedVisualQA.json) охватывает эти шесть рисунков,
не все251 view.

- [Classic,0–50мс: вход и многопиковый отклик](../../../Reports/StructTrain/TimeLearner/s03-stock-wave-replay-visual-m40-a1/Classic-threshold-low-retry32-soma1-zoom-001.png).
- [Classic: третий максимум, native samples](../../../Reports/StructTrain/TimeLearner/s03-stock-wave-replay-visual-m40-a1/Classic-threshold-low-retry32-soma1-measured-peak-00097-detail.png).
- [Branch: слабый поздний максимум, native samples](../../../Reports/StructTrain/TimeLearner/s03-stock-wave-replay-visual-m40-a1/Branch-threshold-low-retry32-soma1-measured-peak-00389-detail.png).

Последний рисунок относится к более поздней части полной пачки, после второго
импульса. Он иллюстрирует измеримость слабого максимума, а не изолированный
отклик первого импульса. Общие и локальные шкалы Y подписаны отдельно.

## Реализация и приёмка

Модуль `Scripts/StructTrain/TimeLearner/stock_first_pulse.py` использует
production `audit_unassigned_burst`, `read_partial_probe` и
`measured_wave_plateaus`. Import ничего не запускает. CLI для полного source:

```text
python -m Scripts.StructTrain.TimeLearner.stock_first_pulse SOURCE_stopped_state.json
```

Все numerical checks выполняются на worker. [Verification](StockFirstPulseVerification.json)
подтверждает четыре tests без skips на M40: реальные Classic/Branch prefixes,
отклонение изменённого stimulus timestamp и удалённой recorded wave. Десять
members и357 tool source hashes сверены с Git; шесть source bindings совпали
с исходным опубликованным архивом Train. Группа закрыта, lease released.
Второй сервер в эту приёмку не входит. Новое обучение и отдельная single-pulse
проба не запускались; существующие данные не переоценены по новым критериям.

Evidence4c0bc50757adee420270adc43fe96545e36ee6ea, root инструмента
eab9a7789906471410cb8ad93ed53c5bff1bb3d3. Visual evidence2fc1131d30e27a414c8485f287c2af90170126bd
и дополнительные details ee8df041b8bc466399e5ff0364d7a2ab311a2c60.

## Следствие для исправления алгоритма

Нельзя считать каждый локальный максимум отдельной response wave и затем
требовать ровно четыре таких максимума. Но переход к «четырём самым большим»
также необоснован. Следующая проверка должна записать Exc/Inh составляющие,
LT events и реальные связи в том же candidate, сохранив waveform baseline.
Это позволит различить прямой отклик, feedback и поздние составляющие до
выбора версионированного правила response assignment. Предсказанная задержка
не заменяет измерение; CapturedPerInput и исходные допуски сохраняются.
Старые invalid, исторические4/8–6/8 и научные метрики не переписываются.
