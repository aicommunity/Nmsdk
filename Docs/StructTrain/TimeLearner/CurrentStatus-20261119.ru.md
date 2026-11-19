# TimeLearner: проверенный статус на 19 ноября 2026

Актуализация после завершения native terminal-selection gates19 ноября.
Полная цель этапов0–12
активна. Полностью принят этап0; этапы1–12 частичны. Процент общей готовности
не назначается: оставшиеся алгоритмические и режимные проверки имеют разный
объём. Accepted root develop остаётся87e7da0205b6bb0d582f7b4f2551c935fd7f2350.
Рабочие ветки codex/timelearner-physical-model-data уже содержат source-retention,
historical export и новый native portable boundary schema8/summary9. Этот код
и расширенные интеграционные проверки ещё не приняты серверным gate.
Адресно принятые gates относятся
к Root3c5bfe01609a6e6bd290aa9697938e885d5904b6 / Pulse1d8fc24cdb19b4b0e399483d198314b84548f9ea.
Верхние разделы определяют текущий статус; записи ниже раздела истории
сохраняют состояния своих датированных попыток.

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
|M40: terminal-selection fresh SDK|44/44 PASS, включая14 terminal cases,6 snapshots и прежние регрессии; supervisor/все группы закрыты, primary опубликован.|
|M40: terminal portable fresh SDK A2|Собрано, выполнено56:44 PASS/12 FAIL. Все12 composite cases прошли; plain fresh-process warm cases запускались до native Init. Gate отклонён, все группы закрыты, primary опубликован.|
|Elder: независимый terminal-selection fresh SDK|14/14 PASS, supervisor/все группы закрыты, primary опубликован.|
|Предыдущий Elder: fresh SDK,14 targeted cases|13 PASS/1 FAIL. Постановка kernel case исправлена; его corrected version прошла на M40. Старый отказ сохранён, старый gate не переименован в успешный.|
|Предыдущий M40 gate29|25 PASS/4 FAIL. Четыре N0 ThresholdCandidate не получили исходного certificate, maximum_sweeps_exhausted; downstream проверки ещё не подтверждены. Persistence2 прошли.|
|Windows .14: heldout4|Native и полный audit завершены; TP1/FP0/FN0/TN3.|

[M40 report receipt](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/native-temporal-report-closed.json),
[Elder14 receipt](../../../Reports/StructTrain/TimeLearner/MeasuredBoundarySelection-20261118/elder14-closed-rejected.json).
Перечисленные ранее живые задания завершены; повторный запуск не выполнялся.
Прежние native jobs и portable A2 закрыты. Новых Train нет.
Эти адресные проверки не заменяют полную объявленную матрицу262Linux/261Windows.
[Native terminal acceptance](NativeTerminalSelectionAcceptance-20261119.ru.md).

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
|7|Measured bounded L/Ns/Rs search, N0 repeats, причины остановки, final verification; explicit terminal restore проверен44/44 M40 и14/14 Elder.|Новый source-retention/historical-export код, полный portable переход и cold/runtime/analysis integration; полная bounds/physics/reset/C-search матрица.|
|8|Solo/recognition state, transactions, реальное подтверждение порога, первые unseen foil.|Все PostTune/inhibition/reset modes и расширенная независимая frozen evaluation.|
|9|Корневой пакет/CLI, manifest357 и адресные migration gates.|Оставшиеся Bin analysis/matrix/shared tools и callers; complete=false.|
|10|Owned groups, leases/budgets, provenance и fail-closed publisher.|Полная effective-factor, cancel/recovery/publication fault matrix.|
|11|Реальные положительные и отрицательные результаты, order/window/reset проверки отдельных моделей, временные отчёты.|Систематическая legacy/V2 и физическая/режимная матрица, новые независимые условия и повторы.|
|12|Поддерживаемые отчёты; DOCXv3 Classic15/Branch14 страниц,9 примеров,29 страниц проверены.|Сквозная сверка root/PulseLib/Bin/config/ClDesc, завершение миграции и очередная актуализация примеров.|

## Ближайшее критическое исправление

Global budget/deadline после edit мог оставить неизмеренный последний кандидат.
Controller selection, полный native capture и explicit terminal restore с
owner mirrors/C-state, readback и physical epoch адресно проверены на обоих
серверах. Для обычных cold JSON возможность пока не включена. Новейший код
сохранения исходного графа перед transaction, historical export context и
factory schema8/summary9 ещё нужно проверить. Factory разделяет historical
proof и actual native model; import создаёт Finished DATA, без контроллерного
checkpoint и живых полномочий. Подготовлены fresh-process, warm-control и
tamper проверки. Все12 protocol4/5 cases A2 прошли;12 plain child checks
отказали из-за warm Start до native Build/Init. Исправленная постановка,
historical_summary на source epoch и4 новых plain completed cases ещё не проверены.
Полная native приёмка, cold/runtime declarations и Python analysis integration
остаются обязательной открытой частью.
[Полный контракт](TerminalBestStateBoundary-20261118.ru.md).

