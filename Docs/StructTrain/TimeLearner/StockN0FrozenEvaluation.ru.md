# Восемь паттернов: frozen-диагностика фактических N0-состояний

Постановка14.11.2026 до нового Test. [Classic N0 завершился без сходимости](ValidationPlans/M40StockN0ClassicTrainA1-20261114/RESULT.ru.md); Branch N0 ещё выполняет объявленный холодный Train. Следующий диагностический контроль использует **фактически экспортированное остановленное состояние**, а не шаблон и не лучший промежуточный кандидат. Если Branch завершится с полноценным learned boundary, для него нужен completed export/evaluate protocol; diagnostic-тест не должен принудительно превращать успех в stopped state.

## Условия первой оценки

- Восемь исходных Phase A pattern vectors с сохранёнными labels/IDs из того же pinned Bin snapshot, что в принятых N1 matrix controls;4 ISI на паттерн,1 target/7 foils. Parameters_00.xml/results.csv и полный matrix revision сохраняются как fixtures.
- Native SDK/runtime тот же, что у N0 Train; runtime.json сравнивается с фактическим training runtime целиком.2000Гц, исходный threshold100, полный native import всей модели. Identity conversion сохраняет индивидуальные L/Ns/Rs/C и эффективный граф.
- reset_per_trial, полные2с на каждый паттерн, штатные реальные input timestamps и spike events. Это новый frozen-протокол, а не воспроизведение августовского continuous scheduler/ITI. Order/ITI robustness этой серией не доказывается.
- При оценке используется весь отклик. Ранние спайки считаются явно по времени относительно последнего фактического входа; их нельзя выдавать за детекцию завершённого паттерна. Данные сохраняют также историческую whole-window оценку.
- Порог фиксирован100; модель и порог не выбираются на этой матрице. Молчание target — FN,7/8 молчаний не является успешной классификацией. Калибровка и подбор порога в первой оценке отсутствуют.

## Проверяемый production-путь

Worker fixture test_stock_n0_stopped_matrix_native читает и полностью аудирует training run-manifest, проверяет source package SHA/model revision, N0/topology и отсутствие сертификата у stopped source. Применяет существующий stock_stopped_evaluation.job_for и публичную команду diagnostic-evaluate с явной owned-cgroup policy. Ни новой ветки нейронного алгоритма, ни отдельного измерителя/renderer не вводится.

Приёмка:8 complete/valid responses по объявленному множеству ID, frozen model.json == model-after.json, вложенный source_solo равен исходному полному package, эффективная neuron graph identity равна исходной. Source package hash не меняется; весь run проходит штатный DATA audit; native/outer groups закрыты. Нет требования TP/FP или разделимости ради PASS. Threshold100 и counters являются измеренными свойствами опыта; положительный итог сходимости не создаётся.

## Дальнейшее представление

Сохранить сжатый полный primary, модель, фактические inputs/spikes, метрики и provenance. Полный отчёт с потенциалом каждой сомы для каждого паттерна, входными импульсами, обзором и читаемыми увеличениями остаётся воспроизводимым M40 cache; выбранные исходные PNG после ручной проверки входят в компактный Git. Графики N1 не подставляются за новые N0 observations даже при совпадении model revision.

Если затем выполняется отдельный Same-Matrix threshold experiment, объявить его до spiking run, использовать штатный diagnostic_threshold_study и единственное заранее определённое midpoint rule. Nonspiking maxima только предлагают кандидат; фактический исход определяется реальным запуском с выбранным порогом. Отсутствие допустимого кандидата, nonseparable proxy и scientific nonseparability не смешивать с invalid observations и не скрывать. Independent Test и calibration certificate эта процедура не создаёт.

Тяжёлые audit/render и новые native evaluation запускаются после закрытия текущего timed Branch Train, чтобы не менять его ресурсные условия. Начальная runtime/physics/mode matrix всего плана остаётся частичной.
