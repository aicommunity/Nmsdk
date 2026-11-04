# Совместный перебор L/Ns/Rs/C: состояние проверки 03.11.2026

Статус: экспериментальная ветка; в develop не принята. Чистый decision-контур
проверен на сервере, native storage/scheduler, schema4, ASan и физическая матрица
пока не приняты. Полная постановка этапов0–12 сохраняется.

## Проверенные результаты

K1: root e4a2db58854c67d08d4dd45067d1724d55947fea,
Pulse9aad0f7f208c61c91f38d54bc92c939c642fab5b,
evidence9ab8a63a892e4ad780ebd19bf2dfeaef648a04f3:
Off A/B137/137 на каждой стороне, отдельный kernel147/147.
Независимо проверены52 members,65793 compressed bytes и357 Git source hashes.

K2: root09b994e7f33c0bbb711c71923f6266e447b708be,
Pulse9269118a41a86efc6bb3c667d46c5ee2aaec4633,
evidence98567c39be6bc6d3ee538404002701adcfbcec7e:
Off A/B137/137 на каждой стороне, отдельный kernel148/148, без failures/skips.
Независимо проверены53 members,66027 compressed bytes и357 Git source hashes
(319 root +38 Pulse). Дополнительный тест проверяет общий бюджет seed inventory.
[Первичные данные K2](../../../Reports/StructTrain/TimeLearner/s07-capacitance-contexts-kernel-normal-k2/bundle.json).

Одинарный kernel не выдаётся за A/B: comparison_performed=false.
Native Rdk integration и operation-trace equivalence в обоих доказательствах
не подтверждаются. Управляемые отклики тестов не являются научным экспериментом.

## Алгоритм и ограничения

Finite C/C0 contexts имеют собственные курсоры L/Ns/Rs и чередуются после полного
кандидата. Бюджет общий; N0 repeats не разрываются между C. Сохраняются полный
active/dormant C-state, CapturedPerInput и last anchor. Для изменённого C в N1
требуется свой domain; live edit инвалидирует domains всех контекстов. Локальный
успех не заменяет свежую финальную проверку каждого входа, включая Branch anchor.

maximumCursorElements ограничивает суммарный seed inventory, делимый между
контекстами. Проверки выполняются до копирования контекстов и расширения N1 Rs
mesh. Исчерпание означает BudgetExhausted, а не сходимость или PhysicalInfeasible.
Это предел seed inventory, а не предел всей памяти Rdk.

Политика выключена по умолчанию. Direct API требует привязанную C0 history.
Для переносимой policy подготовлена [schema4](CapacitanceSchema4.ru.md).
Schemas1–3 сохраняют прежнюю семантику без policy и не должны скрыто хранить On.
Measured C interpolation ещё не включена; конечная сетка не доказывает глобальную
монотонность, физическую недостижимость или достижимость8/8.
Подробности: Pulse Docs/Analysis/TimeLearnerCapacitanceContexts.ru.md.

## Воспроизводимые команды и дальнейшая приёмка

Root CLI controller-kernel SPEC --root-repository REPO --pulselib-repository REPO
--compiler COMPILER --gtest-source FETCHCONTENT_SOURCE --output DIR использует
тот же production builder, что controller-ab, но один pinned Git closure.
Сохраняются исходники/хэши, toolchain, original GTest, compile/run arguments,
owned processes и полный JUnit inventory. Спецификации:
capacitance-contexts-off-ab-v1.json и capacitance-contexts-kernel-v1.json.

Сборки и тесты выполняются только на workers. Локально выполняются статические
проверки и независимая сверка evidence с Git. Native scheduler/storage/C0,
export/import schema4, normal/ASan, читаемые soma+input графики и полная матрица
остаются условиями дальнейшей приёмки. K2 не закрывает эти пункты.
