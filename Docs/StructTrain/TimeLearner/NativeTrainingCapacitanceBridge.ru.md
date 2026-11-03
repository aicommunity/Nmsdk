# Механический мост полного C-состояния в native API

Подэтап7, ещё не принятый runtime. Общий модуль Pulse Core/TimeLearner/
NativeTrainingCapacitance связывает typed TrainingCapacitance с существующим
native C₀ owner. Оба learner сохраняют классы/режимы/config loading и получают
два C++ метода: ReadNativeTrainingCapacitance и ApplyNativeTrainingParameters.
Новых XML properties или действующего фактора C-trim этот API не создаёт.

## Контракт

```text
read at an idle/completed physical boundary:
    absent owned C0 -> nullopt (unknown, never fabricated unit baseline)
    validate signed native state against actual graph/physics/model revision
    merge active + dormant map and witnessed unit paths
    bind origin to original capture/model spec/immutable profile fingerprint

apply full L/Ns/Rs + absolute per-membrane scale map:
    validate actual owned state and requested positive finite bounded values
    reject missing baseline, changed origin/policy or lost known path
    retain the native owner's original C0 witnesses
    translate the complete map to the existing joint native edit
    let the prospective native graph determine active/dormant paths
    extend new C0 only from verified storage images, then apply atomically
```

Origin — canonical SHA256 объекта kind=timelearner_training_capacitance_origin,
schema_version=1, capture_model_revision=baseline.model_revision,
model_spec=baseline.model_spec, storage_images_sha256=baseline.storage_images_sha256.
Он намеренно не равен baseline.sha256: последний меняется при расширении
проверенного channel inventory после роста. Исторические unit paths сохраняются
в полной карте вместе с ненулевыми поправками временно отсутствующих мембран.
Новые неизвестные paths не признаются по имени: joint preview обязан доказать
их существование и происхождение C₀. Сам bridge не меняет C₀/образ/структуру.

Read при queued/running probe запрещён: временная Branch isolation не является
solo model boundary. Apply использует обычные native ownership/probe/integrator
ограничения; отказы подготовки возвращают Rejected без live mutation.
Не вызываются Calculate/Default и не меняются prototypes, Ready или частоты.
Владельцем параметров остаётся модель; pure controller хранит полный map/origin,
а не собственную копию baseline или подставленное parent/default C.

## Подготовленные проверки

NativeTrainingCapacitanceBridge: Classic/Branch × N0/N1 при2000Hz, реальные
storage/Environment и production API. Fresh unbound read не создаёт provenance;
первый bound edit сохраняет heterogeneous C₀. Проверяются stable origin при
расширении baseline после роста, unit scales новых paths, общий shrink/C edit,
dormant scales, joint growth с поправкой ещё не существовавшего канала и C₀
из storage_image. Новые значения сравниваются с эффективными дочерними каналами.
Смена origin/policy, потеря известного path, nullopt при bound owner, NaN и
фиктивный path должны отклоняться с конкретной причиной, без изменения всего
semantic model и native state. Read не должен входить в lifecycle живого нейрона.

Каждый probe сохраняет реальные input/soma CSV и полный evidence packet;
каждая фаза — semantic graph, native signed state и typed map. Эти engineering
пробы не являются научной классификацией или доказательством convergence.
Спецификация native-training-capacitance-bridge-v1.json содержит4 случая.
Первый полный SDK gate bridge-regression добавляет130 ранее unit-проверенных
controller/observation/final/proposal cases: всего134. До этого SDK с новым
модулем ещё не собирался; ранее130 normal/ASan были isolated production units.
Новые сборки/тесты выполняются только на разрешённых workers после закрытия
текущих leases. Визуальные отчёты и independent bridge evidence reader ещё нужны.

## Что остаётся до C-trim On

NativeTrainingService/Bindings ещё не передают map в actions/domain/readback.
Нужно связать всю историю кандидатов/повторов с фактическими физическими
witnesses, добавить versioned summary/domain codecs и independent readers,
совместный N1 domain на том же C, native comparisonScope, начальное владение C₀
до первого C-search edit, конфигурацию bounded policy и сам измеряемый поиск.
CapturedPerInput, anchor, defaults амплитуды/sync и legacy absolute-F
DendriteCapacitance не меняются. ControllerVersion2 с C-trim On продолжает
отклоняться; bridge и весь исходный план не объявляются завершёнными.

