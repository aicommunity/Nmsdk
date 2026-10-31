# Неизменяемая граница Train → finalization: адресные проверки

NativeFinalizationBoundary хранит значения, а не ссылки на owner/storage или
checkpoint динамики. CaptureNativeFinalizationBoundary читает настоящий экспорт
Solo, исходные phase parameters и фактические связи параметров (путь provider,
имя свойства, порядок sources, connected/external kind). Getter не пишет во
внешний источник и не вызывает Build/Init/Reset/Calculate исходного owner.
Экспорт штатно создаёт и инициализирует отдельные rehearsal/image instances;
это не прозрачный checkpoint динамики и не отсутствие любых storage-операций.

Допустима только ready/initialized Solo-модель с Finished training service и
полностью освобождённой границей probe: ни queued/running, ни непотреблённого
результата/физического routing state. NativeProbeOwnsControl сам по себе этого
не доказывает; новый IsNativeProbeAtEditBoundary учитывает состояние executor.
Lifecycle всех живых descendants, session/epoch/outcome и значения/связи controls сравниваются до и
после экспорта. Исходный training outcome/certificate сохраняется без повышения.

Stopped package по умолчанию отвергается; явный allowDiagnostic сохраняет
его как diagnostic_only с null certificate. Это не разрешение conversion или
продолжения обучения посреди пробы. Class value не содержит Rdk pointers и
должен переживать recognition import, Reset/Default и teardown реального owner.

В частности, независимо сохраняются AutoCalibrate, PostTune, Mid и silent
probe threshold; foil count не превращается в бюджет weight candidates.
Legacy Branch parallel-peak path отмечается отдельно даже при AutoCalibrate=false.
Public mode enums переводятся явным switch: legacy CanonRmin=1 и KeepDone=3
не совпадают с порядком NativePostTuneControllerMode. Неактивные параметры
сохраняются как декларация; неизвестный используемый enum отвергается.

Реальный InstallNativeRecognitionState не просто очищает NativeConfiguredPlan:
он заменяет его восстановленной cold configuration из Solo. Training service
заменяется пустым, а VisitNativeRecognitionControls зеркалирует Need/PostTune/
AutoCalibrate=false. Поэтому исходная phase declaration не восстанавливается из
последующих live mirrors. Внешний stop через connected property нельзя получить
проверкой setter: UProperty может пропустить setter при равенстве значения либо
получать значение из provider. Это требование к будущему phase dispatcher.

Здесь реализован только захват независимой границы. Он ещё не установлен в
Calculate/Reset hooks, не снимает guards optional modes и не заявляет поддержку
target-reference/parallel-peak/mid dispatch. Родительскую модель следует Init/Reset
до импорта завершённого learner: последующий явный parent Reset штатно сбрасывает
контроллер. Не добавлять обходные «будящие» Build/Reset ради сохранения checkpoint.

Приёмка: реальные Classic/Branch source packages, source bindings, queued probe,
external stop и распознавание полного объявленного набора после import; неизменность
снимка после Default/teardown; отсутствие зависимости от порядка public enums.


## Проверяемая последовательность

1. Штатно инициализировать/reset cold parent, затем импортировать полный Solo.
2. Выполнить штатные owner Build/Init и проверить Finished / свободную probe boundary.
3. Захватить immutable boundary; проверить неизменность lifecycle, модели, controls,
   provider values и глобального model clock.
4. Выполнить полный recognition import. Его transient controls и service могут
   измениться; frozen original declaration и training outcome не меняются.
5. Предъявить все объявленные target/foil patterns штатным scheduler, сохранить
   реальные наблюдения; проверить recognition revision и исходный frozen hash.
6. После Default/teardown owner читать только значения frozen document. Нельзя
   выполнять rollback/import или обращаться к уничтоженному owner из snapshot.

Девять native tests охватывают Classic/Branch × Snapshot, ConnectedRequest,
QueuedProbe, ExternalStop плюс явное сопоставление всех public PostTune enums.
Connected true request штатно блокирует импорт, требующий Need=false, без записи
в provider и подмены графа. После внешнего снятия запроса полный import разрешён;
снимок исходного true/connected остаётся. Stopped snapshot разрешён только с
явным diagnostic opt-in и не получает certificate. Это API захвата, не phase
scheduler и не рекомендация включать ранее неподдерживаемые optional modes.


