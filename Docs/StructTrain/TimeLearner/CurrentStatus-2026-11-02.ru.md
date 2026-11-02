# Подтверждённый срез 02.11: полнота временных данных

## Последний проверенный результат: transport и временные отчёты

Elder completed transport после image extraction: 8/8 на root c6345fa6,
evidence `abac5800c0ec93c1ecec100b37480982ec176f00`; M40 полный ASan transport
на прежнем root589c7e30: 8/8, evidence `a311a6e3d4133faf57ac826b61460d7ba64917ff`.
Оба delta архива локально восстановлены по точным Git references и проверены:
458/466 logical members; в каждом случае 52/52 CSV и 48/48 сопоставленных
probe packets равны исходному c17f7f61, 8/8 solo model revisions совпали.
Это explicit sync=0.2 transport controls, не классификация8/8 и не default0.02.

Для normal21 baseline/growth завершён полный temporal render: 61 наблюдение,
93 trial-soma pairs,1680 PNG/SVG/PDF в M40 cache. Все20 selected PNG напрямую
просмотрены, включая local-detail шкалы при20000Hz. [Отчёт просмотра](../../../Reports/StructTrain/TimeLearner/s07-bound-capacitance-temporal-selected-a1/VISUAL_REVIEW.ru.md).
Полный cache не объявлен вручную просмотренным. Primary и20 selected — в Git.

Новая schema2 C₀ transfer ещё не прошла runtime gate. B1 остановился из-за
include, исправленного в Pulse69d463a. B2 успешно собрал native executable,
затем обнаружил отсутствие Test_UComponent_Lifecycle в fresh CMake cache.
Это расхождение BUILD_TESTS/BUILD_TESTING, а не падение численного теста.
[Исправление](BuildTestSwitch.ru.md) выполнено в отдельной ветке от develop,
commit `7290955b0269c1b3b90f205ec3b35e38d51d11dd`; требуется configure/build gate.

Дополнительный дефект объёма/стабильности package: [runtime StepDuration](ArchiveTelemetryNoise.ru.md).
Исправление ещё не реализовано. Старые primary не удаляются.
Весь исходный план остаётся активным; этапы1–12 выполнены частично.

## Последующее изменение кода: перенос C₀ в model package

Первая fresh сборка schema-2 переноса B1 остановилась до unit/native
из-за пропущенного include QJsonDocument. Исправлено в PulseLib
`69d463aa50144a1c8ddb4a674bb900c2a07e769f`; нужен следующий build/test cohort.
Failure evidence `6f05f66ea89d93762dee1860a9952f4e5cc95400`, cache seal
`bd35b706609d1c1acfb8df230e2f231cb4cfdebe`. Исходники старого runtime с
21/21 и завершившихся 8/8 transport при этом не менялись.

В feature добавлен [schema-2 Train→Test](CapacitanceStateTransfer.ru.md),
retention проверенного импортированного baseline и независимый reader.
Это следующий ещё не проверенный сервером код, не расширение старых PASS.
Предыдущий root `c6345fa6d2121625e93ec3d26433786fcc85cccc` на Elder завершил
21/21 native и 9/9 unit без ошибок; evidence опубликован в
`26fbfc17dfe717e0f8ae1f2e7b099adcf468f0aa` и требует локальной проверки hashes.
Последующая локальная проверка выполнена: SHA архива и всех 349 members
совпали; сохранены 61 probe packet и восемь bound C₀ states. Архив занимает
1 762 278 байт. Evidence объединён через merge commit
`39cdc257b3760b7baf28fd052170477046924188`. Это normal-проверка указанного
Core cc1eb71, не проверка следующего schema-2 transfer Core 922ba91.
Все восемь новых baseline/growth cases прошли, включая 20000 Гц.
Дальнейшие прежние readbacks ниже сохранены как промежуточные снимки.

## Текущая работа: storage-bound C₀

Серверный запуск нового среза: root
`c6345fa6d2121625e93ec3d26433786fcc85cccc`, PulseLib
`cc1eb71c8a4be8b2241c2b9a870ac4b533e01a51`. Elder build завершён,
9/9 unit PASS. На момент readback новые cases: 4/4 при 2000 Гц и
Classic N0 при 20000 Гц PASS; остальные native cases ещё выполняются.
Общий gate 21 пока не закрыт и не заменяет ASan-проверку.