## Уточнение до первой SDK-сборки

При source review сужена область catch в фасаде: Rejected с гарантией отсутствия
live mutation относится только к подготовке correction. Делегирование native
editor выполняется вне этого catch, сохраняя его failure/rollback контракт.
Иначе исключение после физического commit могло бы ошибочно выглядеть как
безопасный отказ подготовки. Исправление Pulse a58489d8a2d3311719e5f70b8c7781de439ea8cc
не меняет математические кандидаты или допуски.

Первая очередь H1 с rootabf65a9cc отменена до source/build/runtime mutation:
проверены PID/start_ticks314367/324253090 и314368/324253090, отсутствие детей,
неизменность source4d501d611 и продолжающий работу normal43 owner297669.
Численные tests H1 не запускались. Исправленный H2 должен ждать successful
normal43/readers26 и закрытия их owners; production/runtime ещё не проверены.


## H2 остановлен на prerequisite; повтор normal G2

H2 root40a9cb496a7fb92a3618eef3e108ad59074c5316, owner326560/324332166
не приступил к checkout/сборке: normal G1 дал41/43 вместо полного PASS.
Receipt e9546bd63846cc8df54b3fa3eb0a0c72c69074e8 проверен:3 members/598bytes.
Это отказ prerequisites, а не результат выполнения134 bridge tests.

Причина двух G1 failures — повторная регистрация fault-only rollback factory
из разных fixtures в одном storage. Исправлено только имя тестовой фабрики,
с учётом rig.name; native import/rollback, Rdk collision checks и допуски прежние.
Elder G2 root496a80d7190cafcc1e96329ee3c8e2b17cb40114,
owner330097/324362522, publisher330098/324362522 повторяет43 native +26 readers.
До изменения source проверены весь архив G1 и закрытие его owners; process guard
не обнаружил пользователей source/build. Bridge требует нового отдельного
задания после successful G2; H2 автоматически не возобновляется.


## Подготовлен independent reader: приёмка pending

Новые frame snapshots содержат фактическую storage dependency closure, повторно
прочитанную через CaptureModelImageDefinitions с дополнительными image roots
всех baseline channels, включая dormant. Это отдельный readback registry, а
не копирование baseline.storage_images в поле доказательства.

`analyze FILE --format training-capacitance-bridge` проверяет все6 фаз в порядке,
semantic model hash, signed baseline/state, эффективные C=C₀×scale, физику каналов,
registry profiles, полную typed map active/dormant/unit paths и вычисляемый origin.
Между фазами запрещены recapture исходных полей baseline, потеря прежних channel
witnesses и history paths. Фаза отказов обязана сохранить весь model/state/map.
Reader не выдаёт training certificate и явно не подтверждает native import,
probe observations или классификацию.

Подготовлены7 production-reader tests на4 реальных bridge records: позитивный
полный разбор, CLI, неизвестная схема/неполный inventory, forged origin, потеря
dormant map, отсутствие registry snapshot и изменение физической C с пересчётом
всех затронутых digest/revision (проверяется численная физика, а не stale hash).
До server gate эти tests не исполнялись; никакого PASS пока нет.


H3 поставлен в очередь после успешного normal G2: source
1c992e4ab95d6c467f9b006808c8b8046d180781, owner333776/324382901,
publisher333777/324382902. Он выполняет134 SDK/native cases и7 independent
reader tests на своём immutable snapshot. Работающий G2 source не изменён.

При дополнительном review reader усилен восьмым negative control: изменение
maximum_relative_change одновременно в native/typed state с корректным новым
digest не должно пройти проверку неизменной policy между фазами. H3 сохраняет
свой ранее объявленный snapshot; отдельный reader-only gate должен проверить
новую версию на тех же фактических H3 артефактах через Git archive, без изменения
leased SDK source/runtime и без повторного численного расчёта.


