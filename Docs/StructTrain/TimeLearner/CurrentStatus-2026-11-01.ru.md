# Состояние рефакторинга на 01.11.2026

Цель 0–12 активна. Полностью принят только этап 0; остальные этапы имеют
незакрытые требования. Полный остаток сохранён в
[сводке 31.10](CurrentStatus-2026-10-31.ru.md#остаток-полного-плана) и
[утверждённом плане](RefactoringPlan.ru.md). Эта запись добавляет проверенные
подэтапы, не заменяя исходную постановку или обязательную матрицу.

## Принято адресно: native owner PostTune

Код PulseLib ecdbd9944f46a45efafba7d1547b2fbd3e75d084; fixtures root
4820405e5a6cba98007b0e6816f5a243d307e05a. Обе топологии, N1/2000Hz,
CalculateMode0/1, local/connected и два внешних Reset. Новая фаза продвигается
в BeforeCalculate до штатного расчёта детей, без внешнего Advance или вложенного
Calculate. Существующие storage/import/Build/Init/Reset пути сохранены; внутренний
lifecycle отделён от внешнего прерывания. Административное завершение не означает
Calibrated, Exact или успешное распознавание.

| Проверка | Normal | ASan |
|---|---|---|
| Native integration gate | 75/75, 213.461 s | 75/75, 1445.556 s |
| Independent reader | 2/2, 110.079 s с повторным audit | 2/2, 88.008 s с повторным audit |
| Actual records / corrupt controls | 10 / 100 | 10 / 100 |
| Archive members / compressed bytes | 836 / 4095348 | 569 / 2408564 |

No skips; ASan leak checking выключен. Все outer/member hashes проверены,
каждый пакет включает два исходных portable runs / 84 artifacts. Неудачные и
отменённые попытки сохранены с отдельными причинами; EXIT-trap zero отменённого
supervisor не используется как свидетельство успешного native выполнения.

[Normal proof](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-normal-a1/README.md)
commit864e7f1dd142173e0181e478f1de4be3be5e09eb;
[ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-asan-a1/README.md)
commit eca0b84e2ff025b1d65f0672ef1b214502e3c139.

PulseLib принят через --no-ff в develop:
3e371dc90884025baa10a27976a8c1e7770897f3; remote reachability проверена.
Bin97dd1943a059e67888d56380c5409f3d3997d086 и
Rdk027f7f8353608f83b55f3857a2f6c39138df4c65 не изменялись.
Корневой develop merge539eafb287feb87e5a39f3ae8d9f6cc4f574a821 опубликован,
remote reachability проверена. Он записывает согласованные child gitlinks и
все принятые ниже scoped proofs. Следующая ветка: codex/timelearner-live-finalization.
Код работающих серверных checkout не обновляется.

## Временные графики

[Visual proof](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-visual-asan-a1/README.md):
10 отчётов, восемь completed и два interrupted; 48 полных trial-soma pairs.
2/2 автоматических checks, render+checks 213.731 s; 305 source files неизменны.
Все полные матрицы содержат каждый объявленный target/foil, все каналы сомы,
реальные входы и исходные отсчёты. Полный cache: 2324 files / 197348346 bytes,
M40 /media/user/Data/TimeLearnerRefactor/cache/s08-native-owned-posttune-asan-a2.
Git: 111 metadata members / 90036 compressed bytes и восемь PNG / 1139977 bytes.
Все metadata/PNG hashes и связь десяти source records с ASan primary проверены.

Восемь выбранных first-soma target/foil overview/first zoom просмотрены в
1920×960: наложение входов читается, подписи не обрезаны, легенды не перекрывают
кривые. Принята только читаемость выбранных изображений; полный cache вручную
не принят. Потенциал к концу части окон ещё не вернулся к rest-state. Данные
после окна, continuous stream и большая ITI этим не подтверждены. Это fixed
selection diagnostics, без научного PASS.
[Точная область просмотра](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-visual-asan-a1/SELECTED_VISUAL_REVIEW.ru.md).

## Production Console: адресная приёмка завершена

Root08ae95430014a6a6c8b92ebc040181372fd0f912, PulseLib8a71a855d3fa6ecf64ad6a64a69d1b37e918d449
(тот же native код, дополнительные документы). Console PostTune теперь использует
BeginNativePostTunePhase и обычные тики модели; standalone calibration сохраняет
прежний driver. Execution schema2 связывает четвёртый phase-execution.json с
подписанным execution, всеми model ticks, частотой и begin/end clock. Schema1
поддерживается отдельно, без выдуманного phase receipt.

Normal job: s08-native-owned-posttune-worker-normal-a1, supervisor PID2096495.
ASan job: s08-native-owned-posttune-worker-asan-a1, supervisor PID4103970.
Оба задания поставлены на 20 PostTune controls (18 старых режимов/метрик/лимитов
и два schema3 fixed/probe cases), шесть standalone calibration regressions,
4+3+12 checks production/CLI/negative controls. Новый reader также повторяет
два прежних owner evidence tests до дальнейшего анализа. На момент записи
normal уже выполнил 26 операций и проходит проверки; ASan ещё выполняет corpus.
Обновление normal: 26 операций, 4/4 PostTune checks, 3/3 owned-phase checks
и 8 ordinary calibration checks прошли; один setup provenance-класса skipped.
Исходный gate закономерно завершился status1, а не PASS. Причина — отсутствие
отдельного env и неправильный порядок зависимых классов при module discovery.
Новый maintained checker root e6eb2a76aa09c7498495893b8fa99014d278f916 выполняет
явные классы в порядке 4+3+8+4 и сохраняет typed результаты каждой группы.
Повторный normal reader PID2127180 и queued ASan reader PID4133904 проверяют
сохранённые corpus, создавая отдельные CLI acceptance probes. Главные 26 операций
повторно не запускаются. Начальный skip и неудачный gate сохраняются.
Это не объявлено принятой Console-реализацией до терминальных receipts,
публикации полной Git closure и проверки её hashes.

Обновление после corrected checker: оба workers завершили 26 основных операций
и 19/19 checks без skips. Normal 413.589 s; ASan 464.310 s. Runtime before/after
совпал на каждом. Main 18 PostTune: 9 Calibrated, 7 SearchUnresolved,
2 BudgetExhausted; два fixed cases — WeightsSelected с fresh final responses.
Шесть standalone calibration controls сохранили schema1 и ожидаемые исходы.
Первоначальный status1/setup skip оставлен в обоих пакетах, не переписан.

| Production proof | Members | Compressed bytes | Portable runs / artifact entries |
|---|---|---|---|
| [Normal](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-worker-normal-a1/README.md), eeeac0a53d450e5e00a201e9081d630f83444145 | 1452 | 7067640 | 28 / 1196 |
| [ASan](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-worker-asan-a1/README.md), 13dfee817c3fbd796dfb91e7e74e2e4614506fcd | 1515 | 7170828 | 28 / 1196 |

Все outer/member hashes проверены локально, exact Git closure опубликована;
пакеты объединены в feature через --no-ff. Extra CLI acceptance probes входят
в 28 portable runs и не считаются независимыми научными обучениями.

Завершён production temporal report gate:
s08-native-owned-posttune-worker-visual-asan-a1, PID4157957, renderer/test root
504d6fac3be225102079541dc94a5a8f37fa9381. План: все 20 PostTune и шесть standalone
calibration reports, 3+2 checks всех полных native samples, soma channels,
реальных inputs и масштаба. Cache — M40 Data; большие PNG/SVG/PDF не публикуются
в Git. Terminal status0: все 26 отчётов, 3+2 checks без skips, 1132.731 s.
Кэш: 10418 файлов / 1107367233 байта. Опубликован
[compact visual proof](../../../Reports/StructTrain/TimeLearner/s08-native-owned-posttune-worker-visual-asan-a1/README.md),
commit0507b652e9a752b3654bf4981588d34861de7570: 404 metadata members /
400608 compressed bytes и восемь PNG / 1139977 bytes. Все outer/member hashes
проверены локально. Восемь PNG побайтно совпали с ранее просмотренными при
1920×960 native owner PNG; соответствия и точная область перенесённой приёмки
читаемости записаны в SELECTED_VISUAL_REVIEW.json. Новый ручной просмотр и
полная ручная приёмка кэша не заявляются. Научный verdict отсутствует.

Новый schema1 compatibility reader на M40: 4/4, 120.024 s, 18 прежних portable
runs из подтверждённого архива normal-a2. Исторические primary не изменялись.
Эти повторы не являются новыми независимыми обучениями или доказательством
улучшения классификации.

## Переход через outer clock: проверенная предпосылка live handoff

Source root62d6bf77e47897401a5709924fd960b59f62303a / PulseLib3e371dc.
Normal 24/24 (28.916 s), ASan 24/24 (163.801 s), без skips; runtime before/after
совпал. Четыре новых случая Classic/Branch × CalculateMode0/1 переводят
Environment на один timestep без Calculate детей; conversion/import исходной
completed boundary проходит. Это восстановленная finished Solo-модель, ещё не
автоматический переход из живого Train.

Reader root76048fcf59890fcae31c73779bd5dff47a4e127c: по 3/3 на обоих workers,
четыре actual records, 32 повреждённых record controls и 16 re-signed projection
controls. Полная boundary после шага времени точно равна повторному экспорту
до шага. Первый и повторный экспорт различаются только ранее установленным
empty→zero InputFeedbackSignal cache; вся XML и её hashes сохраняются и
проверяются существующим узким правилом, новых исключений не введено.

[Normal proof](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-clock-handoff-normal-a2/README.md),
commitca8d2e7ea9aada9e3a5491ffaf8eec05401fd55d: 172 members / 934920 bytes;
[ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-clock-handoff-asan-a2/README.md),
commit13d8fce27dab0a3b098fdd97ed7aefd495c649f4: 176 members / 948704 bytes.
В каждом полные два исходных portable runs / 84 artifacts; все outer/member
hashes проверены локально. Начальный native a1 упал на смешении first/repeated
export, хотя import проходил; оба attempts сохранены. ASan reader a1 содержал
KeyError в отрицательном fixture, исправление и неудачный attempt сохранены.
Scientific verdict=null; полный этап 8 остаётся открыт.

## Место и данные

Оригинальный normal owner-proof получен через Git на M40 Data и проверен по
всем 836 members. На Elder удалены только его подтверждённые raw-копии:
440 files / 487636124 bytes из двух неудачных attempts и, после повторного reader,
224 files / 318706334 bytes из завершённого attempt. Все логические данные
доступны в опубликованном lossless archive; уникальные primary не удалены.

Дополнительно удалены 1262 ELF_REL .o файла трёх неиспользуемых owned build-кэшей,
275639032 bytes; 17 CMakeCache/executable файлов сохранили hashes. Для 510
идентичных immutable source snapshots завершённых runs применены hardlinks:
пути, bytes и signed run manifests неизменны, освобождены их отдельные копии
блоков (39370752 bytes). Receipt хранит каждый anchor и hash. Активные модели,
текущий runtime, пользовательские файлы и исторические уникальные логи сохранены.
Все cleanup receipts включаются в proof нового worker.

Дополнение после clock gate: automatic Git GC дважды остановился на полном
диске Elder, оставив временные tmp_pack. После проверки отсутствия открытых
handles удалены только эти два неиспользуемых временных файла (250044416 и
239501312 bytes); завершённые pack/index сохранены. Automatic gc отключён
только в owned source clone. Дополнительно удалены 20 распакованных JSON-дублей
завершённого Console corpus (556261102 bytes), каждый побайтно сверён с
опубликованным primary archive; все 1452 members архива заранее проверены из
Git на M40. Для повторного reader этого Elder corpus сначала восстановить
указанные archive members. Подписанные исходные manifests не изменены.
[Per-file receipts](../../../Reports/StructTrain/TimeLearner/s02-elder-verified-cache-cleanup-20261101/README.md),
commitbef73f6655838833d5f145a0be2fe38b58fb7472. После очистки df: 759 MiB.
Уникальные primary и пользовательские исторические данные сохранены.

## Следующий обязательный объём

Начата реализация [живого dispatcher](NativeLiveFinalization.ru.md):
PulseLib69eba48208629a2462243e21fc6046b4d132041d,
root6659caaf57744489e2cd2b615f7e17a3bfb9003d. Read-only capture выполняется
после естественного завершения Train, а conversion/import/owned PostTune —
перед детьми следующего tick. Исходный outcome и immutable request сохраняются;
остановка без сертификата не создаёт recognition-модель. Runtime declaration
пока задаётся API, а не production job/ControllerConfiguration. Target-reference,
C-trim и legacy nonseparable fallback остаются явно запрещёнными в новом пути.

Первая normal/ASan пара (root6659caaf5 / PulseLib69eba48): native6/6,
116.425 / 663.040 s; по два cold fixed handoff и четыре clock controls.
Readers по2/2 без skips: 32.255 / 25.665 s. На обоих initial supervisor status1
сохранён: широкий glob включил вспомогательные Train JSON. Успешный native
XML/process receipt проверен отдельно; supervisor не переименован в PASS.

Normal addressed source root5afe5b963 / PulseLibcf530be: 31/31 (345.452 s),
16 live controls, четыре clock и11 lifecycle, terminal0. Два stopped-primary
follow-ups rootf0cf989cb на том же PulseLibcf530be прошли2/2 (1.834 s): добавлены
native summary и partial CSV/state для независимой проверки остановки.
Composed view выбирает только эти два новых stopped records, остальные14
live records оставляет из первоначального31-case gate. Каждый файл связан
с точным producer/SHA; исходные stopped records также сохранены.

Полный normal reader rootf31d6a3de:4/4 без skips,106.192 s с построением
composed view и проверкой двух native gates. Проверены четыре completed
и12 rejected controls,32 corrupt completed и60 corrupt rejection controls.
Отдельный maintained native_execution_gate проверен на реальных первых
receipts: по2/2 на workers, десять corrupt controls, включая auxiliary JSON,
подмену executable/runtime, PID identity, лишний argument и failed supervisor.
Его начальные Path setup и неверное ожидание числового start_ticks сохранены;
production runner правильно хранит /proc identity десятичной строкой.

[Normal compact proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-normal-a1/README.md),
commita7ef72e14f8a43fff916a460d126cc6bf25db03b:599 members /351871673 raw bytes
→1943492 compressed bytes. Все outer/member hashes локально проверены после
--no-ff merge; два original profile/design portable runs /84 artifacts включены
отдельно от свежих Train primary. Это не31 тест нового follow-up executable:
разные source snapshots указаны явно. В develop новый dispatcher ещё не принят.

Четыре completed controls сохранили Train SearchUnresolved. Fixed: оба
WeightsSelected; grid policy: оба SearchUnresolved с восстановленной исходной
recognition-моделью. Во всех четырёх frozen replay target0 spikes /foil0 spikes.
Это молчание с FN, не успешная классификация и не доказательство улучшения
разделимости. Матрица содержит два паттерна и не сравнима с августовским8-case
протоколом как одинаковый научный опыт. Temporal report acceptance ещё открыта.

ASan full regression PID20741 действительно жив: rootf0cf989cb /
PulseLibcf530be, ожидаются95 cases (75 прежних +4clock +16live), runtime не
обновляется. Последняя проверка: завершены managed/owned controls и два новых
cold fixed handoff; выполняется ClassicConnectedCalibrate. Queued reader
PID54868 ждёт именно этот terminal receipt, после чего проверит95-case coverage,
process/runtime binding и4 payload tests (всего6 checks). No terminal receipt,
broad ASan acceptance и compact publication пока нет.

Временные отчёты нового handoff: первый normal cache (renderer3d679ec7f)
содержит16 reports,213 training и42 recognition trial-soma pairs;3/3 checks,
516.173 s,931 неизменённых source files. Он не принят по хронологии: отдельная
review фактически обнаружила trial_10 перед trial_2 в10 training reports.
Исправление rootd16237f83 сортирует по непрерывным числовым writer ordinals,
проверяет возрастающий begin и отсутствие пропущенной промежуточной пробы.
Visual-a2 PID53240 строится на тех же primary, без нового обучения; selected
visual QA, compact metadata и публикация ещё ожидаются. Полные cache остаются
на M40 Data. Старый status0 и отдельный chronology-review сохранены.

CLI analyze/report --format native-live-finalization с обязательным
--primary-inventory добавлен для этих native integration-control artifacts.
На source10032be3c прошли2/2 checks (0.889 s), включая реальные no-data report,
analysis и отказ missing inventory/model overlay до output. Source hashes
не изменились; numerical runs0. Production Train-job declaration остаётся открыта.

## Следующий обязательный объём

Scoped Console acceptance и Git publication завершены. Programmatic live
handoff реализован и адресно проверен на normal; требуются broad ASan/visual
acceptance, production job/CLI declaration, target-reference/parallel-peak фазы
и независимый frozen Test. Same-matrix replay не заменяет independent evaluation. Остаются полная physics/mode/frequency/dimension
матрица, UnInit/Cancel/multirate negative controls, N0/N1/C-trim алгоритмические
проверки, миграция всех tools, scheduler/recovery/publisher integration,
исторический replay/cold retrain, permutations/ITI и полная документация.
Серия D не возобновляется. Августовские визуальные 4/8–6/8 сохраняют исходную
доказательность. Научные 8/8 не являются условием завершения рефакторинга.

## Обновление: chronological visual proof и явная отмена

Исправленный renderer d16237f838eec366df86d05455b3d266386a0e88 завершён:
16 reports,3/3 checks без skips,518.175 s,931 source files неизменны.
213 training и42 recognition trial-soma pairs; полный cache6928 files /
447227287 bytes остаётся на M40 Data. Compact proof58c5b3985d3d156f71b4eac4256e4acbcaa2e338
содержит440 metadata members /277096 compressed bytes и8 PNG /1194620 bytes.
Все outer/member hashes проверены после Git merge. Восемь выбранных
first-soma target/foil overview/first zoom Classic/Branch непосредственно
просмотрены в1920×960: подписи, входные импульсы и кривые читаются. Полный
cache вручную не принят; SI units и settling за концом окна не подтверждены.
Первый chronology-broken attempt сохранён отдельно.
[Proof и точная область QA](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-visual-normal-a2/README.md).

В PulseLib4d2d278 добавлена отмена live finalization между тиками: native
ExternalStop закрывает частичную Train-пробу; queued cancel не импортирует
модель; PostTune использует штатный transactional rollback. Внешний connected
request не записывается. Cancelled armed declaration не начинает Train снова
при оставшемся true provider. Root e7543c5eb8f1224138ec591d504b59a64d204777
добавил8 реальных controls обеих топологий. На Elder job
s08-native-live-finalization-cancel-normal-a1 / PID2233662 выполняет сборку
на неизменяемом снимке; runtime acceptance ещё нет. Independent payload reader
дополнен для actual cancellation records и48 malformed controls; его проверка
ожидает producer. Production Train schema2 ещё не реализована.

Обновление cancellation gate: Elder producer PID2233662 завершён status0,
8/8 native checks без skips,62.289 s; runtime before/after совпал. Native
source root e7543c5eb8f1224138ec591d504b59a64d204777 /
PulseLib4d2d278ee047b4860d07f8dbf9f7d629f670ac0e. Reader PID2237620
на root604b468200d461bd7b064d0f18536454b33026c4 уже прошёл2 receipt checks,
проверку восьми actual cancelled records и48 malformed controls; выполняет
прежние4 payload regressions. До terminal receipt полная приёмка reader
и публикация cancellation primary не заявляются.

Сохраняемый codec финализации добавлен в PulseLib019e5d1 (runtime пока не
проверен), root cbe7d7a69ffbe2ed5a3c02a9cc6b82c3e58f9996 добавил fixture
четырёх persisted designs и32 malformed controls. Queued M40 job
s08-native-live-finalization-cancel-codec-asan-a1 / PID69156 закреплён на
root dcc64fff651e29569e03312f1f8acad0179d9c00. Он ждёт успешного завершения
старого95-case producer PID20741 и reader PID54868 перед изменением owned
source/build/runtime, затем выполнит9 checks (8 cancellation +1 codec).
Оба старых процесса повторно подтверждены живыми; они не перезапускаются.
Production Console Train schema2 и Python worker integration остаются открытыми.

Cancellation reader завершён status0:8/8 checks без skips,112.695 s,
136 producer files неизменны. Опубликован proof1af3cc9e155d1ce94c18afd08f7cd0900176b26a:
252 members /117794880 raw bytes →752596 compressed bytes. Все member и
outer hashes локально проверены после --no-ff merge. Оригинальные два
profile/design portable runs /84 artifacts включены; старые regression primary
связаны с прежним опубликованным normal proof без дублирования.
[Cancellation proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-cancel-normal-a1/README.md).

Реализуется production Console Train schema2 + Python worker: explicit plan,
source capture до импорта, nullable no-boundary diagnostic, раздельный
recognition export и typed nonzero exits. Добавлен production14-operation
corpus с отдельным frozen evaluate; runtime-проверка этой новой реализации
ещё не выполнена. Нельзя считать новый путь принятым по прежним8 native tests.

## Завершение broad ASan live gate и запуск production schema2

M40 producer PID20741 завершён status0:95/95 native checks,3822.630 s,
без failures/errors/skips. Reader PID54868 завершён status0:6/6 checks,
91.408 s,548 source files неизменны; runtime before/after совпал.
Scope:75 прежних native controls +4 clock +16 live; payload reader
независимо проверяет16 live controls, не все75 старых сценариев.
Опубликован ASan proof531116d70b1d7b14fb1b8cfcf333c08a63e1d82d:
792 members /667719504 raw bytes →3343244 compressed bytes. Все member
и outer hashes локально проверены после --no-ff merge. Original profile/design
closure2 portable runs /84 artifacts включена; первые supervisor/reader
ошибки сохранены. Этот binary предшествует Cancel API, codec и production
schema2; Leak detection выключен, полного этапа8 приёмка не заявляется.
[ASan proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-asan-a2/README.md).

Production source3f9661a01703d107b02f306c006e1f56be07ddf2 собран на Elder.
Первый s09-native-live-training-worker-normal-a1 / PID2249379 завершён1:
standalone codec fixture не создал свой output directory и Write отказал.
Новый Train corpus не начинался. Исходные XML/process/status сохранены;
исправление9d8da9af3079a91f512d13f4dd005b96063dc3c8 добавляет native mkpath
в fixture. Новый normal-a2 / PID2253367 использует этот неизменяемый снимок;
ожидаются1 codec check и14 production operations, затем3 reader checks.
Нельзя считать production путь принятым по успешной компиляции.

Для места Elder удалены10 подтверждённых распакованных дубликатов крупных
старых live JSON. Каждый SHA сверён с published normal proofa7ef72e14 и
599-member mirror на M40, который заново проверен целиком. Удалённые пути
проверены на принадлежность точным старым native/corpus каталогам и отсутствие
fuser handles; новый runtime и baseline profile/design fixtures не затронуты.
Logical duplicate bytes258266323; свободное место203325440→353660928 bytes.
Per-file receipt хранится в normal-a1/confirmed-duplicate-cleanup.json и должен
войти в production proof. Для повторного старого reader-normal-a3 сначала
восстановить удалённые archive members и composed view. Уникальные primary
не удалялись; текущая production серия использует другой baseline-source.

## Принята normal production schema2, ASan/visual выполняются

Normal-a2 / PID2253367 завершён status0 на root9d8da9af3079a91f512d13f4dd005b96063dc3c8,
PulseLib019e5d17aa1d2dcc551dc71a32a85c383953c71a:1 codec test (4 plans/32
malformed declarations),14 production operations и3/3 reader checks.
337.735 s для codec/corpus/checks, из них58.514 s для3 reader tests.
Это4 genuine cold Train→native finalization,4 отдельных frozen same-matrix
evaluate,4 partial schema2 и2 partial schema1 controls. Runtime и codec-runtime
before/after совпали. При post-Train замене графа source Solo и summary не
теряются. Typed partial schema2 nonzero сохраняет process_error, но его
структурированные данные проверяются; schema1 semantics сохранена.

Complete reader root07e172610eb480c90f1d70d27c6e7eb2c5f918a8 / PID2266608
прошёл4/4 без skips,61.222 s,490 source files неизменны. Четвёртая проверка
добавляет bundle closure всех14 runs и5 malformed packaged controls;
предыдущие проверки включают16 re-signed native и24 malformed plan controls.
Это4 проверки с перекрытием прежних3, не7 независимых tests.

Опубликован [normal production proof](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-normal-a2/README.md),
commit84e798616736a36140c293c3d0ad7851a4fe3412. Closure14 portable runs /
446 artifact entries; каждый outer/member hash проверен локально после merge.
Сохранены исходный codec-directory failure и initial publication rejection:
общий verifier ранее не знал pipeline manifests. Теперь cold Train требует
source=null, export/evaluate — включённый source artifact, полная byte/hash
closure сохраняется. Numeric runs при corrected reader/publisher не повторялись.

ASan Cancel/codec и reader также завершены:9/9 native (382.178s),8/8 reader
(91.297s),137 unchanged source files;4 actual codec plans проверены повторно.
[Proof](../../../Reports/StructTrain/TimeLearner/s08-native-live-finalization-cancel-codec-asan-a1/README.md)
commit9e9be85de7706631c873331402d63f510090ec21:253 members /117892004 raw
bytes →765044 compressed bytes. Все hashes проверены локально. Core019e5d1,
rootdcc64fff6; этот binary ещё не содержит production Train schema2.

На M40 production ASan PID89567 закреплён на root7ea85a5035dcfd66d5f677cacdb41127af30f47c
и том же Core019e5d1. Ожидаются1 codec +14 operations +3 original checks.
Queued complete reader PID100877 на root9554c0e465b5ce72a989c3d34edfd63dc0e5df2b
ждёт именно его status0 и повторит4 complete checks, без нового обучения.
Numeric source/build/runtime работающего задания не обновляются.

M40 normal production visual PID97885 использует renderer root9554c0e46
в отдельном metadata worktree. Он получил proof84e79861 через Git, проверяет
полную archive closure и строит14 reports реальным CLI --format pipeline-run.
Затем3 report checks должны сверить каждый Train sample/soma, все completed
pattern responses и readable zoom. Нового численного обучения нет; cache —
Data, selected QA и compact visual publication ещё ожидаются.

Все4 normal full Train остаются SearchUnresolved. Fixed — WeightsSelected,
grid — SearchUnresolved/source restored. Все4 отдельных frozen target/foil
Test дают TP0/FP0/FN1/TN1. Это достоверный отрицательный результат, не успешная
классификация и не8-case August reproduction. Весь исходный план0–12 открыт.

Обновлены native runtime/worker документы корня и PulseLib; PulseLib
d06859c24238663401f6583e31265eb9080281e7 — docs-only, Core tree в точности
8e3a027a9d30d104886284b6825eed8cd6c413f1 как у фактически собранного019e5d1.
Bin прежний accepted docs/ClDesc snapshot97dd1943 через --no-ff включён в
develop11ce4cec, затем отдельная docs branch50f94f67 описала новый CLI и
историческую область старых каталогов; --no-ff merge develop03e8aec4517e69a38e72918b9fcf40bdd7fb0882
опубликован. От runtime Bin97dd1943 отличается только LAYOUT.md; конфиги и
ClDesc новой docs-веткой не менялись. Новый PulseLib/root feature ещё не
объединяется в develop до завершения текущей scoped ASan/visual приёмки.

## Production ASan завершён; normal visual принят адресно

ASan producer PID89567 завершён status0:1 codec,14 operations и3/3 original
reader checks без skips,1130.925 s (3 checks48.147 s). Runtime и codec-runtime
before/after совпали. Complete reader PID100877 завершён0:4/4,50.040 s,
490 source files неизменны, новых numeric runs0.
[ASan proof](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-asan-a1/README.md)
commit264c429974e9d97bb5d5277b1fc25c846fa80eda:521 members /206717468 raw
bytes →1225484 compressed bytes,14 portable runs /446 artifact entries.
Все outer/member hashes локально проверены после --no-ff merge. Источники
root7ea85a503/Core019e5d1, reader9554c0e46; leak detection выключен.
Все четыре frozen пары на ASan также TP0/FP0/FN1/TN1, совпадают model revisions
b4102b582e31 Classic и797ed41bf05d Branch. Это не независимые научные повторы.

Normal visual PID97885 завершён0:14 reports через production CLI,3/3 checks
без skips,393.604 s (checks41.056 s),543 неизменённых source files.
93 training и42 recognition trial-soma pairs; все declared complete patterns
и soma channels, partial schema1/schema2 явно цензурированы. Cache4119 files /
291766358bytes на M40 Data. Compact [visual proof](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-visual-normal-a1/README.md)
commite6f5cd9669f05cf38be4674340bfad974f6495ca:272 metadata members /190348
compressed bytes и10 PNG /1500834bytes; все hashes проверены.

Все10 selected PNG непосредственно просмотрены1920×960: first-soma target/
foil overview/first zoom Classic/Branch и2 one-tick partial Train overview.
Легенды/подписи читаются, реальные inputs наложены, partial panels показывают
единственную точку и censored region с valid=false/complete=false. Padded
ordinate1e-12 в one-sample view является масштабом отображения, не точностью
измерения. Нет утверждений о settling/ответе после конца окна или full-cache
ручной приёмке. QA commit92de61b01a25901781e2b3d0f0693e7017066d26.

ASan visual PID114561 выполняет собственные14 reports и3 checks на source
proof264c42997, renderer9554c0e46. Численные фазы не повторяются. Publication
и selected QA этого отдельного ASan cache ещё не завершены.

Документы PulseLib a3235b77734f089a271619b44d4155bac48edd0c и Bin develop
49adcd0208d0c8ab8d70e7cca47ae6e34b05145e направляют текущие acceptance scopes
в единую корневую спецификацию. Core tree не изменился с019e5d1; Bin configs/
ClDesc не менялись относительно фактически использованного97dd1943.
Новая root/PulseLib feature ещё не принята в develop; полный план0–12 открыт.

## Завершена scoped ASan temporal приёмка

M40 visual PID114561 завершён0:14 reports,3/3 checks без skips,362.263 s
(checks36.898 s),521 source files неизменны;14 run closures /446 artifacts
проверены при распаковке Git proof264c42997.93 training и42 recognition
trial-soma pairs, новых numeric runs0. Cache4119 files /291766822bytes
остаётся на Data. Опубликован [compact ASan visual proof](../../../Reports/StructTrain/TimeLearner/s09-native-live-training-worker-visual-asan-a1/README.md),
commit54b33d7029df3b5c00a5a0b4c8b8d70c54a4158d:272 metadata members /190708bytes.
Все outer/member hashes локально проверены.

Все10 independently rendered selected ASan PNG побайтно совпали с normal
PNG, прямо просмотренными в QA commit92de61b01. В Git сохранены10 точных
ссылок/hashes, новых PNG bytes0. Перенесена только selected legibility scope;
новый direct manual review и full-cache acceptance не заявляются.
Все заявленные normal/ASan14 production операции и temporal checks теперь
имеют terminal0, доступные Git primary/metadata и адресные QA receipts.

PulseLib feature включена --no-ff в developf23d1b8dee908ddfdc549619b754875fc627ce9b
и опубликована. Core tree8e3a027a9d30d104886284b6825eed8cd6c413f1 в точности
соответствует фактически проверенному019e5d1. Bin develop49adcd02 опубликован
ранее; изменился только LAYOUT.md относительно runtime Bin97dd1943.
Root merge выполняется после записи этих точных child gitlinks.

Это приёмка scoped native live/cancel/codec + production schema2 baseline
Classic/Branch,N1,2inputs,2000Hz,fixed/grid,CalculateMode0/1. Это не закрытие
полных этапов6–9 и не full original matrix. C-trim, target-reference/parallel-peak,
N0/N1 полная алгоритмическая/physics matrix, historical replay, independent
Test, полная scripts migration, scheduler/publisher и оставшаяся документация
по-прежнему обязательны. Все4 full models дают SearchUnresolved и silent
target; научный PASS не установлен. СерияD не возобновлялась.

Scoped live pipeline root включён --no-ff в develop
1d4822af22e05b741e4a1c779cf99ba05cb0a1fa и опубликован; ls-remote проверен.
Gitlinks PulseLibf23d1b8d/Bin49adcd02/Rdk027f7f83 совпадают с опубликованными
child develop heads. Новый algorithm substage — codex/timelearner-n0-candidate-order.
[N0 hypothesis и gates](N0CandidateOrdering.ru.md): сначала воспроизведение
ограничения перебора на unchanged production kernel, затем измеряемое изменение
порядка кандидатов. Full-stage7 и физическая N0 матрица пока не приняты.

## N0: воспроизведение ограничения бюджета и проверяемое исправление

M40 baseline supervisor135125 завершён0; native tests2/2 ожидаемо упали,
process return1. На unchanged Coref23d1b8d / root31934548524ab0da77311f4fc046db05cdf69b81
Classic и Branch оставили L2/Ns1 и SearchUnresolved: ближайшее L2/Ns2 не
измерено. Это controlled production-kernel oracle, не физический эксперимент.
Proof72d9df51a9684f1bdd485c7998ae065eb6defaa4 опубликован и включён --no-ff;
21 archive member и outer hashes проверены локально,10724 compressed bytes.

Corec25db29 предлагает соседние Ns после полного измеренного улучшения
rank у timing-ready/amplitude-invalid кандидата; full geometry legality,
fixed anchor, fresh anchor/input, repeats и final gate сохранены. Дубликаты
кандидатов не расходуют бюджет повторно. Дополнительные regression cases
проверяют length-only поиск, хуже работающий сосед/возврат к длинам, repeats.
Docs-only Pulsee4978a2 имеет тот же Core tree64cdc352af865dc0e860ea05fb2c6d9799ccc36e.

Исправленный root942e5df4559467a9a19c56755f945ce6501e7780 собирается/проверяется
на M40 в readbacks/s07-n0-candidate-order-fixed-asan-a1, supervisor137298.
На последней проверке процесс жив; production Core собран, интеграционные
тесты ещё компилируются. Runtime/source активного задания не менялись.
Новая feature не принята в develop; full stage7 и физическая матрица открыты.

## N0: две серверные проверки и объявленная visual coverage

M40 fixed-asan-a1 supervisor137298 после сборки прошёл новые5/5 kernel cases
и реальные NativeModelEditor ClassicN0_2000/BranchN0_2000. Далее выполняется
20000Hz. Общий wall limit300s оказался мал для расширенного ASan набора;
результат ещё не терминальный на последней проверке. Очередь fixed-asan-a2
PID148245 ждёт именно terminal timeout/wall_budget_exhausted и исчезновения
принадлежащего процессу PID/start_ticks; только после этого повторяет тот же
бинарник и неизменный source/runtime с лимитом3600s, без rebuild. Первый запуск
и его реальные process receipts сохраняются, незавершённая серия не считается PASS.

Normal Elder fixed-normal-a1 supervisor2304393 собирает тот же root942e5df45.
Перед сборкой удалены только4 JSON-дубликата86901712 bytes: все543 members
опубликованного proof84e79861 заново сверены с M40 extracted Git mirror;
локальные SHA и отсутствие открывшего их процесса проверены перед unlink.
Свободное место116051968→202956800 bytes. Receipt включён в normal readback;
прошлый normal-a2 unpacked corpus теперь требует восстановления этих4 JSON
из Git/M40 перед повторным использованием. Уникальные файлы не удалялись.

Spec n0-candidate-order-native-v1.json объявляет точные31 test IDs и4 native
training phases (warm/cold Classic/Branch). Report scope не включает waveform
старых editor-only probes; они сохраняются в полном raw test archive. Visual
worker M40 PID148416 ждёт успешного fixed-asan-a2; затем production renderer
строит все объявленные training trial/soma views в Data cache. Первая visual
setup попытка завершилась до запуска из-за short-SHA fetch; повтор использует
полный445469038650354e98c740dbe52e433eb76c6fec. Ни visual, ни scoped algorithm
приёмка пока не объявлены завершёнными; develop не изменён.


ASan fixed-a1 теперь terminal1: production runner execution=timeout,
wall_budget_exhausted, returncode=-15,300.599977652s. До остановки25 cases
отмечены OK в stdout, включая5 новых и2 editor2000Hz; complete XML отсутствует.
[Proof](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-timeout-asan-a1/README.md)
d0bf145a80c8c03708374cbd5b012e7dfa1d2cbe сохранён в Git;40 archive members и
outer hashes проверены локально,46552 compressed bytes. Это частичная попытка,
не полный PASS. Fixed-a2 PID148245 действительно начал повтор того же binary
с3600s после terminal timeout; visual PID148416 ждёт именно его успешный итог.
Elder normal PID2304393 ещё компилирует integration target; runtime не обновляется.


Независимый N0 reader roota86f96ee5d015b304c63e7070b733477ed69891b требует
точного набора31 успешных JUnit cases и всех4 declared phases. Включает4 tests
на actual JSON/CSV/certificates и повреждённые копии данных. Metadata workers
Elder2312312 / M40154042 подтверждены живыми при запуске; ждут именно своих
producer terminal0. Новых numeric jobs они не создают. Численные Elder2304393
и M40148245 на последних отдельных /proc проверках живы; выполняются editor
probes20000Hz. Full31/31 и reader4/4 ещё не объявлены. Runtime не меняется.


Normal-a1 завершён terminal1: execution=timeout/wall_budget_exhausted,
returncode=-15,300.304135126s,26 completed stdout cases, complete JUnit нет.
[Proof941969016c577aef6fa4dc4deca1e1d3ab3b27c8](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-timeout-normal-a1/README.md)
включает61 member/225672compressed bytes, abort dependent reader и duplicate
cleanup receipt. Outer и все member hashes локально проверены. Первое staging
публикации упёрлось в диск. Удалены133 неиспользуемых ELF ET_REL object caches
80090112bytes только из завершённого owned build; проверены отсутствие
компилятора/линкера и fuser. Receipt сохранён; runtime/executable не менялись.
Диск5.6MB→85.9MB. Последующие сборки потребуют регенерации этих cache files.

Normal-a2 PID2315548 запущен только после подтверждённого timeout и завершения
owned PID/start_ticks, тот же binary/source/runtime,3600s без rebuild.
На последней /proc проверке жив04:02: Classic/Branch2000 и Classic20000 прошли,
выполняется Branch20000. Reader-normal-a1 остановился на неуспешном producer;
новый reader-normal-a2 PID2316199 ждёт normal-a2. ASan-a2 PID148245 жив15:16,
выполняет Classic20000; reader154042 и visual148416 ждут прежние точные jobs.
Ни31/31, ни reader4/4 пока не объявлены.

Новая [сводка всех этапов01.11](PlanCompletionAudit-2026-11-01.ru.md) заменяет
старые текущие формулировки при сохранении исторических аудитов. Она учитывает
реализованные controller/archive/live pipeline и отдельно полный остаток.
План0–12 и активная цель сохраняются полностью; develop не обновлён.


Normal fixed-a2 terminal0:31/31 native cases,375.292s по gtest. Reader-a2
terminal1 до tests из-за overlap glob с service_model.json. Исправление71878cb54
требует этот model file отдельно, canonical model hash и совпадение actual
revision; numbered trial completeness не ослаблена. Reader-normal-a3 PID2322439
terminal0:4/4,56 probes,188 unchanged files,0.221566s. Численное обучение не
повторялось ради исправления reader. Первые reader/publisher отказы сохранены.

Full [normal proof](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-normal-a2/README.md)
c9c65de9b12989b0ddcb51da5924f1854a56f88e опубликован, включён --no-ff и локально
сверен:205 members/8623983raw→346080compressed bytes. Model outcomes4×
SearchUnresolved и negative certificates; распознавание этим native fixture
не оценивается. Все5 controlled proposal cases,4 native editors2000/20000Hz
и4 native warm/cold training controls прошли; полного stage7 это не закрывает.

ASan corrected reader PID164462 на71878cb54 ждёт producer148245; прежний
reader154042 сохраняется как первоначальная постановка, его ожидаемый setup
failure не подменяется. Normal visual PID165784 получает исключительно Git
proofc9c65de9b и строит4 declared training phases/56trials в M40 Data cache;
численных прогонов не создаёт. Полные ASan и visual результаты ещё pending.


Normal temporal worker165784 terminal0:4 phases,56trials,84soma pairs,
render123.315699s,205 source files неизменны. Отдельный visual reader169106
terminal0:3/3 N0 и3/3 old338-probe/507-pair regression checks,77.037563s;
117 N0 selected phase files неизменны. Общий visual test сохранил старые
явные counts/partial semantics; новый class задаёт56/84/complete=true.

[Visual proof077334d7fb76bc6d05983a892570f5178ce9b21d](../../../Reports/StructTrain/TimeLearner/s07-n0-candidate-order-visual-normal-a1/README.md)
включён --no-ff. Проверены outer hashes,141 metadata members/95916compressed
bytes и8 PNG/1233786bytes. Полный cache2063files/103004513bytes остаётся Data.
Все8 selected PNG непосредственно просмотрены1920×960: final input0/first soma
warm/cold Classic/Branch overview и peak zoom. QA commitfd90e862d4f817cc2269ad9c46ba9c8c52aeb5a8
фиксирует exact hashes, читаемые labels/legends/inputs/rise/peak. Полная ручная
приёмка cache, SI units и ответы за пределами окна не заявлены.

ASan real numeric process150150 подтверждён /proc живым26:43,104%CPU/RSS~1GB.
ClassicN0_20000 прошёл1274.927s; далее BranchN0_20000. Runtime/source не менялись.
Full31 и reader4 на M40 ещё pending. Publisher173580 ждёт именно producer
terminal0 и corrected reader164462 terminal0, затем сохранит actual ASan primary
и первоначальный failed reader. Новый numeric run не создаётся. Весь план и
full stage7 открыты; develop пока не обновлён.


Независимый source-review подэтап stage1 выполнен в отдельном worktree
E:/Science-Repo/nmsdk-parameter-contracts и ветке codex/timelearner-parameter-contracts.
[ParameterControlContracts](ParameterControlContracts.ru.md) + machine ledger
содержат10 записей: ControllerVersion, ControllerConfiguration,
ConfiguredModelInitialized, CalculateMode, IsNeedToTrain для Classic/Branch.
Проверены47 refs/7 unique blobs полных pinned commits;4 текущих learner class
blobs совпадают с reviewed f23d1b8d. Runtime tests для ledger0: существующие
configured/live controls дают только частичное покрытие, не full acceptance.
Исторический source_inventory.json не переписан и не помечен целиком PASS.

CTRL-OWN-001 записан как source-contract risk с непроверенной production
достижимостью, не воспроизведённый дефект. SetPointer ignores local writes;
protected ExternalDataSource would forward them, но ненулевое присваивание
в production дереве не найдено, только derived inspection-test exposer.
Общий Rdk forwarding contract не менялся; unsafe-cast воспроизведение не вводилось.

Root-only docs feature0e74bfa6c44b06aec48356f1c1f88db6b867889b объединена --no-ff
в developc910ba84cada0a37b195f48ebe603215b75dd963 и опубликована, ls-remote проверен.
Child gitlinks f23d1b8d/49adcd02/027f7f83 неизменны. Это docs-only delta к
принятому live baseline1d4822af2, не новая численная сборка или закрытие stage1.
Develop затем включён --no-ff в N0 feature, без изменения её functional Core.
ASan native process150150 подтверждён живым39:33; идёт Branch20000Hz. Полные
31/reader4/visual ASan и scoped N0 develop merge ещё ожидаются.


## Принят scoped N0 candidate-order подэтап

ASan producer148245 terminal0:31/31 native cases,2764.079s; corrected reader
164462 terminal0:4/4,56 probes/188 unchanged files,0.159291s. Proof
fb1f578b94395fbb786e7e6658b9e0f704f341ac:201 members/8658691raw→348832bytes,
outer/member hashes проверены локально. Leak detection выключен.

Configured repeat follow-ups normal2340047 / ASan186704 terminal0:каждый3/3
native +3/3 actual-data checks,48probes/10groups/108 unchanged native files,
39.513974s и253.101449s. Runtime before/after совпал, rebuild0. Proofs
a0ff3273501466677d34423d3c2a5d52d36766d3 /6e596751df9be629b6480d249756f72dd9874a5a:
по125 members,104708/108188compressed bytes; hashes проверены. Два exported
model graphs каждого proof имеют пересчитанные hashes actual certificate model.

Base ASan temporal148416 и visual reader197579 terminal0:56trials/84pairs,
124.066112s render,3/3 checks0.454444s,117 phase files unchanged. Proof
32cca42c0275ce92bee3a93f37970448f0bf9526:142members/96408bytes;8 exact PNG
references к directly reviewed normal fd90e862, без новых image bytes.

Repeat temporal normal192131 / ASan199542 terminal0:48trials/72pairs и3/3
checks каждый,101.825486/99.217732s,125 primary files unchanged каждый.
Normal proof78a12250c220c1e480559ab450ee07f0220298a0:119members/81904bytes и
4PNG/618333bytes. Все4 прямо просмотрены1920×960; QA252ca56bf3a492130d9193efd8edb3c57875a38f.
ASan proof4d024c5f822cc6265bbfc0ac017f90890f0addfb:112members/81664bytes,
4 exact reviewed-image refs, новыхPNG0. Все outer/member/ref hashes проверены.
Full caches остаются M40 Data:normal1763files/88636254bytes,ASan1763/88636239.
Manual scope только selected first-soma/final-input0 views; full-cache manual
acceptance, SI interpretation и независимые научные повторы не заявляются.

Native fixture outcomes — SearchUnresolved и fresh negative certificates.
Контролируемый response oracle подтверждает proposal policy, реальные native
controls — регрессии. Warm/prebuilt означает построенный объявленный fixture,
не continuation ранее обученного состояния. Августовский replay не выполнялся.

PulseLib feature включена --no-ff в develop38edfcad7983478a7e2ca736c32ae2703861c1fd,
push и ls-remote проверены. Core64cdc352af865dc0e860ea05fb2c6d9799ccc36e точно
равен фактически проверенному c25db29. Bin49adcd02 и Rdk027f7f83 не менялись.
Root feature фиксирует exact child link; root --no-ff merge следует после этой
записи. Подэтап закрыт в указанной области, полный stage7/план0–12 открыт.


Root N0 functional acceptance merge8394a028a65afaacbe72f1ce741f26b309c4e3b7
опубликован в develop, ls-remote проверен. Closure PulseLib38edfcad/Bin49adcd02/
Rdk027f7f83 точно совпадает с child remote commits. Предыдущий root-only
parameter-control review c910ba84 включён. Все owned numeric/repeat/visual
задания этого подэтапа терминальны; runtime в ходе исполнения не менялся.

Следующая ветка codex/timelearner-n0-production создана от этого develop.
Приёмка выше относится к Test_PulseLib_StorageComponents, а не к заново
собранному Console. Перед production N0 pipeline требуется отдельно собрать
NeuroModelerConsole с текущим Core в новом runtime и проверить его manifest.
Старый Console из runtime прошлой live-N1 серии этим подэтапом не выдаётся за
новую N0 сборку. Elder compiler object cache частично удалён только как
воспроизводимый cache; следующие сборки должны учитывать свободный диск.

Полные этапы1–12 не объявлены выполненными. Следующая работа расширяет
production coverage и выявляет оставшиеся algorithm/mode/profile дефекты;
она не возобновляет старую сериюD и не меняет CapturedPerInput или августовскую
доказательность4/8–6/8. Получение8/8 не является условием инженерной приёмки.
# Продолжение: production N0 после принятого kernel-подэтапа

Ветка `codex/timelearner-n0-production` продолжает план после root develop
8394a028a65afaacbe72f1ce741f26b309c4e3b7. Добавлены явные N0-протоколы
с1/2 измерениями кандидата, сохранением fixed anchor и индивидуальных Rs;
производственные корпуса используют штатные CLI/Console/worker, по14 операций.
Код запуска021692a3fa0de4577e0770fd0af867a582a0ef03; усиленные проверки
фактически измеренного Ns>1 опубликованы1d2d3b0cd5abd783ebb96a0e746903257b1c708c.

M40: отдельный Console runtime собран из PulseLib develop38edfcad7983478a7e2ca736c32ae2703861c1fd;
build proof23edc5481229bb8f6deddda3cacc1c9ad04e9366 включён в feature через merge.
Двадцать Python job preflight checks прошли. Производственный supervisor228908
запущен, первая Classic-fixed Train/evaluate пара завершилась. Реальные
кандидаты Ns1/2 измерены при Rs86000000; результат обучения SearchUnresolved,
не Exact. Полная приёмка обоих корпусов и temporal reports ещё не завершена.

Elder: свободно было75022336B. После проверки отсутствия пользователей/процессов,
формата ar и контрольных сумм удалены только старые статические link caches
двух собственных runtime;168469220B, free243515392B. Уникальные первичные данные
и executable не удалялись. Receipt сохранён на сервере; отдельная normal сборка
Console запущена supervisor2377203/start_ticks307276259 из root1d2d3b0c.

См. [точную постановку и ограничения](N0ProductionCoverage.ru.md). Наличие
build proof либо завершённой Train/evaluate пары не закрывает полный stage7,
исторический replay и независимую оценку. Все остальные обязательства плана
сохраняются.

## Завершение адресного production N0 и серверной очистки

Production N0 проверен на обоих workers: по2 протокола /28 операций,
7/7 data checks и3/3 temporal checks для каждого протокола. Отдельные Console
сборки и настоящие Ns edits при фиксированных индивидуальных Rs,
Train→frozen handoff и malformed-data controls
подтверждены. Численный Core тот же38edfcad7983478a7e2ca736c32ae2703861c1fd;
в этом подэтапе не вводилась новая амплитудная цель или физика.

Primary proofs: dde55f0a0ce4331f194c4ea45b5cfc8933189816 (ASan) и
8b25481711776c45dd5f89a87d477b2203310f60 (normal). Полные403MB корпуса сжаты
до2473616B и2391204B, closure28 runs /1052 artifacts каждого проверена.
Temporal proofs:3e388a5af0ea38d278ea8d00f8600183abdbb99d и
413cdea0b93aa1b8eb44942275dfabcacde52c9c. Все16 уникальных выбранных PNG
непосредственно просмотрены1920×960,32 normal counterparts совпали побайтно,
новых normal PNG0. QA7dfb3a01a18637804efcbf8502279bf17039f71d.

Все16 full Train — SearchUnresolved. Это не положительный результат обучения
или независимой классификации. По графикам установлено, что окно заканчивается
на затухающей реакции; полнота данных объявленного окна не доказывает полного
settling/отсутствия последующих ответов. Эти limits добавлены в план.
Преимущество informed proposal policy на реальном timing-ready случае ещё
требует проверки, как и другие размерности/профили/режимы исходного stage7.

Разрешённая пользователем очистка завершена:433.33GB логического объёма старых
ELF/ar и повторяющихся INFO-логов, плюс715813989B законченных временных копий.
Научные первичные данные, модели/конфиги, исходники и Git history не удалялись.
Текущие Console hashes не изменились. Доступно102.61GiB на Elder,84.55GiB на
системном диске M40 и506.01GiB на M40 Data. Необязательные debug-summary caches
не добавлялись в Git; опубликованы небольшие receipts/selected excerpts.
Новая версия helper прошла4/4 file-retention/fuser/scratch checks на обоих workers.

Детали и полные SHA: [N0 production](N0ProductionCoverage.ru.md),
[maintenance](ServerCleanup-2026-11-01.ru.md), [полный аудит](PlanCompletionAudit-2026-11-01.ru.md).
Адресные подэтапы готовы к root merge; исходные этапы1–12 и цель целиком остаются
открытыми. Следующий приоритет — physical positive/dimension controls и проверка
алгоритмов, затем расширение матрицы; количество пройденных checks не заменяет их.

Дополнение: проверка совместимости N0-шаблона перед приёмкой подэтапа. Исправление 0980f23309e099cb7cc73a1355a2dd25c7f788ab сохраняет полную конфигурацию при вызове подготовителя без новых факторов; раньше такой вызов ошибочно требовал повторного задания диапазона Ns. Проверено исходниками 54382334754986c574c7ccbcd5ded5b55f1b638e на Elder и M40: исходная ошибка воспроизведена через прежний публичный make_job; по 9 проверок для repeat=1/2, по 10 фактических Train-заданий на протокол регенерированы идентично, 1147 исходных файлов каждого корпуса не изменились. Численные прогоны и отрисовка повторно не выполнялись. Исходные отчёты с 7 проверками остаются отчётами своего снимка. Новые квитанции: Reports/StructTrain/TimeLearner/s07-n0-template-contract-normal-a2 (7aeb9655afdc3aec7ef607664393318fe290d1a3), s07-n0-template-contract-asan-a2 (0689def9d7a056bc9e9464d5ba647fcb8e30cbf9). Первые попытки настройки a1 завершились SyntaxError до выполнения проверок и также сохранены. Это приёмка совместимости подготовителя, а не положительный результат физического обучения и не закрытие полного этапа 7.

Новый подэтап native-dimension-controls (feature; ещё не merge в develop):
normal и ASan по 16 реальных cold Train для Classic/Branch × N0/N1 × N=1/2/4/5;
по 4 Exact только в одновходовых identity controls с новым final probe,
по 12 SearchUnresolved при фиксированной геометрии. По два reader набора 4/4
на каждом worker; проверен пятый канал Classic CSV. Дополнительный normal N0
physical proposal control подтвердил измеренную последовательность L1/Ns1 →
L2/Ns1 → L2/Ns2 → L3/Ns1 в обеих топологиях; оба Train SearchUnresolved,
reader 2/2. ASan proposal control и полная временная приёмка ещё выполняются.
Источники/артефакты/ограничения: [NativeDimensionControls](NativeDimensionControls.ru.md).
Это не успешная классификация и не закрытие полной матрицы этапов 3–8.

Уточнение: ASan proposal control завершён, оба случая подтверждены reader 2/2; proof db3211020d6e2695ec2a5768d417ebbc855cbc8f. В работе остаётся temporal/visual приёмка нового подэтапа.

Итог temporal приёмки native-dimension-controls: 16 dimension reports /568
trial-soma pairs и 2 physical N0 proposal reports /42 pairs; temporal checks
3/3 для каждого dimension attempt и proposal набора. Дополнительно baseline
production report reader 3/3. Все 20 выбранных PNG1920×960 прямо просмотрены,
включая пятый soma channel и формы реальных L/Ns кандидатов; full cache manual
review не заявлен. Shared normal/ASan plots обоснованы 252 canonical-equal JSON
packet / byte-equal CSV pairs при отдельных runtime manifests. Proof438a11cae58cd307f6729fbbdb012f8c6ef8e264,
Reports/StructTrain/TimeLearner/s07-native-controls-visual-a1; selected QA записана
отдельно в SELECTED_VISUAL_REVIEW.json. Этот адресный подэтап готов к merge.

Отдельно начато исправление N1 finite-mesh resolution: исходный real normal
контроль имеет measured sign bracket и минимальную ошибку4.7358625548610256e-5
при tolerance1e-5. Baseline proof12f39119a3eacc843441db2cbae58b0a5ad560e4 опубликован
в отдельной ветке. Реализация measured resistance refinement изолирована в
codex/timelearner-n1-measured-refinement (root e19a303f2d9252a5179ad0f457593e48c0c35fd1,
PulseLib bf50ae57512ff0a1591937f4f23cef172a8928dc); новые normal/ASan сборки
выполняются. Эта реализация ещё не прошла серверную приёмку и не находится
в develop; успешная физическая сходимость и классификация не заявлены.

Подэтап dimension/N0 physical controls принят в develop merge
2b5af8c191b6ea20dff0f8b676e702db8c53c82f (старые фразы «готов к merge» выше
описывают предыдущий снимок). N1 measured refinement остаётся в отдельной ветке:
актуальный PulseLib c89a067ea4719c2c3f7546a9cf77b11b188b334d включает code guard
1dddf1b861546eb8e7802ab4ff6610ef2844520e и документацию. Сборки a1 пока проверяют
предыдущий bf50ae57512ff0a1591937f4f23cef172a8928dc/root e19a303f2d9252a5179ad0f457593e48c0c35fd1;
они не подменяют приёмку последнего commit. После их terminal состояния требуется
свежая адресная a2 сборка/проверка, затем physical N1 A/B и temporal reports.
Протокол, ограничения, baseline proof и критерии:
[MeasuredResistanceRefinement](MeasuredResistanceRefinement.ru.md).
