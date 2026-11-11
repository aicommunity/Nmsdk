# Исправление ложного missing из-за прогнозного окна — 12.11.2026

## Подтверждённый дефект постановки измерений

На настоящем Branch N4/N1 cold8 Train все пять rejected groups20/22/24/26/28 имеют valid assigned basin в полной сохранённой записи; исходное узкое окно даёт missing. Production replay и native-scale renderer приняты2/2 на source20e404281. Старый Classic package6 replay независимо принят1/1 на Elder с прежними исходами, то есть исторические состояния не переоцениваются. [Исходный Train](ValidationPlans/M40StockCold8TrainA1-20261112/RESULT.ru.md), [analysis gate](ValidationPlans/M40RecoveryN4WindowAnalysisA1-20261112/README.ru.md).

Первая ошибка Branch особенно показательна:assigned input2, measured maximum sample604 относительно full-before; прогнозное окно605..685. Пик исключён на один native tick (0.5ms), а не отсутствует физически. Relative peak0.3020s, начало окна0.3025s. Его amplitude0.00829352955716034 меньше amplitude другого, input1,0.008612371704209809. Full-window assigner выбирает именно input2, а не глобальный максимум. Четыре cursor_advanced после такого missing сохраняют неверную гипотезу окна, затем invalid-budget stop.

29frames первоначальной полной latency сегмента L1 не являются измеренной производной задержки по длине. Узкий линейный прогноз с постоянными40-frame guards не подтверждён в изменённой структуре. Научный исход старого Train остаётся invalid_observation; post-hoc valid не создаёт certificate.

## Изменение production пути

Новая явная команда stock-candidate-window-study prepare-full-window формирует plan3/configuration8; старые prepare/prepare-recovery сохраняют plan1/2. ALGORITHMS3 и ConditionSpec отличают новую постановку. Контроллер C++/native runtime не подменяется.

Для каждого входа из проверенной characterization берётся только полный диапазон записываемой native-сетки и начальный reference peak/plateau. Существующая native recipe задаётся коэффициентами:delay/length/Ns/Rs/C guards0; base_left=reference_first; base_right=sample_count−1−reference_last; hard_first0/hard_last sample_count−1; maximum_window_frames sample_count. Поэтому legal candidate всегда получает [0,sample_count−1]. Арифметика проверяется на initial и всех прежних length/R corners; отдельная property-проверка меняет L,Ns,Rs,C и подтверждает неизменность домена. Никакая предсказанная задержка не становится наблюдением.

Native protocol остаётся full-before → все omission controls → full-repeat. Применяется прежний basin/necessity assigner для закреплённого импульса. Genuine ambiguity, missing, nonrepeatability, nonfinite и incomplete сохраняют прежние причины отказа. Полное окно не означает выбор наибольшего пика всей пачки. Изменяется область поиска измерителя, не его принадлежность импульсу.

Сохраняются ModelSpec/storage physics, target и stimulus timestamps, reset policy, CapturedPerInput amplitudes и initial reference capture windows, индивидуальные границы, search/time budgets, min amplitude1e-6 и tolerances abs1e-5/relative0/Sync0.02. Новое cold обучение заново измеряет references. Нет retarget, threshold fitting, C-trim, нового LTMembrane или runtime prototype mutation. Окончание полного окна остаётся конечным наблюдением, а не доказательством отсутствия ответа за ним.

## Приёмка и ограничения

Подготовлены четыре declaration regressions и наследуемый реальный preflight для обеих stock топологий (plan3 вместо2) через production CLI/native path. [Серверная declaration/native-preflight приёмка выполнена5/5](ValidationPlans/M40ObservationDomainPreflightA1-20261112/RESULT.ru.md). Новый cold Train ещё не выполнен. Далее проверить реальные candidate proposals на полном диапазоне и свежую финальную верификацию всех inputs; не обещать Exact или8/8. Полные режимы/physics/PostTune и оригинальные этапы1–12 не закрыты этим исправлением.

Plan3 — версия Python-плана задания, не ControllerVersion и не StructureBuildMode. Native конфигурация остаётся8, runtime/физика неизменны.
