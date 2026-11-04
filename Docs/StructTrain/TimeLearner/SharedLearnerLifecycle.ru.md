# Кандидат общего lifecycle dispatcher

Pulse candidate `8644c50984c45a2211de13a75fe05cffc5bb3154`, исходник `cc97149c90ce98ff24ca688452f4a40d54e0e63d`. Три одинаковых тела ABeforeCalculate/ABeforeDefault/ABeforeReset обоих learner перенесены в общий NativeLearnerLifecycle. Конкретные методы остаются виртуальными Rdk hooks; helper получает owner, topology-specific integration-failure predicate и квалифицированный вызов базового hook.

Порядок, lifetime scopes, состояния, обработка исключений, ForceSkipComponentCalculation и true-return сохранены механическим преобразованием. Обратная замена owner/callbacks восстанавливает точный исходный текст всех шести тел. Новых вычислений модели и изменений поиска здесь нет. [Проверка преобразования](SharedLearnerLifecycleMechanical.json).

Выделение сохраняет различие failure codes:Classic2/3/4,Branch4/5/6. Общая проверка по одной таблице была бы неверной, даже при одинаковом тексте прежних методов. Legacy file-based ApplyLoadedAnchorProperties не переносился в этот commit; его поведение требует отдельного semantic review.

## Требуемая приёмка

1. На неизменяемом baseline SDK802/Pulsecc выполнить native-shared-lifecycle-regression-v1:133 существующих реальных tests, включая18 core canaries из native-shared-lifecycle-v1. Два проверяют код ошибки и сохранность реального Output сомы после preflight rejection;16 проверяют Reset/Default/Destroy, threshold/weight phases и nested callbacks. Их исходники берутся целиком из production integration target.
2. Собрать candidate на Elder в отдельном source/build/runtime. Сохранить actual compiler/build flags, source closure и loaded libraries. Измеренный baseline build207MiB и runtime144MiB; source3GiB. При17GiB свободно допустим отдельный bounded build с предварительной проверкой диска, без изменения baseline802 или текущих runtime.
3. Повторить те же133 controls и полный native-csearch-threshold-regression-v1 (304). Сохранить все отрицательные predecessor результаты отдельно. Tests/App/CMake должны совпасть с frozen SDK802; новый spec добавляет запуск, а не тестовую копию функций.
4. Сравнить реальные наблюдения candidate с опубликованным baseline304, proof25bbda55:одинаковые множества trial/trace files, полные CSV, typed statuses, параметры моделей и сертификаты. Неприменимые различия provenance/path/PID должны быть перечислены явно; не считать общий tree hash эквивалентностью динамики.
5. После приёмки normal провести ASan и оставшиеся lifecycle/compatibility/multirate проверки на свободном worker. Живые M40 K1 и следующий joint44 не изменять.

До фактической компиляции/runtime ни корректность кандидата, ни этап6 не считаются принятыми. Все stage1–12 остаются частичными. Численные/интеграционные проверки выполняются только на workers, исходники и результаты — через Git, merge children-first --no-ff после приёмки.

Фикстуры16 interruption controls восстанавливаются из Git primary `Reports/StructTrain/TimeLearner/s08-native-phase-lifecycle-interrupt-normal-a1/primary.tar.xz` (SHA256490c8c74240efb8d661dc14cd4bb5de653255b0e8513a5a7a3c7a71e71fafe42), каталог fixtures. Env TIMELEARNER_POSTTUNE_FIXED_SOURCE обязателен: пропуски не считаются PASS. Этот снимок содержит исходные portable Classic-auto_metric и Branch-synthetic jobs и их настоящие primary siblings. Expanded133 дополнительно включает целиком plain TEST/TEST_F из FinalizationBoundary,NativeExecution,LifecycleContracts; XML gate обязан подтвердить точное множество. Параметризованные TEST_P этим списком не покрываются автоматически.
