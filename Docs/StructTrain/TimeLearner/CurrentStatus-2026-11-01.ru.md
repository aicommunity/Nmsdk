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