Активные/ожидающие readbacks на Elder (префикс
`/home/user/timelearner-refactor/readbacks/`):

- `s07-bound-capacitance-normal-a1`: supervisor PID 4065102,
  start ticks 320989028; 9 unit и 21 native.
- `s07-bound-capacitance-publication-normal-a1`: PID 4067107,
  ticks 321000497; ждёт закрытия owner и публикует primary через Git.
- `s05-bound-capacitance-transport-normal-a1`: PID 4074659,
  ticks 321053640; ждёт успешного предыдущего gate, затем запускает
  все восемь explicit sync=0.2 transport controls на том же runtime.
- `s05-bound-capacitance-transport-publication-normal-a1`: PID 4075041,
  ticks 321056785; ждёт transport, сохраняет новые байты и точные Git-ссылки
  на одинаковые primary исходного `c17f7f61…`, без повторного копирования.

Пути source/build/runtime не менять до закрытия всех их owners. PID сверять
со start ticks; timeout подключения не считать завершением процесса.
Результаты публикации и их member hashes ещё предстоит проверить локально.

Добавлены schema 2 baseline, проверяемое происхождение новых C₀ при росте
и отдельное сохраняемое состояние поправок ёмкости. Новые восемь fixtures
ещё требуют серверного запуска; старые PASS не подтверждают новый код.
[Состав и ограничения](NativeCapacitanceEdit.ru.md).
VPN Automats2 восстановлен. M40 продолжает ASan completed-transport без
перезапуска: шесть из восьми cases прошли, идёт Classic PostTune.
Это промежуточный статус, не закрытие gate. Develop остаётся принятым
`f1708eb97bc3b412c101dffc468221af2bc87e59`; этапы 1–12 остаются частичными.

## Последнее дополнение: transport и Build

Elder completed transport:8/8 на явно объявленном sync0.2,8 Exact packages
проверены по SHA/допускам. [Результат и ограничения](CompletedBoundaryFixtures.ru.md).
Это отдельный положительный контроль; прежние default0.02 cold-Train8 failures
сохраняются и не превращены в PASS. Evidencec17f7f61f11a05c7ea8992e77593528690c956c5.

Rdk Build всё ещё возвращал false при caught exception, вопреки требуемому
контракту. Реальный native baseline подтвердил единственный bool failure:
738985c742f881e3fca3ff23229f68db7d3adf68. В Rdk feature исправлены возврат и
consumer guards Connect/CreateStructure/Environment. [Контракт и проверка](NativeBuildBoolContract.ru.md).
На Elder новый numeric root5d73cd0858abc1e93655d5fa10189225da990201 с Rdkc3850711:
9/9 unit,13/13 native и4/4 explicit0.2 transport passed. Evidence
094bced1b7431e726b052e315eceb2e04e2ad277. ASan этой коррекции ещё требуется;
develop не менялся. Документационные heads Pulse5bdd08b и Rdk48d6548e
отличаются от numerical f9272f5/c3850711 только Docs; Core trees совпадают.

M40 версия до bool correction (rootd8bf/Rdk03497edf) завершила9/9 unit и12/12
native под ASan,1259632ms native. Опубликовано в31840e7173094912856ddc0f43d8a446ed73ebba:
492 verified members.36 native CSV/packets и112 negative downstream CSV/packets
совпали с normal. Отдельный regression8 закончил теми же failures и сохранён.
Следующий transport explicit0.2 root589 на M40 жив (PID2115894/start_ticks271244564);
при последней проверке4/8 passed, calibration/PostTune ещё выполняются.
Publisher2126622 ждёт его завершения, сохраняет primary delta с normal Git base,
затем запускает isolated9/13 correction. К новой Rdk bool correction завершённые
результаты до этого запуска не относятся.

Дополнительная задолженность stage9/12: native_test_reports schema1/2 требует
JUnit без failures. Для отрицательных test runs нужен явный diagnostic report
mode с сохранением failed inventory, partial windows и неизвестной полноты;
не ослаблять PASS policy старых схем. Прямой probe renderer partial observations
поддерживает, но единого отчёта failed native suite этим ещё не получено.

