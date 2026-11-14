# N0: локальная нормализация следующей временно допустимой геометрии

Статус: ограничение текущего production-порядка подтверждено кодом и [завершённым Branch N0](ValidationPlans/M40StockN0BranchTrainA1-20261114/RESULT.ru.md); кандидат исправления реализован в Pulse58c6e6d51c749a13a79498a681e14ea2fe353ed7, серверная проверка ещё не выполнена. Исходный native SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8; локальный Pulse04a10aa94da7adb887ccabd73a7b7ea2d8dd7600 добавлял документы и сохраняет этот алгоритм. Старый runtime не изменяется.

## Доказательство

BoundedTraining.cpp::Consume, после завершения повторов кандидата, вычисляет improved относительно общего best. Enqueue N0 neighbors требует improved && withinTiming && !withinAmplitude. Поэтому хороший амплитудный результат одной длины подавляет начало локальной нормализации другой длины, у которой исходный Ns1 пока имеет плохую амплитуду. Это смешивает ранжирование финального лучшего кандидата и решение, где продолжить исследование.

В реальном Branch N0 при полном L=[26,26,25,1] Ns4 дал amp residual+0.0003079757232195002, timing−0.015499999999974534с. Затем L26/27/28 с Ns1 дали timing−.006/+.003/+.012с, но amp residual около−.012; Ns>1 для них не измерен. В Rank оба кандидата withinTiming=true/withinAmplitude=false, поэтому нормированная сумма Ns4/L25 около31.57 меньше суммы Ns1/L26 около1192.19. Условие improved=false не даёт enqueue даже соседнего Ns2 новой длины. Это не обоснование изменения Rank, амплитудной цели или допусков.

Различать физические scope: исходный L25/Ns1 использовал полный L=[25,25,25,1], а Ns2..5 и повтор Ns1 — [26,26,25,1]. Перенос амплитудных измерений между этими bank layouts недопустим. Подсказка следующего кандидата может использовать историю только как proposal с обязательным новым измерением.

## Требуемая правка

Файлы: Core/TimeLearner/BoundedTraining.h/.cpp и адресные production-session tests в PulseLib; затем новый same-budget native N0 контроль и root DATA/report fixtures. Не менять Native scheduler, storage images, параметры на каждом тике или bool Build/Calculate/Reset.

Разделить global best для результата и локальную историю N0-исследования. Scope локального улучшения включает input, полную геометрию/неактивные Ns/Rs, активные L/Rs, эффективный C-context и неизменный model/protocol context с frequency/dt/reset. Свободной переменной остаётся только активный целый Ns. При bank propagation формировать легальный полный vector существующим PrepareCandidate; изменившуюся физическую scope не считать тем же измерением. Повторные пробы аггрегируются до обновления local best.

На каждой новой timing-ready scope должен быть доступен собственный конечный normalization turn, даже если Ns1 хуже глобального best. Бюджет turn выводить из оставшихся candidates/probes/edits с учётом2 fresh anchor/input probes на каждый из K repeats; ограничить число предложений и сохранить ресурс для других геометрий. Конкретные пределы зафиксировать в реализации и тестах до нового A/B. Простое удаление improved недопустимо: оно может провести все128 Ns на первой длине и снова лишить бюджета остальные геометрии.

Псевдокод:

    receive completed valid candidate (or completed repeat group)
    update global best using the unchanged Rank
    if N0 and timing-ready and amplitude-outside:
        find exact physical normalization scope
        update scope-local best and bounded turn accounting
        if local improvement and turn allowance remains:
            propose unissued legal neighboring/measurement-guided integer counts
            never promote a proposal to a measured point
    retain finite whole-domain fallback and complete candidate deduplication
    apply edits only through the existing native adapter at probe boundaries
    remeasure fresh anchor and assigned native burst after every effective edit
    Exact only after the unchanged independent all-input final gate

Соседний measured bracket Ns3/4 вне допуска не даёт дробное Ns, Exact или PhysicalInfeasible. Не предполагать глобальную монотонность; nonmonotone/invalid/missing observations не должны пополнять allowance или скрывать fallback. Для changed C/profile/retarget прежняя scope/история непригодна.