Дальше: завершить и проверить portable переход, затем same-budget cold A/B
и actual frozen8 с читаемыми графиками.
Открытая реализация детализирована в
[portable boundary design](TerminalPortableBoundaryDesign-20261119.ru.md):
включая no-transition/Exact, ранние stops, warm journal и все protocol families.
Параллельно завершить публикацию уже полученных heldout данных и графиков.
Остальные требования этапов сохраняются.8/8 не является условием окончания
рефакторинга; Exact требует свежей all-input проверки одной конечной модели.

## История попыток19 ноября: захват native graph и новые сборки

Актуальная отдельная попытка: Rootfb30b8be92bcfc006b94f1476d615dc8ab2ac03a /
Pulse19545036eecb884e2682c53b1a031a82abc82560. После успешной canonical
preparation на M40 запущена fresh SDK сборка с56 заявленными cases: прежние44
с расширенными source/portable/fresh-process/warm assertions и12 новых
composite transport cases. Controlsaa236d76b0fb8877652fa1db37160ae2e3ae11b2,
job s07-terminal-portable-sdk-m40-a1. Supervisor4104184/start412501038 и
kernel unit timelearner-7c732e30-bc8c-4918-b8c9-33b9f937d27a.service,
main4111704/start412504166 подтверждены живыми. Это ещё не native приёмка;
новых научных Train/Test нет. [Handle](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/m40-native56-running.json).
Следующие записи этого раздела — история предыдущих попыток, не активные jobs.

Уточнение A1: fresh build остановилась на двух сравнениях QJsonArray с
QJsonValue в новом factory. Выполнено0 из56 cases; supervisor и все группы
закрыты, reservations освобождены. Ошибка исправлена явным QJsonValue;
аналогичное сравнение исправлено в fresh-process тесте. Прежний A1 сохранён:
[primary и подтверждение отказа](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/m40-a1-build-failure.archive.json).
Исправление ещё требует отдельной свежей сборки и выполнения56 cases.

A2: Root3916cf6da8157cfbe84ef0f54a1a446824d70e0a /
Pulsec84a1c1e864786660d7626d2e577fb3b83eeb67b, controls8ee6c0d51980669ba605eddb0689768d417592a3.
Canonical preparation PASS, свежая native сборка56 cases запущена.
Supervisor2937/start412659767 и unit timelearner-106cf42b-4d8e-4fc5-94aa-aed858452471.service,
main10784/start412662722 подтверждены живыми. Старые A1 source/build/runtime
не изменены. [A2 handle](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/m40-native56-a2-running.json).

A2 завершена:56 выполнено,44 PASS/12 FAIL, gate отклонён. Во всех12
plain child failures warm Start предшествовал штатным Build/Init и получил
native_training_requires_initialized_ready_learner. Тест исправлен переносом
warm контроля после существующей инициализации, без дополнительных Build
в learner. Все группы/supervisor закрыты. [Полный primary](../../../Reports/StructTrain/TimeLearner/TerminalPortable-20261119/m40-a2-rejected.archive.json):
1013 проверенных members,17 log aliases,16116665 compressed bytes.
Новая рабочая версия добавляет source historical_summary, DATA audit schema8,
проверки28 native boundaries,12 plain и8 composite warm exports, а также4 plain completed controls.
Это код, ожидающий native и Python приёмки; ordinary cold JSON ещё не включает
terminal policy. Следующая серия содержит60 C++ cases; новые научные Train/Test
пока не выполнялись.

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

Уточнение исхода native30 A1: сборка production PulseLib завершилась, но сборка
теста остановилась: два SCOPED_TRACE на одной строке объявили одну переменную
gtest_trace_61 дважды. Выполнено0 из30 C++ cases; gate отклонён, все группы и
supervisor закрыты. [Исходный отказ](../../../Reports/StructTrain/TimeLearner/MeasuredNativeBoundary-20261119/m40-native30-a1-build-failure.json),
[закрытие](../../../Reports/StructTrain/TimeLearner/MeasuredNativeBoundary-20261119/m40-native30-a1-closed-build-rejected.json).
Rootd790786db21ae6d56cbb0e1fbbb70f9ef1b2d310 разносит trace declarations по
строкам. Для A2 подготовлены новые source/build/runtime, прежние A1 сохранены;
те же30 cases, тот же Pulse57f603b. Controls22cd7149c3e6ab83b1537fd7c8eb538594946e3a.
Canonical preparation A2 пройдена; native supervisor3701540/start411377128
и unit timelearner-c2590dc5-40e8-4c30-90f5-cc8b6b085bf8.service,
PID3709096/start411380156 подтверждены живыми. [Handle A2](../../../Reports/StructTrain/TimeLearner/MeasuredNativeBoundary-20261119/m40-native30-a2-running.json).
Результат30 C++ проверок ещё не получен; A1 и A2 являются разными попытками.