Reader-only I1 поставлен в очередь: source9e1d1a73987f90f3be9e725f37fc5acc80d2d2c2,
owner335141/324394463; ожидает опубликованный successful H3 (native134 +reader7).
Перед анализом проверяет SHA256SUMS, bundle, каждый tar member и полный inventory.
Пакет Python извлекается из Git archive в отдельный каталог;8 tests читают четыре
H3 records, SDK source/build/runtime не затрагиваются. Опубликованный результат
должен включать source-file hashes и ссылку на исходный native evidence commit.
На момент постановки I1 находится в ожидании, PASS отсутствует.


## Подготовлен typed N1 domain/schema3, runtime pending

Оба learner получили AssessNativeTrainingResistanceDomain. Requested complete map
строго разрешается через текущий owner. Native совместный preview L/Ns/Rs/C
формирует effective map (допустимы только новые доказанные unit paths), signed
C₀/state с preview revision и отдельный storage-image readback. Requested map
сохраняется отдельно как контекст действия контроллера; effective map описывает
сам preview. Live model/owner не изменяются.

Старые domain calls остаются schema2. Explicit typed call выбирает schema3:
requested_capacitance, effective_capacitance, capacitance_state,
capacitance_storage_images. Available без полного witness запрещён. Unsupported
может иметь null effective proof; он не подтверждает физику. Python reader
проверяет все новые поля, native C₀/registry/C, requested/effective соответствие
и пересчитывает Rs bounds по тем же реальным каналам. Скрытие C-полей под schema2
запрещено. Native summary/service/adapters пока не используют эту capability.

N1 части четырёх bridge tests расширены: domain preview сверяется с последующим
фактическим joint commit по полному hash/state/map; изменение policy отвергается
без изменения live model. Добавлены7 independent domain-reader tests на двух
реальных Classic/Branch N1 records, включая resigned physical C corruption и
проверку связи с исходным/конечным графом. Эти изменения ещё не собраны и не
исполнялись; для них нужен отдельный SDK gate после H3/I1 и ASan.


Добавлена восьмая domain-reader проверка: настоящий прежний native API вызывается
для того же L/Ns/Rs/C; schema2, status, полный preview и Rs endpoints должны
совпасть с новым typed API. Это проверка существующего production path, а не
перекрашивание schema3 JSON под старую схему. SDK/reader16 gate (bridge8+domain8)
должен использовать production validation.run_suite с полным объявленным
inventory, package/fixture fingerprints и structured skipped/failures/errors.


## Очередь J1: SDK134 + structured readers16

Source92787e4962a5674f3f622ae06a60e71b09a901c6, Pulse
8b5d8f8262c097928daf0789ace14189fad85e3c. Elder owner342716/324461355,
publisher342717/324461356. Ожидает published successful H3 (134+7) и I1 (8),
проверяет primary closure и закрытие predecessor owners до изменения source/build.
Затем запускает134 SDK tests (N1 bridge cases теперь включают domain), после
них production validation.run_suite: bridge8+domain8, полный фиксированный
список16 IDs, package fingerprint, fingerprints фактических JSON fixtures,
структурированные failures/errors/skipped. Publisher требует executed16, exact
inventory, нулевые failures/errors/skipped и завершённый valid native134.
Синтаксис трёх новых/изменённых Python модулей проверен на Elder из Git92787e496,
это не замена runtime tests. На момент постановки J1 ожидает prerequisites.

M40 ASan transport G2 source496a80d7190cafcc1e96329ee3c8e2b17cb40114:
owner2621211/274992757, publisher2621212/274992757. Ожидает successful normal G2;
это gate automatic owner/transport43, а не новой typed domain реализации.
Для schema3 domain по-прежнему нужен отдельный ASan gate после normal J1.


## ASan owner temporal report и сравнение waveform, 03.11

Для ASan C3 primary d7cace1f5f9f62385b97281d0d1f48770e7153fd на M40
запущен production native-test-run renderer: source2736598f113cbb48874240696b46955ab840fb90,
owner2627462/275036158, renderer2627516/275036447, publication owner2627463.
До запуска проверены все261 archive members. Код извлечён через Git archive
в отдельный readback; leased SDK source/build не меняются. Используется существующий
plot-venv-a1 (matplotlib3.9.4, Pillow13.0.0), штатный Agg renderer.
Первый bootstrap с short root ref и следующий запуск с системным Python завершились
до создания cache; их exception/ownership receipts сохраняются, численных прогонов
не было. Текущий C3c использует full SHA и проверенное окружение.