Снимок фиксирует finalization intent именно в момент Capture, а не историю
изменения параметров во время Train. Будущий dispatcher должен отдельно
замораживать декларацию при Start и различать собственные переходы controls.
Нельзя поднимать IsNeedToTrain после восстановления Finished ради тестового
снимка: для ControllerVersion=2 это штатный запрос новой сессии/ResetControl.
Connected provider может иметь true без вызова setter; этот реальный случай
проверяется отдельно. Принимается фактический request value, а не желаемый.

## Серверные проверки 31.10: исходный экспорт и сравнение

Root a282fe9a56cd49c09bc81da128b2f1e4c8283417, PulseLib
f8929f906d24f8824450b9542445bcb9016f9337: Elder normal — 24/24,
20.492 s; M40 ASan — 24/24, 128.163 s, без skips. Девять boundary tests,
десять lifecycle regressions и пять configuration codec tests. ASan leak checking
выключен; это не полная матрица этапа 8 и не доказательство качества распознавания.

До усиления XML-сравнения попытка a3 также прошла 24/24 на обоих workers.
Во всех восьми capture-comparison records a3 между before и captured/after
изменялись только native XML двух class definitions NPMembraneBio:
InputFeedbackSignal с Rows=0/Cols=0 без данных → Rows=1/Cols=1 со значением 0,
а также связанные XML/package hashes. Граф/параметры, identities, references,
training evidence и dataset совпали. Причина перехода внутри native allocation/
reuse пока не установлена: Snapshot уже вычисляет Identity перед SaveComponent,
поэтому гипотеза обратного порядка этих двух операций не подтверждается кодом.

Текущий тест сохраняет XML целиком, проверяет его SHA и нормализует только
указанное точное представление нулевого feedback в NPMembraneBio. Не разрешено
исключать все native XML как volatile state: это могло бы скрыть потерю физики,
не включённой в semantic identity. Первичные before/captured/after сохранены
без нормализации. Независимый finalization_boundary_evidence.py сверяет их,
binding к frozen source и полный объявленный набор target/foil replay trials;
не проверяет этим происхождение обучения и не выдаёт scientific verdict.

Попытка a1 остановилась на missing test include до запуска native tests.
В a2 четыре full-package equality assertions не учитывали описанный feedback
cache transition: результаты и причина сохранены. Последующие прогоны не
переписывают эти неуспешные попытки. В proof входят полные исходные fixture runs,
а не только локальные baseline jobs/models: run manifest проверяется по каждому
включённому artifact. Первая упаковка отклонена именно из-за неполной closure;
полный набор берётся из ранее опубликованных Git primaries с проверкой SHA.

Configured dispatcher, автоматическое подключение к hooks и снятие guards optional
modes остаются открыты. Временные отчёты replay описаны ниже.

Компактные первичные доказательства:
[normal](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-boundary-normal-a1/README.md)
и [ASan](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-boundary-asan-a1/README.md).
По 202 members, соответственно 1014552 и 1029284 bytes. Каждый содержит все четыре
native attempts, отклонённую первую упаковку, 14 независимых consistency checks,
16 negative controls и два полных исходных portable runs / 84 artifact entries.
После --no-ff merge проверены все inventory/archive/member SHA. Reader source:
e50af3eef91b2da932b086b8d9cab2f81fac1969. Это проверка целостности и условий
capture/replay, не полная аттестация mapped-file lifetime или обучения fixtures.

## Временные графики replay

[Visual proof](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-boundary-visual-asan-a1/README.md)
содержит метаданные четырёх отчётов: Classic/Branch × plain/connected, оба исходных
target/foil patterns и все каналы сомы — 12 полных trial-soma pairs. Все native
samples сохранены, входные импульсы наложены на SumPotential. PNG 1920×960,
overview и detail; detail не менее 8 pixels/native tick. Источник — реальные a4
наблюдения, никаких новых численных прогонов для отчётов не выполнялось.

Renderer root 52bd7ff2f43ec828714df8758bc468c0e97fff0b. Более поздний root
a32c3590a4689dbc52a9009d7d2f0b6a23e79ec2 проверяет backend до создания output;
три серверных report tests прошли за 1.031 s, без skips. Проверены точные waveform
samples, полнота patterns/channels, overlay, PNG/SVG/PDF и масштабы. Неполная
проба и недоступный backend не создают output tree.

