# TimeLearner: проверенный статус на 19 ноября 2026

Проверка серверов: 18.11,21:03UTC / 19.11,00:03МСК. Полная цель этапов0–12
активна. Полностью принят этап0; этапы1–12 частичны. Процент общей готовности
не назначается: оставшиеся алгоритмические и режимные проверки имеют разный
объём. Accepted root develop остаётся87e7da0205b6bb0d582f7b4f2551c935fd7f2350.
Рабочая ветка до этой сводки:2fd4de3d93dfa6b687428ed3d283591d50c9ff2d.

## Научные результаты

| Проверенная модель и протокол | TP | FP | FN | TN | Ограничения |
|---|---:|---:|---:|---:|---|
| Новый cold Classic,8 исходных паттернов |1|2|0|5|Порог выбран на той же матрице; Train BudgetExhausted, сертификата нет.|
| Новый cold Branch,8 исходных паттернов |1|2|0|5|То же ограничение Same-Matrix.|
| Сохранённая Elder Branch,8 исходных паттернов |1|1|0|6|Порог0.09874840158355691 подтверждён actual native Test; остановленная модель.|
| Та же Elder Branch, target control и3 новых foil |1|0|0|3|Порог и модель зафиксированы до новых ответов;3 новых foil, один знакомый target, одна обученная модель.|

Последний heldout4 прошёл полный common source/model/scorer audit:
все4 окна complete/valid, модель frozen, порог повторно не выбирался.
Target дал спайк0.4925с, через2.5мс после последнего входа; новые foil молчат.
Native1420.02с и audit1437.16с завершились exit0, все связанные процессы закрыты.
[Полная квитанция](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-common-audit-closed.json).
Успех этих3 новых foil не отменяет FP на исходном phasea-row-4, не доказывает
сходимость Train и не является независимым повторным обучением.

Полный primary исходного baseline/threshold Test Elder опубликован на M40.
Новый heldout primary собран на .14:126928729 bytes,
SHA256309c9d895b913e149836b7185daf13d035764c021a180d89f5a1369dbe330f7a.
Пакет опубликован в центральном архиве M40: все70 members,3200472564
expanded bytes проверены по hash/size; исходная Train primary и прежняя
калибровочная primary разрешены по каталогам. [Квитанция и CAS-ссылка](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-primary.archive.json).

## Последние задания и проверки

| Задание | Фактический исход |
|---|---|
|M40: временной отчёт Elder baseline/threshold,16 проб|2/2 declared tests PASS; галерея baseline/threshold создана. Kernel group закрыта. Визуальная приёмка и публикация этой новой галереи ещё впереди.|
|Elder: fresh SDK,14 targeted cases|13 PASS/1 FAIL; выполнены все14. Отказ BoundedTrainingMeasuredBoundary/UnmeasuredEditAndBudgetStopCannotReplaceTheMeasuredSelection. Gate не принят, причина требует разбора. Supervisor и дочерние группы закрыты.|
|Предыдущий M40 gate29|25 PASS/4 FAIL. Четыре N0 ThresholdCandidate не получили исходного certificate, maximum_sweeps_exhausted; downstream проверки ещё не подтверждены. Persistence2 прошли.|
|Windows .14: heldout4|Native и полный audit завершены; TP1/FP0/FN0/TN3.|

[M40 report receipt](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/native-temporal-report-closed.json),
[Elder14 receipt](../../../Reports/StructTrain/TimeLearner/MeasuredBoundarySelection-20261118/elder14-closed-rejected.json).
Перечисленные ранее живые задания завершены; повторный запуск не выполнялся.
Эти адресные проверки не заменяют полную объявленную матрицу262Linux/261Windows.

## Готовность этапов

