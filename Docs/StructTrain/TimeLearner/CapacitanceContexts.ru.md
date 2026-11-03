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