Полный cache — M40 Data `/media/user/Data/TimeLearnerRefactor/cache/s08-native-finalization-boundary-asan-a1`:
576 files / 51389834 bytes. Git: 38 metadata members / 30840 bytes и четыре PNG.
После --no-ff merge проверены все inventory/archive/member/PNG hashes и 12 bindings
к трём исходным файлам каждого отчёта: replay, capture comparison, fixture job.

Четыре выбранных target/first-soma overview/detail Classic и Branch просмотрены
в исходном 1920×960: подписи, шкалы и обе кривые читаемы, импульсы различимы.
Full cache, foil/остальные somas/connected figures и SVG/PDF вручную не приняты.
SumPotential соединяет точки линиями, вход изображён ступенчато; видимый sub-tick
сдвиг начала не доказывает причинного опережения. Единицы модели SI-unverified.
Эти imported-model controls не доказывают успешного обучения, independent Test
или завершения configured finalization. Для queued/stopped controls нет
выдуманных waveform-проб. Итогового scientific verdict нет.

## Active-request import и clock isolation: адресные normal/ASan проверены

PulseLib ec3d7b4fc01efec5bfd727b3057e86a66bb6a94b, root
c0496d2538054afd580fc46f00922144aabe630c добавляют явный
ImportNativeFinalizationState(package, implementation, boundary). Этот путь
требует завершённого исходного Solo, активного запроса, прежних controls/bindings,
точного source_solo кандидата и повторной проверки исходной модели. XML остаётся
точным, кроме документированного zero-feedback cache перехода двух image snapshots.
Сравнение dataset не ослаблено; ни одного Calculate при entry нет.

Managed recognition hold хранит immutable исходную границу. Need остаётся true,
а CalculateMode и исходные PostTune/AutoCalibrate не заменяются frozen mirrors.
Меняться могут только физические threshold mirrors; controls и bindings остальных
параметров читаются заново. Реально снятый connected request даёт
native_finalization_external_stop, даже если setter не вызывался. Значение provider
не записывается и не восстанавливается силами learner.

Общий transaction scope использует ReplaceNativeRecognitionState, сохраняющий
текущую policy при import кандидатов/rollback. Прежний ImportNativeRecognitionState
остаётся явным frozen import и по-прежнему требует Need=false у внешнего source.
NativeFinalizationIntent возвращает value-copy исходного документа. Это не
сохранение текущей физической динамики и не controller checkpoint.

Четыре новых интеграционных сценария: Classic/Branch × CalculateMode 0/1,
реальный connected request, полный fixed PostTune с разными measurement/final
thresholds, отклонение чужого source, external stop и явный frozen import.
Normal: 44/44 tests на root c0496d253 (191.796 s), затем 18/18 на root a05416971
(68.693 s), без skips. Второй прогон включает ранний отказ unsupported C-trim
до model commit; не поддержанный trim не сбрасывается импортом в ноль. Базовый
ASan на c0496d253 завершил 44/44 (1353.853 s), без skips, leak checking выключен.
Новый guard и clock isolation отдельно проверяются в следующем ASan gate.
Automatic configured
dispatcher, публичный mapping target-reference/mid/parallel-peak, full matrix и
снятие optional guards этим не выполнены. Старые исторические verdict не меняются.

Независимый reader: root 8e3e6678664c2940063879b2dd6257e16ad76aa5,
2/2 tests (23.196 s), четыре actual transactions и 20 negative controls.
Проверены исходные Train summary/packets/CSV, сохранённый outcome search_unresolved,
полные измерения весов и финальные реакции. Для каждого случая по 1602 weight и
1602 final samples. Выбор весов не объявляется успешным распознаванием.

Первый reader ошибочно требовал сохранения CalculateMode исходного Train (1)
после явного post-import переключения replay в 0. Фактическая рекурсивная сверка
обнаружила только этот semantic source delta для обоих mode-0 случаев. Теперь
source lineage допускает только объявленный переход управления, записывает
original_training_calculate_mode и calculate_mode отдельно; другие semantic
параметры и training evidence остаются неизменными. Необъявленная смена режима
отклоняется отдельным negative control. Failed reader и исходные данные сохранены.

### Обнаруженная зависимость от часов предыдущего задания