| Этап | Реализовано и проверено в части области | Что удерживает полную приёмку |
|---|---|---|
|0|Согласованное начальное объединение develop/gitlinks.|Этап принят.|
|1|Исторические источники, реестры дефектов и публичных параметров.|Оставшиеся audit unknowns, inherited properties и effective-factor coverage.|
|2|Изолированные сборки/runtime, manifests, внешний архив и восстановление primary.|Полная build/resource/fault matrix и closure всех принятых публикаций.|
|3|Строгие ID/completeness/finite проверки, versioned scorer, реальные frozen observations.|Полнота исторических адаптеров и единый verdict во всей поддерживаемой области.|
|4|Настоящие lifecycle/storage/physical DATA fixtures.|Полная fresh/reuse/Copy/Load/Build/growth/heterogeneous и режимная матрица.|
|5|Export/import, stopped/completed state, native Train→Test roundtrip.|Остальные физические/связевые варианты и согласование будущего terminal restoration с archive/replay.|
|6|Общий native service/controller и Classic/Branch adapters.|Legacy/V2 A/B, оставшееся дублирование, отдельная multirate verification.|
|7|Measured bounded L/Ns/Rs search, N0 repeats, причины остановки и final verification.|Возврат к выбранному измеренному полному графу при глобальной остановке, его проверки; полная bounds/physics/reset/C-search матрица.|
|8|Solo/recognition state, transactions, реальное подтверждение порога, первые unseen foil.|Все PostTune/inhibition/reset modes и расширенная независимая frozen evaluation.|
|9|Корневой пакет/CLI, manifest357 и адресные migration gates.|Оставшиеся Bin analysis/matrix/shared tools и callers; complete=false.|
|10|Owned groups, leases/budgets, provenance и fail-closed publisher.|Полная effective-factor, cancel/recovery/publication fault matrix.|
|11|Реальные положительные и отрицательные результаты, order/window/reset проверки отдельных моделей, временные отчёты.|Систематическая legacy/V2 и физическая/режимная матрица, новые независимые условия и повторы.|
|12|Поддерживаемые отчёты; DOCXv3 Classic15/Branch14 страниц,9 примеров,29 страниц проверены.|Сквозная сверка root/PulseLib/Bin/config/ClDesc, завершение миграции и очередная актуализация примеров.|

## Ближайшее критическое исправление

Global budget/deadline после edit может оставить неизмеренный последний
кандидат. Controller selection уже выделен; новый native graph capture
готовится в рабочем дереве и ещё не собран/не принят. Автоматический terminal
restore полного графа, owner mirrors/C-state, новая revision/epoch и согласованный
export/replay пока не реализованы. Один новый kernel regression сейчас отказал.
[Полный контракт](TerminalBestStateBoundary-20261118.ru.md).

Дальше: разобрать этот отказ, проверить capture и реализовать законное terminal
восстановление; затем same-budget cold A/B и actual frozen8 с читаемыми графиками.
Параллельно завершить публикацию уже полученных heldout данных и графиков.
Остальные требования этапов сохраняются.8/8 не является условием окончания
рефакторинга; Exact требует свежей all-input проверки одной конечной модели.

## Последующее продвижение: захват native graph и новая сборка

Root47f532a7aef1253e03bac7073f192ea555e118e5 / Pulse57f603b1048d6547bda6e2e97f7decc0305715f0:
реализован process-local захват полного graph/Dataset/storage/C-state выбранной
контроллером измеренной точки. Добавлены6 native cases, исправлена постановка
одного отказавшего kernel regression. Автоматический terminal restore ещё
не реализован; [границы и следующий контракт](TerminalBestStateBoundary-20261118.ru.md).

На M40 canonical preparation пройдена. Свежая сборка и30 заявленных C++ cases
выполняются отдельно в s08-measured-native-boundary-sdk-m40-a1,
controls978af14a078abe3b90a6ca12a2cfe5c2333ec7b5. Supervisor3611226,
unit timelearner-d4980d0d-93d1-4d64-ac49-0ee632466cb6.service подтверждены живыми.
[Handle](../../../Reports/StructTrain/TimeLearner/MeasuredNativeBoundary-20261119/m40-native30-running.json).
Работающий runtime не обновляется, новый код в develop не принят.

В готовой Elder baseline/threshold галерее2391 PNG. Просмотрены16 исходных
overview всех паттернов и2 positive-lobe overview target/FP. Подписи и реальные
входы читаемы; общий full-recovery Y масштаб сжимает положительные отклики
молчащих проб. Для подробного сравнения этих проб ещё нужны положительные
companion views. Полная visual acceptance и публикация галереи не объявлены.
[Границы визуальной проверки](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/native-temporal-report-selected-visual-review.json).
