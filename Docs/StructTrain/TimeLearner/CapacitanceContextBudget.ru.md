# Семантические дубли C-контекстов при малом бюджете

Исходный Pulse198dd5b77223938c53bf5e1e52880f402f5cf865 генерирует unchanged
контекст и seeds с первым абсолютным scale1. Если выбранный диапазон уже имеет
unit corrections, второй контекст не меняет C. При maximumContexts2 ни lower,
ни upper C scale не исследуются. Warm non-unit corrections отличаются: C01
может быть настоящим сбросом и должен оставаться кандидатом. Пустой Branch
interval также не должен создавать отдельные одинаковые domain contexts.

Новые три regression tests охватывают Classic/Branch N0/N1 при двух context
slots, warm1.1 correction и пустой coincident Branch interval. Ожидаемая
воспроизводимость на старом коде — failure minimal-budget и empty-interval,
успех warm-reset; это подтверждено серверной проверкой K3 ниже. Declared kernel151
(14 On controls), native target30, future full regression258. Исторические
J2 27/19 и K2 148 остаются результатами своих immutable source snapshots.

Исправление должно удалить только доказанно одинаковые C contexts. Возможный
диапазон выбранного входа учитывает topology, текущую downstream position и
bounds. Known dormant corrections внутри диапазона сохраняют значимый C01;
поправки вне диапазона не делают unit reset значимым. Неизвестные новые пути
имеют unit multiplier собственного будущего storage C0. Проверка равенства
не должна разворачивать огромный declared кабель до native preview.

Псевдокод:

    contexts = [unchanged full state]
    seeds = bounded absolute C0 scales, with one spare seed for a duplicate
    for scale in seeds:
        if selected-range request cannot change any possible path:
            continue
        keep context up to declared maximumContexts
    reserve total cursor inventory across retained contexts
    measure every actual candidate and run the ordinary fresh final gate

Не меняются математическая цель, tolerances, C0/storage physics, общий
scheduler/lifecycle или формат policy4. Default Off не затрагивается.
Приёмка: old-source regression reproduction, corrected kernel151, Off A/B137
на каждой стороне, затем реальные native/ASan/matrix проверки. Ни число tests,
ни успешный pure kernel не являются научной классификацией или полной приёмкой.


Baseline regression root e927b4a59537a3c32233a96603644bf68e6c9bac сохраняет
Pulse198 и те же151 tests. Исправление Pulse84e456d6fb551021e0222ebaf51fa313df2623b4
добавляет только private predicate/отбор seeds в BoundedTraining.cpp. Predicate
проверяет known path indices и implicit unit future paths, не создаёт union map.
Для Branch учитывает текущую downstream length и upstream upper bounds;
консервативно не удаляет context, если no-op не доказан. Штатные native preview,
C0/profile и fresh all-input gates остаются авторитетными.
Серверные reproduction/corrected/off-compatibility проверки завершены; native/ASan/matrix проверки исправления ещё требуются.


## Серверная проверка K3, 03.11.2026

Evidence commit `06408c3487f5c6f62e2090e3ea27515f16a56470`,
[пакет](../../../Reports/StructTrain/TimeLearner/s07-capacitance-contexts-kernel-normal-k3/bundle.json).
На Elder собраны целые production decision sources с оригинальным GTest:

- Off compatibility: 137/137 baseline и 137/137 candidate, одинаковые test sources.
- Старый Pulse198 / root e927b4a59537a3c32233a96603644bf68e6c9bac:
  149/151, ровно два ожидаемых failures minimal-budget и empty-interval.
- Исправленный Pulse84 / root d23a4164669bf3dcee8918f6322085e558a99e49:
  151/151, включая сохранение настоящего warm reset к C0.

Старый failed verdict сохранён как воспроизведение дефекта. Для сравнения старого
и исправленного кода использованы одинаковые test sources. Независимо сверены
outer checksums, все71 archive members /87570 compressed bytes, 106 production
source records и312 runner source records по точным Git commits. Это проверка
контроллера; native Rdk integration, ASan, физическая матрица и classification
не подтверждаются. Полные этапы плана этим не закрываются.


## Следующий native контроль: два слота

Добавлены четыре отдельных NativeCapacitanceSearchMinimalBudget случая:
Classic/Branch × N0/N1, maximumContexts2 и maximumCandidatesPerInput2,
фиксированные исходные L/Ns/Rs. Используется настоящий EditingRig, storage,
штатный scheduler и AssignedBurstWave; исходные четыре activation cases
не заменяются. Артефакты имеют отдельный csearch_minimal prefix. Проверяются
реальный measured non-unit C, отдельный N1 domain и отсутствие Exact при
нулевом sync tolerance. Python reader требует все четыре случая, полные
первичные данные и согласованный owned C-state. Это negative control обучения,
не доказательство классификации. Новые декларации: target34/full262; отдельный
minimal gate4. До серверного результата это только подготовленные проверки.


03.11: render-v2 обнаружил ошибку нового fixture inventory: full configured
package хранит normalization в configuration.model как N0/N1; summary search
configuration использует отдельный normalization synapse_count/tip_resistance.
Исправлены два новых reader inventory без изменения production схем/аудиторов.
Уже выполняющийся immutable J3 build/root1c8206ed98dad49982f1a1e9a1764c118e2cfe34
не меняется: его native34 результат и исходный reader verdict будут сохранены.
Для окончательной приёмки требуется reader rerun из исправленной версии на тех
же primary после завершения J3; numerical rerun из-за Python inventory не нужен.
