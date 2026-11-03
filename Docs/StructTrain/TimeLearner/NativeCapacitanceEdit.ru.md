# C-trim: физический baseline и правка ёмкостей

## Актуальный статус, 03.11

Explicit baseline/edit/joint API и completed/stopped transfer приняты в develop;
проверенные commits, normal/ASan evidence и точные ограничения приведены в
[адресной приёмке](C0Acceptance-2026-11-03.ru.md). Ниже сохранена хронология
построения этих проверок. Формулировки о pending относятся к своему снимку,
а не отменяют состоявшуюся приёмку.

Автоматический owner последующих edits — отдельный кандидат. Normal C2 прошёл
8 native и19 independent readers; evidence
`a928fb92edd0880728a697da0fed6d7ede3e7d4a`,259 members проверены.
ASan, transport43/dormant-image import и visual QA ещё выполняются;
[текущий контракт и handles](CapacitanceOwnership.ru.md).
Bounded C-trim search по-прежнему отсутствует: V2 с SyncCapacitanceTrim On
выдаёт явную диагностику. Принятие physical API не включает этот режим.

## Исторический normal checkpoint baseline/growth

Последующий normal gate baseline/growth завершён21/21 +9/9 unit на rootc6345fa6,
все349 members и61 probe packet проверены. Полный временной отчёт:
93 trial-soma pairs,1680PNG в M40 cache,20 выбранных оригиналов непосредственно
просмотрены. Новая [schema2 переноса C₀](CapacitanceStateTransfer.ru.md) —
следующий срез кода с отдельной ещё не завершённой приёмкой.

## Историческая постановка: привязанный baseline

В PulseLib `cc1eb71c8a4be8b2241c2b9a870ac4b533e01a51` реализованы отдельный
baseline schema 2, привязка к ModelSpec/исходному графу/storage-образам,
проверка статической физики каналов и расширение C₀ при штатном росте.
Прежний baseline schema 1 сохранён для совместимости. Совместный кандидат
возвращает расширенный baseline только после commit. Добавлен отдельный
codec состояния поправок C с проверкой полной карты и revision модели.

Новые восемь native fixtures проверяют Classic/Branch, N0/N1, 2000/20000 Гц,
неоднородные C₀, повреждение свидетельств, изменение физики, рост из storage,
повторное масштабирование относительно исходного C₀ и неполную карту.
Spec: `Scripts/StructTrain/TimeLearner/specs/native-bound-capacitance-v1.json`.
Для объединённого gate 21 cases отдельно задан отчётный spec
`native-bound-capacitance-report-v1.json`: ровно 61 ожидаемая временная трасса,
включая все 24 трассы новых восьми fixtures. Он использует штатные графики
всех выходов сомы с наложенным фактически предъявленным входом, обзором и
увеличенными временными окнами. Это постановка полного отчёта, пока без
утверждения о состоявшемся render или визуальной приёмке. Полный render
предназначен для кэша M40; в Git — primary и выбранные проверенные рисунки.
Это пока реализация и тестовые постановки, не runtime-подтверждённый PASS.
Автоматическое включение этого состояния в NativeLearnedState и bounded
C-trim search контроллера V2 остаются открытыми. V2 с C-trim On ещё запрещён.

## Исторический checkpoint standalone API после восстановления VPN

Elder standalone gate завершён: 8/8, 32 raw probes проверены, 8 сравнений
ответа при одинаковых входах подтверждают ненулевое изменение сомы. Evidence
5acd3eebbf2c812a5e04e07bd0a14f88eb2ea4fb. M40 ASan тоже завершён8/8:
23f0086845092feed0967112b1cd59583d086149;32 CSV byte-equal и32 JSON packets
полностью совпадают с normal. Это прежняя standalone версия, не joint API.
Temporal cache на M40 завершён: 8 cases, 32 trials, 48 trial/soma pairs,
1787 PNG, 5545 hash-проверенных файлов.16 выбранных PNG просмотрены поштучно,
сохранены в Git с протоколом Review.ru.md. Полная48-pair визуальная приёмка
не заявляется. Это диагностические traces с ambiguous peaks, не сходимость.

Совместный editor L/Ns/Rs/C (Pulse9694ae3) проверяет Rs domain после новой C.
Первый Elder gate numerical root722c978: 8/10; оба fault rollback теста
не прошли (получен Applied). Отрицательная попытка сохранена в evidence
7364e82e219b1a63b6fa6f598dc7876dc2e59b02 вместе с runtime, build и raw data.
Её нельзя считать проверкой работающего отката.

