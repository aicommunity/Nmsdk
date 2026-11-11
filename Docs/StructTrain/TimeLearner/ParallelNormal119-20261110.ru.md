# Полный native119: обычные Release-сборки Elder и M40 — 10.11.2026

После адресного Elder normal18/18 подготовлен полный119-case cohort на обоих обязательных Linux workers. Это дальнейшая приёмка реализации, не новая серия классификации и не завершение этапов1–12.

## Неизменяемые условия

Source355c60df066bdc8da09bd6d7872b47f6e71c0494 / Pulse165d49da7e65cd6ac59bca2812ce52884ddd50c2 / Rdkde4134235c0dcb8b91fd9a43b267348ad1a163ca / Bin8cb6dba07b30432272984c8ce3136b48ad06f064. Используются уже доставленные неизменённые source snapshots; новые build/runtime/output каталоги. SDK355 и worker1386206616d82952166ece926e814cd2c5aafbb9 имеют одинаковые native_acceptance_worker bytes. Canonical tool Elder98ed6da0da8bc0cb46512ebe92150570c2909206, M406bb8baeba6e01999860ad31813ab089b7a194e65; оба проверяют4074 source files,29 SDK modules и точные configure arguments. Смена инструмента не подменяет код проверяемого SDK.

На обоих workers Release/O3, LLM Off, без ASan, parallel2. Leaf4GiB/128tasks, whole worker8GiB/128tasks, timeout43200s, build10800s. По12GiB disk reservation и floor512MiB; перед запуском Elder свободно16361308160bytes, M40 Data около286GiB. На M40 прежний registry schema1 не подтверждает количественный admission: фактические kernel memory/tasks limits и path locks остаются обязательными, объявленную memory/disk величину нельзя выдавать за учтённую общей ёмкостью v2. Migration registry — открытый пункт этапа10.

## Полный состав

119 distinct IDs,42 leaf-группы,308 artifact rules перенесены без изменения из исходного119A2 declaration. Это не сумма18 с прежними PASS. В составе codecs11, cold7 guards2, public-bank11, actual owning replay4, manual R20, portable proof17, package6 cases29, Console/summary11, source6 recognition3, runtime2 codec11. Проверки могут завершиться отрицательно; недовыполненные cases не становятся PASS.

[Elder: заранее зафиксированная постановка](ValidationPlans/ElderNative119-20261110/cohort.json) и [живое kernel-наблюдение](ValidationPlans/ElderNative119-20261110/launch-observation.json): canonical completed/return0/diagnostics clear,66.657s; supervisor180136/start389341665, outer185780/start389342622 подтверждены живыми. Отдельные source/runtime предыдущего normal18 не меняются. Контроллер: /home/user/timelearner-refactor/readbacks/s07-native119-normal-a1-controller.

[M40 исходная постановка](ValidationPlans/M40Native119Normal-20261110/cohort.json) остановилась до компиляции: invalid_reservation_resources. По ошибке была скопирована зависимость от86 unrelated historical binding records; свежий job не читает и не изменяет эти старые задания. [Точные исходные exception/terminal/closure metadata](ValidationPlans/M40Native119Normal-20261110/preparation-rejected-a1.json) сохранены. [Независимая A2 постановка](ValidationPlans/M40Native119NormalRetry-20261110/canonical-plan.json) не ссылается на эти records; старый move18 runtime явно protected. Это исправление launch dependencies, не ослабление проверок состояния/физики/119 cases. Исходный failed preparation не переписывается.

M40 A2 canonical completed/return0/diagnostics clear,83.780s. [Фактический запуск](ValidationPlans/M40Native119NormalRetry-20261110/launch-observation.json): supervisor1049443/start339920576; статус outer running. Контроллер: /media/user/Data/TimeLearnerRefactor/readbacks/s07-native119-normal-a1-controller. Сборка и C++ verdict119 ещё не завершены.

## Дальнейшая приёмка

После завершения проверить119 unique completed cases, все308 artifact rules, первоначальные outcomes, source/resource/runtime immutability, actual loaded libraries и closure/lease. Сохранить все необходимые primary компактно в Git. Затем запустить actual Python package6 reader16 на полном новом корпусе (включая stopped/partial/default-sync/zero-group и legacy5), и настоящий Console cold Train→export→calibration/реальное подтверждение→frozen Test. Ни инженерный Exact при SyncTolerance0.2, ни frozen recognition fixture не дают автоматически stock N4 результата.

Параллель normal119 на двух workers не заменяет прежний отрицательный ASan C0 memory result. При совпадающем normal-поведении остаётся отдельно локализовать ASan memory overhead/retention по actual phases, не менять физику или критерии ради PASS. Повторное задание не запускается из-за SSH timeout: сначала проверяется та же process identity. SeriesD автоматически не возобновляется.