Шесть из десяти прежних fixed records byte-exact; четыре positive selection/
roundtrip отличаются, в том числе абсолютным временем на 0.0015 s (три шага
предшествующих lifecycle tests). Полные recursive differences сохранены; их
waveform/научная эквивалентность пока не заявляется. WithFreshModel уничтожал
модель, но не сбрасывал часы общего Environment: свежий job наследовал model
time предыдущего теста. Это дефект общего production helper, не основание
переписывать исторические измерения.

Root 87e36a376afe513c0355c468ba7eb8afa3829219 исправляет начало job через
штатный Environment.Reset после DestroyModel и до CreateModel. Проверяется
фактическое нулевое время; bool Reset не используется как error channel. Новая
проверка выполняет два последовательных fresh jobs по три native ticks. Для
полной runtime-проверки изменения запущен отдельный 45-case gate; до его
окончания исправление clock isolation не считалось принятым. Теперь normal
45/45 завершён (196.890 s), ASan 45/45 (1370.820 s), без skips, включая два
последовательных fresh jobs; leak checking выключен. Адресная двухсерверная
проверка этого изменения закрыта, полные этапы 2/8 этим не объявляются выполненными. Промежуточный
ожидавший 18-case ASan job отменён до checkout/runtime creation, вместо него
проверяется сразу полная актуальная версия; receipt сохраняется. Работающий
44-case run при этом не прерывался. Старые задания и runtime не обновляются.
Полная историческая серия и серия D не запускаются.

Независимый reader на ASan a1 также завершён: 2/2 tests, 20.827 s, без skips;
четыре actual transactions и 20 negative controls. Новый clock-isolated ASan a3
не смешивается с этим исходным набором данных.

[Normal primary proof](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-ownership-normal-a1/README.md)
содержит 203 members / 2642116 bytes: a1 44-case, a2 18-case, reader attempts,
compatibility differences и два полных original portable runs / 84 artifacts.
После --no-ff merge проверены все inventory/archive/member SHA. В этот proof
не входят отдельный clock-isolated normal a3 45-case run и новые ASan runs:
это исторический proof предыдущего подэтапа. Новые полные доказательства —
[normal clock-isolated](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-ownership-normal-a2/README.md)
(150 members / 2028576 bytes) и
[ASan clock-isolated](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-ownership-asan-a1/README.md)
(219 members / 3453216 bytes). Каждый содержит два original portable runs /
84 artifacts. Все archive/member/inventory SHA после --no-ff merges проверены.
Reader gates на clock-isolated данных: normal 2/2 (23.695 s), ASan 2/2 (20.228 s),
по четыре transactions и 20 negative controls. Происхождение Train не переписано.

## Временные графики managed transactions

[Visual proof](../../../Reports/StructTrain/TimeLearner/s08-native-finalization-ownership-visual-asan-a1/README.md):
четыре reports Classic/Branch × CalculateMode 0/1, 24 complete trial-soma pairs,
оба target/foil и все soma channels при measurement и preserved final thresholds.
Дополнительно прежний filename-based entry point построил реальный fixed report
(ещё четыре control pairs). Все 60 original source files имеют прежние SHA.
Общий data renderer получает actual replay source вместе с оригинальными
summary/packets/CSV и повторно проводит полный audit; исторические файлы не
подменяются ради loader. Ни модели, ни численные эксперименты при рендеринге
не рассчитываются повторно.

Root renderer eb58ac90344ca6ecc8a0952998e1702aa6879808; реальный gate 115.774 s.
Cache M40 Data `/media/user/Data/TimeLearnerRefactor/cache/s08-native-finalization-ownership-asan-a1`:
1334 files / 111753950 bytes. Git: 61 metadata members / 61320 bytes и восемь PNG.
Проверены все hashes и 64 bindings к actual managed records, original model files
и original CSV из полного ASan primary proof.

Восемь выбранных target/first-soma overview/detail для обеих topology и двух
состояний физики просмотрены в 1920×960: подписи, сома и реальные импульсы читаемы.
Detail имеет ≥8 pixels/native tick, прореживания нет. Foil, другая Classic soma,
mode-1 figures и остальные tiles/SVG/PDF вручную не приняты; они прошли coverage
checks. SI units unverified; соединённые линиями samples не доказывают sub-tick
опережение импульса. Source Train остаётся search_unresolved; weights_selected
не означает recognition success. Configured dispatcher и full stage 8 открыты.