Ниже сохранены предыдущие уточнения этого дня. Полными остаются только этап0
и перечисленные scoped проверки; исходные этапы1–12 остаются частичными.

## Checkpoint: восстановлена связь Automats2

Обе машины доступны через user@10.245.1.12. Elder standalone C-editor8/8
с32 raw probes опубликован в5acd3eebbf2c812a5e04e07bd0a14f88eb2ea4fb.
M40 ASan той же версии завершён:8/8,6359859ms. Evidence
23f0086845092feed0967112b1cd59583d086149 содержит32 проверенных raw probes:
все32 CSV побайтно равны normal, все32 packets равны по полному JSON.
Это проверка старого standalone API, не нового joint editor/operation ledger.

Полный temporal cache завершён на M40:32 trials,48 trial/soma pairs,
1787 PNG,5545 проверенных файлов. В Git только16 выбранных рисунков
с индивидуальным просмотром и metadata; остальные изображения остаются
воспроизводимым cache. [Протокол просмотра](../../../Reports/StructTrain/TimeLearner/s07-capacitance-temporal-selected-a1/Review.ru.md).

Первый joint L/Ns/Rs/C gate Elder:8/10, оба rollback faults не прошли.
Отрицательные данные, runtime и сборка сохранены в7364e82e219b1a63b6fa6f598dc7876dc2e59b02.
Новая feature numerical closure:rootecedb55cd89ea7fd9d6c806268a2761f5a1b0c4a,
Pulsef9272f5244e6183206e1a47a89eadb06a60abbb4,
Rdk03497edfa52e6a0ee2c2e8cd4eaa5021211d514d. В ней специализированная
диагностика пойманных Rdk исключений не меняет bool lifecycle или scheduler.
Первая сборка eced остановилась на ошибке области видимости переменной в
новом тесте. Отрицательная попытка сохранена в
f018cacc04c0ef34f6ddfab9fe62166e4066a840 (15 verified members).
Исправленный numerical rootd8bf0419ef3e022514f77613e2f4a5acbe4e4875
на Elder прошёл9/9 Rdk unit и12/12 native cases. Evidence
6bb5e09b897d0932f641f42aa8e966b935f713a9:229 verified members,36 raw trials.
Оба rollback теста зафиксировали реальное исключение при C=4e-9, восстановили
граф и следующую native пробу. Calculate failure делает пробу incomplete/invalid.

Расширенный normal gate8/8 failed ДО проверки transfer/recognition/calibration/
PostTune: при maximum_sweeps_exhausted прежние fixtures всё ещё требуют
completed certificate. Это открытая регрессия проверки предпосылок, а не
PASS downstream-путей. A/B со старым неизменным runtime f683 завершён:
те же8 failures,112 CSV побайтно равны,112 Train packets равны целиком.
Evidencef0af7f4a3629e6cf6e60fe2225c86952fd9800c7. Для этого набора проблема
существовала до joint editor и Rdk ledger. Это не общее доказательство
отсутствия регрессий. Первый control отклонён source alias guard; отдельный
worktree Bin получил собственный core.worktree, первичный отказ сохранён.
Нельзя менять допуски или объявлять stopped Train завершённым ради этих tests.

Следующий обязательный пункт: исправить зависимости downstream suites от
неподтверждённого completed Train. Нужны реальные положительные certified
модели и отдельные negative/diagnostic cases для long-ISI cold Train; нельзя
выдавать отрицательный Train за проверку conversion/calibration/PostTune.
Сохранённые модели, cold retrain и changed-protocol evaluation проверять
раздельно. Добавление очередного узкого PASS не закрывает эту задолженность.

На M40 жив новый ASan job s07-operation-diagnostics-asan-a1,
PID2078457/start_ticks270983842: isolated runtime,9 unit +12 native cases.
Следующий regression gate8 ждёт его завершения по PID/start_ticks;
source/build/runtime до окончания всех owners не обновлять.

Принятый develop по-прежнему f1708eb97bc3b412c101dffc468221af2bc87e59.
Полный C-trim V2, его persistence/growth/search, общая матрица и этапы1–12
не закрыты. Ни текущие traces, ни эти gates не являются результатом
классификации. Ниже прежние checkpoints сохранены как история уточнений.