## Актуализация19 ноября: A3 и подготовленная terminal transaction

A2 завершилась до выполнения тестов: compiler отклонил три неявных преобразования
const UEPtr в native witness calls. Выполнено0/30; исходный отказ и закрытие
сохранены в m40-native30-a2-build-failure.json и m40-native30-a2-closed-build-rejected.json.
Root554b70a719ad712f402be608ca4d45826424fc82 использует явный Get().

Повторная проверка19.11,01:48МСК: A3 с этим Root и прежним Pulse57f603b
активна на M40, supervisor3804988/start411618921 и unit
timelearner-f8ffe62c-0dd3-4b34-9682-1121fd84deda.service подтверждены живыми.
Свежая сборка завершилась, compiled inventory записан; итог30 cases ещё
не принят. Это отдельные source/build/runtime, прежние попытки не изменены.

Pulseb5128706c91df017be58d81b029ee53139057b84 добавляет явную native terminal
transaction: после BudgetExhausted контроллер отзывает прежние полномочия,
на следующей before-children границе восстанавливает полный выбранный граф,
Dataset, owner mirrors и C-state с readback и резервом rollback из исходного
edit budget. История поиска и фактическая physical epoch разделены; сертификат
не создаётся. Подготовлены14 native случаев для обеих топологий/N0/N1,
Reset/external stop, C-state, нехватки edit allowance и отказа attachment.
Они ещё не собраны и не приняты; A3 их не содержит.

Это промежуточная native API-возможность. Обычные cold JSON её не включают;
versioned portable export/import/replay перехода ещё требуется. Старые exporters
отклоняют такой scope, чтобы не описать восстановленный граф как прежний
terminal search state. Следующий научный A/B требует закрыть эту границу,
затем выполнить cold Train и frozen8 при одинаковых бюджетах. Только этап0
полностью принят; полная цель0–12 сохраняется.

A3 завершена после предыдущей проверки: выполнено30 случаев,26 PASS/4 FAIL.
Все группы и supervisor закрыты. Четыре отказа — независимое сравнение пустого
owned C-state с захваченным: non-const JSON lookup добавлял baseline:null.
Исправлено чтением value() без вставки поля; исходный отказ сохранён в
[квитанции](../../../Reports/StructTrain/TimeLearner/MeasuredNativeBoundary-20261119/m40-native30-a3-failures.json).
Нужен новый native прогон исправления и terminal transaction;26/30 не приёмка.

После closure A3 запущены два независимых fresh SDK задания с
Root3c5bfe01609a6e6bd290aa9697938e885d5904b6 / Pulse1d8fc24cdb19b4b0e399483d198314b84548f9ea:
M40 terminal-selection-a1 —44 случая; Elder terminal-selection-a1 —14 новых
terminal cases. Обе canonical preparations пройдены, новые supervisors и
kernel units подтверждены живыми. M40 supervisor3925312/start411857291,
unit timelearner-512750df-162b-4924-b49b-c4eee1f2ad00.service; Elder
supervisor1516047/start461313628, unit timelearner-4cafdba4-833f-4255-bc82-b749478f45f3.service.
Итоги тестов ещё не получены. На Elder удалена только проверенная закрытая
старая build-measured-boundary-sdk-a1; source/runtime/primary сохранены.

Отдельно [исправляется читаемость положительных откликов](SharedRecoveryReadability-20261119.ru.md)
молчащих проб при общем recovery-масштабе. Это правка renderer с ещё ожидаемой
серверной и визуальной проверкой, без нового Train/Test или научного verdict.

## Принятая адресная проверка terminal selection

Оба задания закрыты: M40 **44/44 PASS**, Elder **14/14 PASS** на прежних
Root3c5/Pulse1d8. Подтверждены worker validation, полные фактические JUnit
inventories и whole-group closure. Native M40 suite603.953с, Elder193.913с.
Все6 snapshot cases проходят, включая четыре прежних empty-C отказа.
Полные primary обоих серверов опубликованы в external M40 archive.
[Область, артефакты и ограничения](NativeTerminalSelectionAcceptance-20261119.ru.md).

В рабочей ветке после принятой комбинации добавлены retention исходного графа
перед transaction и read-only historical export context для protocol3/4/5.
Эти новые изменения и расширенные14 source assertions ещё не проверены gate.
Полный portable terminal factory/export/import/replay и cold/runtime/analysis
integration остаются открытыми. Нового научного Train/Test не было.

На .14 создан отдельный report-renderer venv, headless matplotlib/Pillow
проверены. Общий Python и пользовательский C:/Projects/Nmsdk не изменялись.
Первый embedded Python не имел venv; отказ сохранён, успешный отдельный venv
создан через обнаруженный установленный полный Python. Генерация новых
научных графиков в нём ещё не запущена.
