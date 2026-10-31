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

## Active-request import: реализация ожидает runtime-приёмки

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
Запущены совместно с capture/lifecycle/codec/fixed PostTune/threshold regressions;
до получения результатов runtime-приёмка не заявляется. Automatic configured
dispatcher, публичный mapping target-reference/mid/parallel-peak, full matrix и
снятие optional guards этим не выполнены. Старые исторические verdict не меняются.