Source audit: BeforeReset/BeforeCalculate вызывают соответствующие A-hooks;
ни UComponent/UItem, ни NPulseNeuron их не перекрывают. UContainer ловит
исключения и возвращает штатный bool. Для отделения этого механизма от
ошибки fault injection новые тесты фиксируют факт hook и фактическую C.
Rdk добавляет специализированный process-local operation ledger, сохраняя
bool и порядок lifecycle. Native Init/Reset, probe и recognition проверяют
новые ошибки после marker. Rootd8bf0419ef3e022514f77613e2f4a5acbe4e4875:
Elder9/9 Rdk и12/12 native passed, evidence6bb5e09b897d0932f641f42aa8e966b935f713a9.
Сбой реально наблюдался при4nF и завершился полным восстановлением графа;
прежняя история ошибок не блокирует следующую исправную пробу.
M40 ASan новой версии ещё собирается. Дополнительные8 downstream fixtures
на normal не прошли предпосылку certificate при исчерпании sweep; нужны A/B
и корректные положительные/отрицательные контроли, без ослабления критериев.
Develop остаётся прежним.

Ниже сохранены предыдущие checkpoints; сведения о живых jobs в них исторические.

Новая feature от developf1708eb97bc3b412c101dffc468221af2bc87e59.
Pulse исходная точкаa18c8a1097a221e5aca3bfc2c1afc07fb2534a56.
Первая implementation4239b807c37311fe91ca3aae322aab7445795aec.
Серверная приёмка ещё не завершена; develop не меняется до результатов.

Рабочий numerical rootf68305c3b54bfebac1bdfd71efb7bb9cfb230d32,
Pulse30d4b1d92007c028a6f85cd7630dd401b3226872. Первая сборка остановилась
на const UEPtr→base-handle преобразованиях; они заменены штатным .Get().
Вторая собрала library API, но остановилась на missing dependent-template
keyword в новом тесте. Обе попытки сохранены на каждом worker; их gate
supervisors остановились с prerequisite_build_failed, численные cases не шли.

Следующие отдельные jobs при последней проверке живы по PID/start_ticks:
Elder builder3906945/319677913, supervisor3906946/319677918;
M40 builder1980074/270220931, supervisor1980081/270220936.
Readbacks: s07-capacitance-edit-build-normal-a3 / -asan-a3 и
s07-capacitance-edit-normal-a2 / -asan-a2. Runtime roots оканчиваются
runtime-s07-capacitance-edit-normal-a3 / -asan-a3. Не менять их source/build
и не запускать повторы до установления terminal или отсутствия владельца.
Это checkpoint запуска, а не результат: ещё нужны actual8 JUnit cases,
проверка raw packets/CSV, temporal reports и scoped acceptance.

Последующая проверка: обе сборки a3 завершены; native gate ещё жив на обоих
workers. Elder CLI3909822, M40 CLI1982839. В сохранённом stdout Elder прошли
первые5 cases (четыре2000Hz и ClassicN0At20000); M40 прошли первые3 cases
2000Hz. Это partial progress, не полный8/8. Не менять source/build/runtime.

Для четырёх завершённых Elder2000Hz cases проверены исходные native packets
и CSV через production raw reader. До/после по361 samples, реальные входные
samples идентичны. Максимальная разность ответа сомы при scale1.1:
N0=0.00026699785413619725, N1=0.00012980397012751776 для обеих topology.
Readback: s07-capacitance-initial-raw-normal-a1/result.json. Широкие diagnostic
окна дают peak_ambiguous:input0, поэтому эти traces показывают физическую
чувствительность, но не являются valid peak measurements или convergence proof.

В feature после numerical rootf683 добавлены полные before/after model identity
артефакты и C++ assertions реальной чувствительности к C при одинаковых input
samples. Они находятся в root3ab4b5a414210504114801fe9aee9d57c2b45077 и ещё не
собраны/исполнены. Core Pulse30d4 не менялся. Повтор с дополненными fixtures
можно готовить только после terminal текущих owners; результаты старых fixtures
нельзя объявлять проверкой нового instrumentation.

Source audit старого C-trim выявил ClassCapacitance из parent MembraneCapacity
и запись scalar DendriteCapacitance[i] одновременно в Exc/Inh каналы всех
выбранных сегментов. Это не сохраняет heterogeneous child physics. Подмена
одной константы другой проблему не решает. Старый режим не переименован в V2.

Новый общий API CaptureNativeCapacitanceBaseline сохраняет actual path→C0
всех каналов с отдельными LT/Soma/Exc/Inh значениями. ApplyNativeCapacitanceScale
работает только на consumed native boundary. Owner guards исключают внешнее
изменение активного Train и frozen recognition. Каждый выбранный dendritic
membrane получает C[path]=C0[path]×scale; повторное применение идемпотентно.
Soma и LT не являются разрешёнными объектами trim. Prototype/parent defaults
не меняются. Нет learner Reset/Build или вложенного Calculate.

Алгоритм физической операции:

```text
validate boundary, ownership, baseline schema/hash/frequency and scales
resolve every selected existing channel and its explicit positive finite C0
clone current physical graph through native snapshot/import
apply candidate C0 * scale independently to actual channels
initialize/reset preview; assess actual native integration equations
capture full predicted semantic identity; dispose preview
verify that live model remained unchanged
apply candidate only if effective C differs; native physical Init/Reset
compare full live identity against preview
on unexpected live failure: restore previous C and verify original identity
```

Неизвестные equations/connected Capacity, отсутствующий channel baseline,
NaN/Inf, bounds, unsafe integration и повреждённый baseline дают явный отказ.
Проверяется весь baseline, включая невыбранные каналы; даже idempotent edit
сверяет полный predicted/live identity, сохраняя живой lifecycle без Reset.
Ни универсальное tau>=2dt, ни fallback1nF не используются. Baseline является
явной декларацией физического исходного состояния; его принадлежность к
profile/ModelSpec и controller persistence ещё не реализованы и не доказаны.

Declared gate8 использует реальные storage/Environment/scheduler fixtures:
Classic/Branch×N0/N1×2000/20000Hz, N0 с двумя tip synapses. Проверяются
heterogeneous Exc/Inh, LT/Soma preservation, scaling/restore, no-reset повтор,
native physical roundtrip, реальные waveform probes, negative candidates и
рост до нового сегмента без baseline. Такой сегмент пока отклоняется.
Численные и интеграционные проверки выполняются только на Elder/M40.

## Историческая постановка joint API и оставшийся поиск C-trim

Рабочее дополнение joint API: общий preview теперь может включать
L/Ns/Rs/C перед assessment. Отдельный C-plan helper выделен механическим
commit aafdaea80c2f630750d2c0ffe1bd45dde8c2c35a; joint implementation —
Pulse9694ae3e0bb1db386939113f640120ac63190540. Оба ещё не прошли серверную
приёмку. Старые overloads без C передают nullptr и сохраняют прежнюю задачу.
Rs domain рассчитывается после применения C к private preview. При live
отказе joint edit использует NativeLearnerGraphCheckpoint для обоих детей;
adapters обновляют Neuron/Dataset и result.graphWasReplaced сообщает замену.
Checkpoint может явно отвергнуть неподдерживаемые внешние bindings до commit;
поддержка полной connectivity матрицы этим не заявляется.

Новый gate10 (2000Hz) объявляет6 joint cases +4 standalone regressions.
N1 positive control использует C×4 с явно разрешённой maxRelativeChange=3,
а не defaults C-trim. Из реально вычисленных domain bounds выбирается Rs,
запрещённая при старой C и допустимая при новой. N0 меняет Ns2→3 вместе с C.
В fault cases настоящий neuron subclass бросает исключение на втором live
Reset, после изменения C; preview faults не вооружены. Проверяются возврат
всего исходного графа, обновлённые handles, следующий физический отклик и
запрет внешнего edit при активном Train. Это пока declared checks, не PASS.
Поддержка поиска C в контроллере и её persistent state всё ещё отсутствует.

1. Привязка baseline к ModelSpec/storage и explicit trained-state transfer
   уже приняты адресно. Автоматическое владение после последующих edits
   проходит отдельную матрицу; включение C в controller candidate/plan остаётся.
2. Extension C₀ при росте из verified storage принят для explicit API.
   Автоматическое сохранение active/dormant maps при обычных edits ещё
   проверяется. Не переснимать уже trimmed C как новый C₀.
3. В общем контроллере реализовать bounded C candidates по свежим timing/amp
   measurements, с исходными targets/tolerances и ограничением поправки.
4. Classic: корректировать выбранный путь. Branch: явный интервал общего кабеля;
   инвалидировать все затронутые observations/certificates и вновь оценить Rs
   domains после C edits. Прогноз задержки не является доказательством пика.
   Для совместного поиска L/Ns/Rs/C нужен общий native preview кандидата:
   недопустимо оценивать Rs domain по старой C или отвергать совместно
   допустимый кандидат только из-за недопустимого промежуточного C-edit при
   старой Rs. Новый отдельный API намеренно проверяет фиксированные остальные
   параметры; его последовательная композиция не доказывает joint feasibility.
   Controller action/readback/evidence должны описывать полный physical candidate,
   включая C correction state, а не только прежние InputParameters(L,Ns,Rs).
5. Допустить Exact только по fresh all-input pass нового revision; сохранять
   negative/quantized/best-effort/budget reasons раздельно.
6. Проверить Train→export/import→Test, warm continuation, growth/Build/load,
   interruption/rollback и PostTune на поддерживаемых физических профилях.

До этих шагов ControllerVersion2 по-прежнему явно отклоняет optional C-trim.
Этот physical primitive не считается завершением исходных этапов4/5/7/8.