Полный отчёт48 engineering two-pulse probes/72 soma pairs сохраняется только в
/media/user/Data/TimeLearnerRefactor/report-cache/s07-capacitance-owner-asan-c3c.
Каждый soma имеет overview и native-sample zoom с input overlay, без downsampling,
PNG1920×960 и минимум8px/native tick на zoom, SVG/PDF. Publisher проверит
рекурсивный file inventory и все cache hashes. В Git предназначены manifest/checksums
в gzip и выбранные overview/peak zoom для всех8 Classic/Branch ×N0/N1×2k/20k
после regrowth на каждом soma; полный cache не публикуется. Direct visual review
и global visual acceptance пока не заявляются.

Отдельный server-анализ5c7838123aafa54597b4f66e0a1a2a08f462a1f9 уже опубликован
и проверен: Normal C2 a928fb92edd0880728a697da0fed6d7ede3e7d4a против ASan C3
d7cace1f5f9f62385b97281d0d1f48770e7153fd. Все48 CSV побайтно идентичны,
95088 строк, нулевые отличия времени, stimulus и каждого soma column. Перед
сравнением проверены все259/261 archive members и inventory8/8 каждого источника.
Это равенство записанных откликов конкретных engineering probes; из него нельзя
вывести классификацию8 паттернов, сходимость, эквивалентность всей динамики либо
завершение C-search/service integration.


## Подготовлен explicit initial C₀ bind, runtime pending

BindNativeTrainingCapacitance(limit) в обоих learner закрывает metadata-only setup
до первого search action. First bind требует Idle native controller без references
или search, незамороженную модель, ModelSpec и legal probe boundary. Из реальных
C/physics/graph/storage создаётся полный unit owner; подписанный state и actual
readback валидируются до присваивания. Модель/параметры/scheduler/lifecycle/dynamics
и epoch не меняются; Build/Reset/Calculate/Default не вызываются. Повторный bind
возвращает проверенный существующий owner, не recapture trimmed C и не меняет
policy. Это явная декларация текущего исходного состояния, а не восстановление
утраченной истории/cold-start proof. Native service пока не вызывает bind.

Подготовлены4 real native fixtures Classic/Branch ×N0/N1 при2k, heterogeneous C,
отказы NaN/смены policy, повторный bind после реального trim, сохранение graph,
C₀, Idle/no fake tick и epoch. Публикуются3 полных frame snapshots и actual probes.
Independent binding reader/CLI проверяют реальные C₀/registry/C и full typed map,
неизменность физической модели при unit bind и исходной baseline после trim.
6 reader tests на4 actual records включают подмену первого graph другим валидным
actual snapshot (не stale hash), потерю registry, fabricated owner и schema/phase
ошибки. Native lifecycle и cold history reader явно не считает доказанными по JSON.

SDK gate binding-regression содержит138 случаев (предыдущие134 +binding4);
после успешного J1 нужен отдельный gate138 и structured readers22 (8+8+6),
затем ASan. Эти изменения ещё не собирались/исполнялись, PASS отсутствует.
После этого всё ещё нужны service/adapters, полные физические witnesses истории,
summary schema3/readers, C-search policy и измеряемые действия поиска.


## Дополнительная граница references → Reset → first bind

Добавлены2 native случая Classic/Branch N1: штатный scheduler собирает реальные
reference packets; external stop не объявляется сходимостью, затем Reset learner
сохраняет references. First C₀ bind после этого обязан отказать с конкретной
причиной initial_model_boundary и не менять graph/owner/lifecycle. Independent
reader проверяет оба actual reference packets, их уникальные IDs, revision и
неизменность graph. Это дополняет4 initial unit-bind/trim fixtures.

Текущий binding SDK inventory —140 (134+6), structured readers23
(bridge8+domain8+binding7); предыдущие138/22 в журнале относятся к подготовке
до добавления retained-reference guards. Все новые случаи ещё pending runtime.


## Закрыт normal43/readers26; full closure и визуальная проверка

