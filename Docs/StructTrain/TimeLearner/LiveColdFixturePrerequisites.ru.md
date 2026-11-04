# Pending: отдельные предпосылки cold LiveFinalization и saved-state replay

Расширенный SDK802 baseline133 с TIMELEARNER_POSTTUNE_FIXED_SOURCE из s08-native-phase-lifecycle-interrupt-normal-a1 выполнил133 tests:119 passed,14 failed,0 skipped. Core18 целиком passed. Все14 failures — LiveFinalization scenarios, ожидающие успешного cold Train и queued boundary. Первичный proof d135320775e719da4e8a7d715950a7e35eec4146 сохраняет полный отрицательный результат; общий lifecycle candidate8644 не компилировался и не выполнялся.

Фактически old source configuration дала budget_exhausted/maximum_sweeps_exhausted до queued state. Она содержит initial ISI[.01,.08], Classic input0 L2..3 и Rs86..172MOhm,4 candidates/input,1 sweep. Перенос из сохранённого обученного состояния и успешный новый cold Train — разные предпосылки. Этот запуск не доказывает ни lifecycle regression, ни PhysicalInfeasible, ни недостоверность исторического saved-state результата.

## Исправление постановки

LiveFinalization теперь требует отдельно:

- TIMELEARNER_POSTTUNE_FIXED_SOURCE — исторические PostTune controls/confirmation specification; прежние completed-state/interruption helpers не меняются;
- TIMELEARNER_LIVE_COLD_SOURCE — production declarations Classic-v1/Branch-v1 Train и frozen Test из корпуса проверенных cold N1 источников;
- TIMELEARNER_LIVE_CALIBRATION_SOURCE — measured-grid-job.json для каждого из этих источников.

Читаются только исходные параметры, дизайн trials, thresholds и storage profiles. Проверяются подписи всех трёх jobs и implementation ID. Новый cold configuration декодируется production DecodeConfiguredNativeTraining; storage образы регистрируются тем же PrepareModelArchive/profile_archives путём, что в Console Train. Готовый learned graph/параметры/controller не импортируются. Источник данных фиксируется отдельным source_declarations.json до первого импульса.

Выбранная отдельная engineering positive декларация ранее прошла на runtimef679:ISI[.01,.03], initial L1/1, Classic input0 L1..3,Rs43..86MOhm,80 candidates и256 probes. Это иная постановка, а не исправление или новый результат исходного[.01,.08] эксперимента. CapturedPerInput, anchorN−1, amplitude tolerance1e-5/relative0/minimum1e-6 и sync.02 не ослабляются. Ни алгоритм обучения, ни физика native компонентов этим commit не меняются. На SDK802 положительность ещё предстоит подтвердить.

## Приёмка и ограничения

Собрать отдельный baseline с Pulsecc971 и исправленной test-постановкой, сохранив старый SDK802/runtime и отрицательные primary. Сначала все24 NativeLiveFinalization controls и plan codec; затем те же133 real tests. Никаких skips вместо PASS. Если новое cold Train также не Exact, сохранять его реальные причины и проверять обучение, не подставлять готовую модель.

Для A/B общего dispatcher baseline и candidate8644 должны иметь строго одинаковые исправленные Tests/App/CMake и одинаковые input declaration hashes. После normal baseline провести candidate133/full304 и сравнение реальных CSV/состояний. ASan и другие обязательные матрицы остаются отдельными gates. До runtime-проверки это pending test correction, не принятое исправление алгоритма, не scientific8/8 и не завершение этапа6.

InvalidDesign строится из любого числа trials: все метки/patterns превращаются в target с различными trial_id. Замена только второй пробы была отрицательным контролем лишь для двухпробного дизайна; при четырёх пробах она оставляла foil и уже не гарантировала unbalanced design.