Текущая алгоритмическая работа: [per-channel C-trim physical editor](NativeCapacitanceEdit.ru.md).
Новый API и8 actual native fixtures находятся в отдельной feature; серверная
приёмка ещё идёт. Старый scalar C-trim не считается исправленным этим API,
ControllerVersion2 по-прежнему явно отклоняет режим до полной интеграции.
Baseline provenance/persistence, growth extension, bounded C search и fresh
final verification остаются обязательными. Develop этим checkpoint не меняется.

Следующее дополнение: [декларативный validation runner](ValidationSuites.ru.md)
прошёл66/66 без skips на каждом worker и5 actual CLI negative controls.
Versioned suite фиксирует Python package, все test IDs и1599-file Git corpus.
Остальные artifact-dependent suites не объявляются принятыми. Численные
алгоритмы этим дополнением не меняются; C-trim/Quantized/BestEffort остаются
открытыми требованиями. Исходная accepted closure этого подэтапа — root
47ef1229474099fd9d540175c8a7f3f5a6cc95b5 / Pulsea18c8a1097a221e5aca3bfc2c1afc07fb2534a56.

Дополнение к PlanCompletionAudit-2026-11-01.ru.md. Полностью завершённым
этапом исходного плана остаётся0; этапы1–12 частичны. Узкие gates не заменяют
обязательную матрицу. Принятый develop44334e272de8429f29775512a860584c60350899
был исходной принятой точкой до описанного ниже scoped merge.

Адресная приёмка search/scheduling/diagnostic/ranking завершена:
PulseLib develop mergea18c8a1097a221e5aca3bfc2c1afc07fb2534a56 опубликован,
его tested Core не изменился. Корень записывает точный gitlink и принимает
feature следующим --no-ff merge. [Scope и доказательства](SearchDiagnosticAcceptance-2026-11-02.ru.md).
Дополнительно на каждом worker60 выполненных Python tests без failures/errors,
один N0 corpus class skipped; все1599 Project.ini roundtrip byte-exact.
Общий запуск122 modules не прошёл без внешних fixtures и сохранён как
неудачная попытка, а не полный PASS. Полные этапы1–12 по-прежнему частичны.

Обновление после восстановления VPN: все четыре ожидавшихся ASan задания
завершились. Integrated163:163/163; recording18:18/18; public preflight:
14 positive/6 negative/2 one-tick Train; public diagnostic:6/6 операций.
Readers24/24 +8/8 integrated, без skips. Proof44548f908365f5030445e4ced11a71147d044331:
2172 members/11207017 compressed bytes, hashes полностью проверены локально.
407+88 CSV и413+94 probe packets равны normal;94 включает6 aliases.
Для diagnostic отдельно равны10 inline trials и4 source CSV:
proof286f7e1b4499db2bc4e9ad49e5980dbd219866bf.
ASan native20 также уже входит в ранее пройденный gate81 на Pulse225.
Это закрывает ожидание перечисленных gates, но не полную приёмку feature.
Подробные source scopes, ограничения и temporal linkage:
[CompletedASanGates](CompletedASanGates-2026-11-02.ru.md).
Ниже сохранён журнал прежних checkpoints; упоминания live/pending относятся
к моменту соответствующей записи и заменены этим обновлением.

Уточнение текущего feature: public diagnostic-evaluate теперь реально
проверен на Elder normal,6/6 операций и7/7 portable readers. Два завершённых
diagnostic Test, два прерванных и два ordinary Console rejections используют
настоящий остановленный публичный Train. Proof480c7683fb91c237d420f441693cd80a2190f3b2
содержит465 проверенных members/4733324 bytes. Источники external_stop,
сертификат отсутствует; обе модели TP0/FP0/FN2/TN2. Это не успешная детекция.
Отдельный partial reader и отчёт сохраняют отсутствующие пробы как unknown,
не создавая файлов наблюдений. M40 render завершён:4 отчёта/15 observed
trial-soma pairs/80 PNG,10/10 checks,9 selected original PNG просмотрены.
Proof4661b39647b204e3ca04ee613bb08bb6d7cadc88; QA DiagnosticRecognitionVisualQA.json.
Дополнительные ordinary+diagnostic readers27/27 без skips:
proofe85f003d6060f4ea7769ad71b40eacfc7b3cd969. ASan-приёмка нового контура pending.
Подробности: [DiagnosticRecognition](DiagnosticRecognition.ru.md).

