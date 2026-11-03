# Проверенный K1 и следующий aggregate-budget контроль

K1 evidence9ab8a63a892e4ad780ebd19bf2dfeaef648a04f3 проверен независимо:
52 members /65793 compressed bytes,357 точных Git source hashes.
Root e4a2db58854c67d08d4dd45067d1724d55947fea /Pulse9aad0f7f208c61c91f38d54bc92c939c642fab5b:
Off A/B137/137 на каждой стороне, отдельный kernel147/147 без skips/failures.
Одинарная проверка не выдана за A/B; native_rdk_integration_verified=false.
Контур конфигурации/переноса schema4, native/ASan C-search и графики реальных
моделей не подтверждаются этими управляемыми test responses.

Следующий commit добавляет maximumCursorElements — общий предел seed inventory,
разделяемый между C-контекстами. Проверки выполняются до копирования контекстов
и каждого расширения N1 Rs mesh. Исчерпание явно BudgetExhausted, не сходимость.
К нему подготовлен один дополнительный тест: kernel148/11 On controls; его
серверная проверка пока ожидается. Политика ещё не переносится старым codec.

# Совместный перебор L/Ns/Rs/C в общем контроллере

Статус: отдельная экспериментальная ветка; серверная проверка ещё не выполнена.
Подробный алгоритм и ограничения: Pulse Docs/Analysis/TimeLearnerCapacitanceContexts.ru.md.

Finite C/C0 contexts теперь имеют собственные курсоры L/Ns/Rs и чередуются
после полного кандидата. Бюджет общий; N0 repeats не разрываются между C.
Сохраняются полный active/dormant C-state, CapturedPerInput и last anchor.
Для изменённого C в N1 требуется свой domain; live edit инвалидирует
сохранённые domains всех контекстов. Локальный успех не заменяет свежую
финальную проверку каждого входа, включая Branch anchor.

Изменения выключены по умолчанию. Direct API policy требует bound C0 history.
Portable configuration/model schemas1–3 пока явно отказывают при policy On:
добавить schema4 roundtrip и production readers необходимо до приёмки.
Diagnostic summary On явно имеет schema4. Нельзя сохранять новую policy как Off.
Measured C interpolation ещё не включена; finite measured fallback не утверждает
монотонность, PhysicalInfeasible или достижимость8/8.

Новые10 CapacitanceContexts tests используют настоящий decision controller,
recorder и управляемые тестовые отклики. Они не являются native experiment.
Для Off A/B сохраняется byte-identical corpus137 исходных tests на обеих
сторонах (baseline root1a4fd929). Спецификация capacitance-contexts-off-ab-v1.json.
Отдельный kernel regression содержит147: прежние137 и10 новых On controls.
Спецификация capacitance-contexts-kernel-v1.json.

Root CLI controller-kernel SPEC --root-repository REPO --pulselib-repository REPO
--compiler COMPILER --gtest-source FETCHCONTENT_SOURCE --output DIR использует
тот же production builder, что controller-ab, но ровно один pinned Git closure.
Записываются исходники/хэши, toolchain, original GTest, compile/run arguments,
owned process groups и полный JUnit inventory. comparison_performed=false;
такой прогон не выдаётся за A/B. Сборки и tests выполняются только на workers,
локально проверены только AST, декларации и diff. Приёмка native scheduler,
storage/C0, export/import, normal/ASan и физической матрицы остаётся открытой.