Combined evidence7ec395554f0f8d506c08b587ba130025d0af1719: прежний native43
ccfa43c1 +исправленный reader snapshotc63d1b7b9c08c7542398ca944bcc7cf22e5ea2b4
дали26/26 production validation checks без failures/errors/skips. Проверены11
archive members/16660bytes, все278 source-file hashes и actual Git diff/gitlinks:
C++/CMake относительно496a80d719 неизменны. Численные пробы не пересчитывались;
исходный G2 verdict not_accepted не переписан. H3/J1/K1 остановились на своих
failed prerequisites и не считаются SDK/runtime проверками новых API.

Elder H4 заново проверил1062 numerical primary members и11 reader members,
закрытие старых owners и начал SDK134+reader7 на неизменном mechanical snapshot
1c992e4ab95d6c467f9b006808c8b8046d180781 (owner371101/324683009).
На actual H4 captured frame уже найден witness gap: baseline содержит dataset
и generator, а отдельно снятая registry closure только channel roots их теряет.
В root snapshots и typed domain это исправлено перечислением ВСЕХ имён из
baseline.storage_images при новом чтении storage. Аудитор не ослаблен; добавлены
три controls потери unused NDatasetMatrix image с конкретным profile-mismatch
reason. Новый integrated SDK140 теперь требует26 readers (bridge9+domain9+binding8).
H4 источники не меняются во время его работы; исправление ждёт нового gate.

M40 ASan G3 sourcec63d1b7b9c08c7542398ca944bcc7cf22e5ea2b4, owner2662153/275233732
начал новую сборку43-case transport и structured readers26 после проверки combined
G3 и всех original primary. На основании измеренных ASan затрат native outer
budget установлен43200s; это execution budget, не допуск сходимости. C3/старые
G1/G2 не возобновляются.

Temporal cache C3c завершён:48 complete probes/72 soma pairs,2697 PNG+SVG+PDF,
8895 file hashes проверены; размер760289883bytes остаётся на M40 Data. Compact
098e81688f2be8eded64e528b619c9f522d559bf содержит26 PNG;
6da96040f04a9fa57f343bc7f6afe4b649a6a76e добавляет6 local-Y peak views.
Проверены34+7 file hashes и согласованность с cache checksum manifest; все32
PNG1920×960 открыты и просмотрены напрямую. Заголовки/оси/легенды и input overlays
читаемы; в20k narrow shared-Y peak views вертикальная форма почти плоская, поэтому
обязательна парная local-Y детализация. Она явно подписана; общий масштаб остаётся
для сопоставления амплитуд. Sidecar review сохраняет точные SHA каждого PNG; raw
pre-review selection metadata не переписана. Global visual acceptance всех2697
PNG и scientific verdict не заявляются.


## H4: first full SDK run, owning JSON value correction

H4 evidenceea4ae160c957846e3dcf6e6ff5ffa8c78b3beba9 проверен:219 members,
3902211bytes. SDK/Console собраны, все134 cases выполнены:130 PASS,4 bridge
failures на одной EXPECT_DOUBLE_EQ. Actual created C=9.5e-10, сохранённый
baseline.channels.Dendrite1_4.ExcChannel=1e-9. Тестовый `const auto c0 =
baseline["channels"].toObject()[...]` сохранял borrowed QJsonValueRef от
временного QJsonObject; после дальнейших allocations чтение ожидания давало0.
Исправлен только тип c0 на owning QJsonValue. Численное ожидание C₀×.95 и
допуски не изменены; native algorithm не менялся ради прохождения assertion.
Bounded search по relevant Core/TimeLearner и root integration tests не нашёл
других таких сохранённых refs без завершающего owning преобразования; conditional
ModelArchive expectedIdentity имеет common owning QJsonValue type от const identity.

Reader7 H4 не запускался после native failure. Отдельно подтверждён и исправлен
registry closure gap по actual H4 snapshot; это независимый от Qt-ref дефект
witness producer. Ни H4, ни новый140/26 integrated gate не считаются принятыми
до полного runtime/independent анализа. ASan43 G3 проверяет прежний automatic
owner, а не эти новые API/test changes.


## Следующая приёмка объединяет old owner и новые metadata API

