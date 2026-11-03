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
успех warm-reset; это ещё требует серверной проверки. Declared kernel151
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
Серверные reproduction/corrected/off-compatibility проверки ещё требуются.