Следующий незавершённый алгоритмический подэтап:
[finite candidate ranking](FiniteCandidateRanking.ru.md). В production
BoundedTraining устранена потеря различий при нулевом tolerance и overflow
нормированной ошибки. Corrected old-Core baseline:8 ожидаемых failures;
correction на Elder:81/81,15/15 readers и4 stopped-boundary audits.
Proofs244399829e94bae3d619c858f48431e89ce59505 и
f9e823ced7d51614a2a1af307405bbdaaac0478f полностью проверены после Git fetch.
20 контроллерных сценариев теперь дополнены4/4 настоящих multi-length
physical cases на обоих workers. Native baseline4 failures сохранён; correction
выбирает measured61ms вместо70.5ms без ложного Exact. ASan81/81 также прошёл;
raw readers21/21 на каждом worker, все48 corrected CSV byte-equal и48 packets
semantically equal. Полные8 temporal reports/96 probes/144 soma pairs/864 PNG
в M40 cache,3/3 automated checks;14 selected original PNG directly reviewed.
Все SHA и границы в FiniteCandidateRanking.ru.md/validation/VisualQA.
Независимый ASan worktree сохраняется; старый live163 не обновлялся.
Подэтап не принят в develop; defaults, CapturedPerInput,
fresh final gate и условия Exact не изменены. Полные этапы1–12 остаются открытыми.

## Завершено

Исходный root07167d55125ced4eeff72703a718203e8c90bfc7/Pulsefca7141:
Elder163/163 и JUnit readers7/7; public Console на обоих workers14 positive,
6 negative,2 one-tick Train, readers28/28. Saved nonexact completed replay:
4 модели/input0 и5 readers на worker. Это узкие проверки, а не классификация
полной матрицы. Источники: SearchTermination.ru.md, LegacyCompletedReplay.ru.md.

Проверка CI163 выявила407 CSV/413 primary probe packets, включая6 packets
без CSV. Exact/warm/retarget fixture вообще не записывал временные данные.
Ещё4 explicit-Reset diagnostics содержат raw JSON samples без closed probes.
C++ PASS не закрывает эти пробелы; immutable результат не исправляется задним числом.

Numeric rootd06585dfc2a739f2244f7ca59328721fe21475dd добавляет запись
отсутствовавших проб с сохранением callbacks. На Elder сборка и18/18 cases
прошли:88 packet/CSV pairs,6 дополнительных packets — подтверждённые aliases,
не повторы. Цель, физика и tolerances этим instrumentation не менялись.

Reader schema2 явно учитывает untraced/gaps/aliases. На реальном CI1638/8
checks; новые данные5/5, schema1 wall regression10/10. Исправлен общий reader:
service_model.json с совпадающим префиксом не является номерной пробой.
Неучтённый probe любого имени отклоняется. Failed reader attempt сохранён.

Все299 members primary archive проверены после Git fetch,835002 bytes:
proof5f84cdf009b9d1537f464635b16a8096cb00741b,
`Reports/StructTrain/TimeLearner/s03-native-trace-recording-normal-a1`.
Readers2e785da3e7f84ea1173ab0b6c55bdc58ab78982a и
ce63736ba79d1ed6d97a230ea76aebca5b70324f.
Подробнее: [NativeTraceCoverage](NativeTraceCoverage.ru.md).

## Журнал прежних заданий и приёмки (terminal уточнён выше)

M40 ASan163-a2 на07167d551 остаётся живым:PID1745907/start_ticks268723161,
execution budget21600s. Его source/build/runtime не обновлялись. Прежний a1
контролируемо прерван из-за ошибочного общего wall budget; partial evidence
сохранён. Ни terminal a2, ни PASS заранее не заявляются.