Для corrected snapshot выбран integrated SDK183: binding6 +bridge/domain4 +
130 pure production cases +прежние43 native ownership/transport/regression cases.
Это проверяет взаимодействие новых Core changes с уже адресно проверенным
automatic owner в одном SDK/runtime и одном storage process. Focused140 spec
сохранён для адресной диагностики. Independent validation —52 declared tests:
прежние26 native/transfer/dormant controls +новые26 bridge/domain/binding controls.
Все inventory/fixture/package fingerprints должны пройти production validation.
Допуски, модели, научная цель и алгоритм поиска ради gate не менялись.
Это будущая проверка, не текущий PASS и не научная classification.


## H5 запущен на отдельном runtime после закрытия H4

Source627b601547bf80fae08e1ebad26cdecaabc9c85e, Pulse
7707be2d19aeaf653d3430277426637a88ab967d, Rdk acc3de8d, Bin39d811e5.
Elder owner400316/324934774, publisher400317/324934775; отдельный
runtime-s07-capacitance-owner-integration-normal-h5. Перед checkout проверены
combinedG3, исходные1062 numerical members,11 reader members и219 H4 members,
закрытие старых owners и отсутствие пользователей source/build. Это новый
SDK183/structured readers52, не автоматическое возобновление H3/J1/K1.
Новые producer closure и owning QJsonValue проверяются теми же физическими
ожиданиями; positive runtime результат пока отсутствует.

Одноразовая отправка orchestration code превысила Windows command-line length
и была отвергнута до создания процесса. Повторная передача использует временный
локальный файл только с кодом, credentials по stdin и прежний проверяющий known
hosts SSH helper. Project sources/config/results по-прежнему только через Git;
пароли не записывались в файлы. После успешного запуска handles проверены живыми.

## Read-only physical witnesses: следующий адресный gate

Pulse9490b7a73ad3b1bbb05c4c025af866fce667a0ea добавляет
`ReadNativeTrainingCapacitanceWitness` в оба learner. Он возвращает typed full map
и independently capturable native identity/state/actual registry closure одного
revision. Проверяются actual C, исходный storage profile и неизменность identity
вокруг capture; unbound остаётся unknown, во время пробы чтение запрещено.
Метод не вызывает lifecycle, не ремонтирует физику и не создаёт новый C₀.

Bridge tests дополнены сравнениями witness с independently captured frames,
сохранностью lifecycle/epoch, fault injection actual child C без обновления owner
и отказом во время настоящей scheduled probe. Новые assertions runtime pending:
H5 использует прежний immutable snapshot и не подтверждает это дополнение.
План следующей адресной проверки: существующие четыре bridge cases Classic/Branch
N0/N1 плюс18 independent bridge/domain readers; после полного закрытия owners H5
и проверки его evidence. Не включать C-trim/service до versioned history schema3
с физическими witnesses каждого candidate/repeat/final и независимым reader.

H6 queued на Elder: source36af2933e738b83fce25070c083f41cc810a8b11,
Pulse9490b7a73ad3b1bbb05c4c025af866fce667a0ea, supervisor410902/325014434,
publisher410903/325014434. Readbacks s07-capacitance-witness-normal-h6 и
s07-capacitance-witness-publication-normal-h6; runtime отдельный. До verified
H5 PASS183/52 и закрытия обоих его owners H6 не выполняет checkout/build.
Далее дополнительно проверяет actual source/build users. При провале prerequisite
новый native run не запускается. Текущий H5 и ASan G3 не перезапущены.

Следующий commit дополняет provider version1 encoder и независимым
`training_capacitance_witness` auditor/registry. Каждая ссылка на revision
обязана иметь full physical witness; таблица не может менять origin/policy,
поля исходного baseline и общие C₀/physics/class/origin entries при росте.
CLI `analyze --format capacitance-witness` возвращает только physical audit,
без probe или scientific verdict. Summary1/2 и NativeTrainingService пока не
переведены на schema3: активация без сохранения истории остаётся запрещённой.

Добавлены20 production witness artifacts (четыре bridge cases ×пять bound
frames), assertions native encoder и10 independent witness tests с corrupted
revision/map/number/profile/C и missing required revision/policy controls.
Проверки требуют реальных server artifacts; локально выполняется только syntax
inspection. H6 pinned до этих изменений и не подтверждает codec/registry.