## Приёмка

1. Production BoundedTrainingSession: первая геометрия имеет хороший, но вне допуска amplitude best; следующая timing-ready Ns1 хуже, зато её реально измеренный Ns2/3 достигает исходной цели. До правки фиксируется starvation; после — fresh native actions и final certificate только по измерениям.
2. Нельзя смешать upstream bank, inactive Ns/Rs, C-context, input или другой frequency/reset/profile. Проверить Nx1 и Nx>4 где поддержано; Classic и Branch order остаются исходными.
3. K repeats: только полный repeat group обновляет local evidence, raw повтор не является независимым candidate; allowance учитывает реальное число probes и все global caps.
4. Малые бюджеты, неулучшение, немонотонность, integer quantization, Ns128 с остатком внутри/вне допуска, повторённые/invalid proposals. Fallback не теряется; отсутствие сходимости не переименовывается в успех.
5. После scoped kernel gate — fresh native SDK и адресные real-component cases; затем один заранее объявленный same-budget Branch N0 A/B против сохранённого текущего baseline. Изменяется только algorithm source; physics, target, tolerances и global budgets прежние. Проверять реальную посещённую область и остатки, а не требовать8/8 ради PASS.
6. Сохранить полный primary, собственные читаемые waveforms/actual inputs и сведения об итоговом actual model. Если новый бюджет снова исчерпан, зафиксировать этот исход; не повторять Train с повышенным лимитом ради положительного отчёта.

Фактическая восьмипаттернная frozen-диагностика исходных N0 моделей выполняется отдельно на старом runtime и не заменяется новой реализацией. Эта корректировка не отменяет прежних наблюдений или текущего budget_exhausted и не закрывает весь этап7.

## Кандидат реализации перед gate

Pulse58c6e6d51c749a13a79498a681e14ea2fe353ed7 добавляет PrioritizeN0Neighbors и отдельные N0GeometryTurn в cursor. Scope совпадает по full parameters, кроме active Ns, и EquivalentTrainingCapacitance; global best/Rank не меняется. После полной группы K repeats новая timing-ready scope получает allowance=min(12,remaining candidates,remaining probes/2/K,remaining edits,max(4,remaining candidates/4)). Только локальное улучшение может продолжить очередь, уникальное enqueue расходует allowance, повторный визит его не пополняет. Whole-domain fallback и полная deduplication сохранены.

Один и тот же новый6-case production-session корпус зафиксирован до правки в root9d9dd4f206a7dacb850b5a7a8bfc7175a29e93ce с Pulse04a10aa94da7adb887ccabd73a7b7ea2d8dd7600. Новый test файл Test_PulseLib_N0Geometry.cpp использует общий fixture header; тела прежних fixture functions и75 явных старых TEST declarations побайтово/по inventory сохранены. Kernel-runner теперь принимает regular Git headers в test_paths и компилирует только cpp. Это зависимость реальных общих fixtures, не извлечение production-функции в тестовую копию.

Требуется фактический old/new kernel run на обоих workers с одинаковыми тестами, сохранёнными failure IDs старого варианта и полным успешным candidate. Затем native SDK/real-component regressions и объявленный same-budget physical A/B. Ни новый C++ runtime, ни новые научные результаты этой правки пока не получены; текущий frozen8 использует старый SDK.

Первый фактический kernel A3 на Elder с корпусом root9d9/80e64: оба варианта скомпилированы, baseline0/6 и candidate2/6. Это не приёмка исправления. Выявлены ошибки нового тестового корпуса: Branch L1 совпадает с фиксированным anchor и не допускает иной Ns в той же bank; Evidence включает отдельное свежее восстановление best после лимита предложений. Корпус уточнён без ослабления итоговых Exact/final-gate требований: Branch стартует с отдельной L2 bank; проверка proposals отделена от restore measurement; немонотонный контроль также использует физически допустимую bank. Перед новым сравнением одинаковый исправленный корпус снова фиксируется с прежним production Pulse04a, затем с Pulse58c. Отказы первого корпуса и неизменённые исходные JUnit сохраняются отдельно; ожидаемое поведение не подменяется фактическим.
