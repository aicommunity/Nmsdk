# Следующая native проверка48: согласованная source preparation

> Текущее решение: следующая native48 будет собрана из НОВОЙ полной SDK956 в source-native48-fresh-m40-a1 и новом build-native48-fresh-m40-a1. План incremental reuse/source-update ниже исторический и superseded;438старыхobjects/184flags не используются заново и остаются неизменными. Разработка отдельного existing-SDK updater отменена как необязательная для этого процесса. Cohort48/37leaves/185rules/physics/profile15 сохраняются; нужны полная4030-file Git delivery иcanonical-only production preparation.

Source Root `956443560ebdb788a0642856381c9c6a7a554b76` получен обычным no-ff merge95e813 (общий test-only fix) и35fba3 (штатный owned-native controller). App/Tests/CMake и gitlinks точно соответствуют95; весь Scripts tree точно35. Pulse остаётся `f7a0e3e63ec29d4647790a695606d1ca32164ef3`. Runtime-проверки этого merged SDK ещё нет.

ПланV2 `3938176fcdaa5b48216b1ced0528581d45616915` опубликован в origin/codex/timelearner-native48-source-control-plan-v2; prefix Reports/StructTrain/TimeLearner/s10-native48-a4-source-control-plan-v2. Root независимо сверил [полные Git-derived дельты и состав cohort](Native48SourceControlRootReview-20261109.json):218 paths от f015 до956,3 пути test-fix и215 путей controller merge. Projected executable/source delta —18Scripts+1test TU. Старый план44903, ошибочно перечислявший только test-fix delta как полный, сохранён в V2 evidence и не используется для обновления SDK.

Группа содержит48cases =37прежних+11непосредственно затронутых,37leaf groups/185artifact rules. Фактический fresh compiled inventory обязателен: source ID inventory не подтверждает запуск. Новые routing cases проверяют N4/N6 и сохраняют actual primary; JUnit-only случаи явно отделены.

Перед source update нужен свежий readback закрытого A3:438compile objects,184flags и cache1281 сохраняются байт-в-байт на этапе обновления исходников. Следующая сборка называется incremental; runtime/output/canonical/controller A4 новые. External canonical/job заранее объявляют argv и preparation в будущем controller/inputs; подготовка не создаёт этот controller, owned launcher копирует bytes без JSON rewrites/hash cycles.

Серверная source SDK не обновлена, сборка и48tests не начаты. Приёмка40actual checks и11kernel units подтверждена отдельно, но их полный сбор штатным data-driven CLI ещё выполняется. До него и свежей production preparation не заявляются ready runtime, archive2/service5 или научные результаты. Полная scientific matrix и исходные этапы1–12 остаются открытыми.

## Изолированная доставка Root956

Root доставил отдельный donor /media/user/Data/TimeLearnerRefactor/source-native48-root956-donor-m40-a1; все1014 физических Root-файлов независимо сверены с ожидаемым Git-mode/blob/size/SHA ledger, без materialization семи submodules. [Raw delivery, полный ledger и pack audit](../../../Reports/StructTrain/TimeLearner/s10-native48-root956-isolated-donor-root-verification/index.json) сохранены в компактном Git. Это не обновление прежней SDK и не приёмка полного4030-file дерева. Сборка/модели не запускались.

Source-pack review уточнён: прежняя Root-квитанция для1b8 проверяла bytes/SHA самого pack, но не полноту checkout closure. Последующий standalone ODB audit нашёл отсутствие пятого Git-control blob (Docs/Audit/.gitignore), исключённого из физической source projection. Старый pack не доставлялся. Исправленный V2 pack6704171B/SHA870f9b3f содержит этот control, полный1014-file код и требуемые tree objects; Root доставил только его. Это исправление упаковки, source commit956 и ожидаемые1014/4030-file ledgers не меняются. Старый план393 и квитанция сохранены как исторические; дальнейший source update обязан использовать новый versioned descriptor, не старый1b8.

## Новая полная SDK доставлена

Root выполнил8Git deliveries в source-native48-fresh-m40-a1 и независимо сверил все4030физическихфайлов: Root1014,Motion93,Hardware356,Pulse342,Cv132,Basic43,Bin269,Rdk1781. Все8HEAD чистые,7gitlinks точно совпадают сRoot956, object alternates отсутствуют. [Полный rawledger, восемь delivery receipts иSHAindex](../../../Reports/StructTrain/TimeLearner/s10-native48-fresh-sdk-root-verification/index.json) сохранены в Git. Старые source/build/runtime не использовались для записи;438старыхcompile objects не переиспользуются.

Это source materialization, не compiled runtime и не приёмка модели. Следующие шаги —29actualSDK imports, canonical-only production preparation сfreshpaths иполнаяноваясборка. Свежий план dcf2c92d1123fc963cf1568cc5c194b980669dfd опубликован отдельно; никакой existing-SDK updater для этого процесса не разрабатывается. Cohort48/37leaves/185rules ифизика/допуски остаются прежними.