H7 queued: sourcefb772a354ff69568f97eada6303395cdb4247acd,
Pulsee87139062cefb537e1ba73103ca68bcf5c2a00a0. Elder supervisor413740/325039485,
publisher413741/325039485 (проверены receipt и живой PID), readbacks
s07-capacitance-witness-codec-normal-h7 и
s07-capacitance-witness-codec-publication-normal-h7. Gate4 native/28 structured
readers запускается только после verified H6 PASS4/18 и закрытия его owners;
H6 в свою очередь ждёт H5 PASS183/52. Уникальные runtime roots, immutable SHA и
actual process guard сохраняются. Никакого PASS этих очередей пока нет.

## Service history/schema3: подготовлен следующий integrated snapshot

В NativeTrainingPlan добавлен recordCapacitanceHistory=false. Explicit true
требует существующего bound C₀, не захватывает baseline автоматически. Общий
native adapter предоставляет read-witness, full-map edit и typed N1-domain
callbacks, но выключенный plan их не вызывает. Service передаёт initial C map
в bounded controller, валидирует full readback после edits/domains и хранит
свидетельства до queue и после TakeResult/observation sink. Running ticks не
снимают witness и не выполняют дополнительных Calculate/Reset/Build.

Исправлена структура registry: ключ — canonical SHA полного witness, физический
model_revision остаётся отдельным проверяемым полем. Один граф может иметь две
разные допустимые dormant histories; revision-keyed таблица теряла бы контекст.
Новый контроль воспроизводит такую коллизию. Summary3 сохраняет C maps и IDs
references/candidates/repeats/domain bases/current model. Read-only evidence
сохраняется при Reset, target invalidation очищает его. Ошибка свежей проверки
не выдаёт старый witness за actual только из-за совпавшего physical hash.

Root production auditor сначала проверяет physical history, C₀/storage continuity,
actual Ns/Rs и stimulus bank bindings, затем повторно вычисляет references,
candidate/repeated residuals и final certificate из primary observations/CSV.
Явный require_certificate=false разрешает анализ завершённой diagnostic history
с exact=None/certificate_verified=false; default certificate gate остаётся строгим.
CLI analyze --format capacitance-history требует точный primary trial inventory.
Schema1/2 с unversioned C-полями отклоняется; исторические data не переписываются.

Подготовлены10 native controls: шесть service N0/N1/repeat runs, два unbound refusals
и два observation-sink dormant-only faults с неизменным model hash. Новые12 reader
checks проверяют реальные traces, повторные группы, reset, пропуски, counterfeit
C/Rs/context и оба отказа. Existing witness checks11 также требуют actual encoded
frames. Следующий normal197 spec =183 previous +10 new +4 legacy service regressions;
independent suite75 =52 prior +11 witness +12 history. Пока это код/declared inventory,
не выполненная приёмка. H5/H6/H7 используют прежние immutable snapshots.

Ограничения, которые остаются обязательными: ConfiguredNativeTraining codec ещё
не включает record flag; learned-state package/import3 должен сохранять boundary
reference/current witnesses. Чтобы не терять их молча, прежний export tracked run
явно запрещён до schema3. C-trim On/search policy не включены. Старый module
test_native_evidence по source всё ещё ожидает service negative certificates там,
где текущий RunNativeTraining сохраняет diagnostic summary без certificate; его
полная актуализация/повторный runtime остаётся отдельной открытой задачей.

H8 queued после H7: rootac1244e4ce2065a6266fffe3a17dd428923800ae /
Pulse2cd80bb573f0e1407aba75d53706cac198043c39, Rdkacc3de8d/Bin39d811e5.
Elder supervisor427223/325160769 и publisher427225/325160769 проверены живыми;
readbacks s07-capacitance-history-normal-h8 и
s07-capacitance-history-publication-normal-h8. До verified H7 PASS4/28 и закрытия
его owners worker не меняет source/build; затем actual process guard и immutable
checkout/build отдельного runtime. Native197/structured readers75 ещё не запускались.
H7 проверяет прежнюю revision-keyed registry утилиту; её результат не подтверждает
новые evidence IDs, service tracking или summary3. Для этого нужен именно H8.