На M40 Data из Git proof5f84cdf получены primary новых88 проб. Full temporal
report завершён в `report-cache/s03-native-trace-recording-normal-a1`,
driverb1787ca05f678c690aebc54221a1c0f0681eafbd; прежний PID1791275 закрыт.
Все138 trial/soma pairs покрыты821 PNG;3/3 coverage/hash/scale checks прошли.
Все14 selected PNG прямо просмотрены1920x960: cold/warm, physics-change,
external stop и deadline. Partial traces не дорисованы после последнего sample.
Это рендер Elder normal данных, не ASan-прогон нового instrumentation.
Proofab1ff2ec6f1eed706f98a5ac0dcbfc9d9237bd39:33 members/2078999 bytes,
hashes полностью проверены. QA: NativeTraceCoverageVisualQA.json. Весь кэш
вручную не просмотрен и в Git не добавлен. Старый CI163 также требует собственного
отчёта407 проб и отдельных raw Reset графиков.

Следующий probe render407 запущен отдельно на M40 из проверенного Git proof3cc20c1,
без обновления Python checkoutb1787ca05 и без изменений ASan runtime.
Readback:`readbacks/s03-integrated163-temporal-cache-m40-a1`, cache:
`report-cache/s04-s07-integrated163-normal-a1`. Supervisor1796987/ticks269055558,
renderer1797026/ticks269055735; wall budget7200s относится только к построению
рисунков. `terminal.json` сохраняет реальный returncode/elapsed; при checkpoint
результата ещё нет. Шесть untraced packets и5 gaps остаются видимыми, raw Reset
plots этим запуском не строятся. Не обновлять этот Python checkout до terminal.

Последующее подтверждение:407 render завершён(returncode0,1343.526s),
557 trial/soma pairs/5600 PNG. Все16 reader checks прошли, в том числе3 проверки
этого полного кэша,3 регрессии recorder88 и10 wall/raw controls.24 selected
original1920x960 PNG прямо просмотрены: Classic/Branch,N0/N1,2000/20000Hz,
финальные diagnostic probes и100-tick peak zooms. Proofb091e60425ed4cd8c4218ae44d9aa9582aa93143:
55 members/4528772 bytes полностью hash-verified. QA:Integrated163TemporalVisualQA.json.
Весь кэш вручную не просмотрен и в Git не добавлен.6 исторических CSV и прежние
Exact/warm traces не появились задним числом. Renderer/Python checkout теперь
освобождён и обновлён отдельно; ASan163 source/runtime не менялись.

Отдельный raw Reset supplement теперь завершён:4 diagnostics/6 soma pairs,
21 PNG в `report-cache/s04-s07-integrated163-raw-reset-normal-a1`;10/10 readers,
9 selected PNG directly reviewed1920x960. Источник — исходный Elder CI163,
не повтор66 native cases. View66 содержит копии настоящих JUnit nodes и wall
artifacts с original/derived hashes. Proofc9831d3fb73d5eab337dce1c4cbf40f88a678efa,
15 members/934815 compressed bytes полностью проверены после Git fetch.
QA:Integrated163RawResetVisualQA.json. Неудачная попытка system-Python без
matplotlib сохранена; a2 использует существующий plot-venv. Closed probe
по-прежнему отсутствует по контракту Reset; графики показывают только raw samples.
Это закрывает необходимость отдельных Reset-графиков для normal CI163, но не
его6 untraced packets/Exact-warm gap или полный ручной просмотр всех407 проб.

После освобождения M40 нужен отдельный ASan gate18 numericd06585d.
Не обновлять source активного163, не перезапускать до terminal/identity check.
Дальнейшая приёмка и --no-ff merge детей, затем корня остаются обязательными.

## Оставшаяся работа исходного плана

Полные evidence/property review; lifecycle/storage/heterogeneous/growth и
physics/inhibition/dimension/frequency матрицы; весь model transport и
публичный diagnostic evaluation; legacy/V2 A/B и режимы алгоритмов,
Quantized/BestEffort, conversion/PostTune/C-trim/calibration; миграция scripts;
production scheduler/leases/crash recovery и fault matrix публикации;
независимые frozen order/ITI/reset эксперименты; сквозная документация.

Нового научного результата разделимой классификации этим срезом не получено.
Августовские визуально подтверждённые4/8–6/8 сохраняют доказательность своего
исходного протокола; перестановки и увеличенный ITI тогда не проверялись.
