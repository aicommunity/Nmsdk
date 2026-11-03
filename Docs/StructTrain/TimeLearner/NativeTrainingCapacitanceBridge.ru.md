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
