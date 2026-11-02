# Подтверждённый срез 02.11: полнота временных данных

Дополнение к PlanCompletionAudit-2026-11-01.ru.md. Полностью завершённым
этапом исходного плана остаётся0; этапы1–12 частичны. Узкие gates не заменяют
обязательную матрицу. Принятый develop44334e272de8429f29775512a860584c60350899
не изменён; алгоритмическая feature ещё не принята.

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

## Живые задания и ближайшая приёмка

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