При последнем poll H5 live155 завершённых successes/0 failure lines, M40 ASanG3
live7/0. Это промежуточный stdout, не финальный expected inventory/verdict.


### Уточнение после восстановления VPN, 2026-11-03

H5: native183/183 PASS сохранён в60bc2936916ef00059278bd196a553a4c3b6b8f7.
Два reader errors происходили из отсутствия переданного CSV при наличии primary
файлов. Исправленный reader source c364899db6c553c247399c06df3130a9d6baf370
проверен отдельно:52/52 PASS, combined evidence
9cf5aaa6c67678f0bab5d3ce35800e17f064c55d. Исходный failed verdict не переписан.
H6/H7/H8 остановились на prerequisite; numerical checks не запускались.
H8b/H8c завершились compile failures, сохранёнными в3731817db28d5cd7fef608896fbe8e6d87173f7f
и78eb539b9284ef5e5bcdd9b492ad625b63591c7c; исправлены include и native pointer view.

Актуальный H8d: root ff2451a9936afaf712386edcd5013ad91784dd10,
Pulse1e62f4d3aedba4ff8a456af0c592aaa7b53fd776. Обе цели успешно собраны.
Supervisor506379/start_ticks325840639, native CLI510768/325871989 живы при poll.
В промежуточном stdout130 successes и один завершённый failure: test ожидал
invalid_argument от изменённой live C, фактически владелец сообщил runtime_error
capacitance_state_does_not_match_model. Следующий case сообщает то же несовпадение.
Кандидат test теперь требует runtime_error с точным диагностическим текстом и
по-прежнему проверяет неизменность графа/lifecycle. Текущий run не перезапущен.
M40 ASanG3 также жив:15 завершённых successes, длительные20kHz cases ещё идут.
Это промежуточные наблюдения, не финальная приёмка197/75 либо43/26.

Подготовлен следующий кандидат portable boundary/configuration schema3.
Он сохраняет C₀/current witnesses и trial bindings через model import/export,
не обещает checkpoint посреди пробы/поиска, проверяет реальную C/C₀-физику, а не
только digest. Добавлены12 native controls и12 readers; новый declared gate209.
Python readers version4 отличает эту семантику от прежних отчётов.
Проверены только AST Python, уникальность inventory и whitespace diff локально;
серверная сборка/проверка кандидата ещё не выполнена. C-search On, полная матрица
режимов и остальные открытые пункты исходного плана остаются обязательными.


H9 поставлен в очередь на Elder: root2194eeadcb3f29e1b2047ae1bcf3e6e7e48e4747,
Pulse21435c8d5a11d2670cdc1609757d3a9973877314; native209/readers87.
Supervisor515626/start_ticks325911553, publisher515627/325911554 проверены живыми.
Readbacks: s07-capacitance-history-boundary-normal-h9 и
s07-capacitance-history-boundary-publication-normal-h9. Сборка пока не началась.
Перед reuse source/build обязательны закрытие PID/start_ticks всех H8d owners,
его полная публикация и проверка всех compressed primary members. H8d должен
иметь ровно четыре failures NativeTrainingCapacitanceBridge Classic/Branch N0/N1
с точным описанным runtime_error; любое иное расхождение запрещает автоматический
переход. Его not_accepted остаётся неизменным. Новая ветка исправляет ожидание
fixture и добавляет portable schema3; новый PASS нельзя подменять прежним183/52.


### Актуализация legacy reader contract (код, runtime pending)

Отдельная ветка codex/timelearner-native-evidence-contract обновляет
NativeEvidenceTest: exhausted service остаётся diagnostic без certificate,
strict default gate обязан его отвергать, явно разрешённый diagnostic analysis
возвращает exact=None. Новые проверки запрещают превращать outcome в exact.
Certificate corruption/reordering/missing-trial проверки теперь берут реальные
completed packages со всеми первичными CSV, проверенные audit_learned_state.
Это сохраняет проверку пересчёта certificate, вместо выдуманного сертификата у
BudgetExhausted. Проверки обоих классов peak assignment сохранены. Серверная
проверка этой отдельной ветки ещё ожидается; H9 использует прежний immutable root.
