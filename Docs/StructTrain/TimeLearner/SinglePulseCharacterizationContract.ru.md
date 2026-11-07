# Отдельная одноимпульсная характеристика — контракт реализации

Статус: проект контракта после проверки production-кода 07.11.2026;
**native-кандидат реализуется, runtime-приёмка не пройдена**. Подэтап этапа7 исходного
плана, не замена штатного обучения пачкой. Основания:
[первый импульс](StockFirstPulse.ru.md),
[точный replay](StockWaveReplay.ru.md),
[каналы и обратная связь](NativeChannelDiagnostics.ru.md).

## Задача и границы

Измерить полный отклик неизменной физической модели на один фактический
импульс при той же амплитуде, длительности, частоте и native reset policy.
Разделить число физических входов N и число предъявляемых импульсов P=1.
Сохранить CapturedPerInput, training target, порог, links/storage physics,
references, search history и обученные параметры. Дополнительные максимумы
разрешено наблюдать; нельзя выбирать самый большой и объявлять обучение Exact.

Classic сохраняет рассылку одного потока на все кончики и запись всех N сом.
Branch сохраняет solo routing выбранной физической точки подключения k:
P=1 означает pulse0, а не input0; при k=2 физический selector остаётся2.
Recognition с включёнными всеми входами является другим протоколом.

## Проверенные ограничения текущего кода

* `Core/TimeLearner/NativeProbe.cpp::CheckPattern` требует MaxSpikes=N,
  N строк MatrixData и expectedInputIsi.size=N. Его нельзя обходить подстановкой
  N=1: изменятся физические bindings и размерность сом.
* Подготовка schema3 связывает номер stimulus с активным Branch input.
  Для characterization необходим явный mapping physical_input/pulse/channel,
  а не изменение смысла этого поля в существующих training observations.
* `NDatasetMatrix::SetMaxSpikesPerFeature` вызывает SyncMatricesToDimParams
  и Ready=false. SetMatrixData меняет NumSamples/NumFeatures. AReset снова
  синхронизирует размеры. Сохранить только MaxSpikes или parent property
  недостаточно: нужны исходные значения и формы обеих матриц.
* NativeProbe уже выполняет neuron/dataset Reset до первого импульса,
  не вызывает вложенный Calculate и временно восстанавливает Branch routing.
  Новая операция обязана использовать эту же границу и scheduler.
* Текущий Restore восстанавливает Delay/Advance и routing, но не обещает
  checkpoint физической динамики. Новая операция также не должна обещать
  продолжение старой динамики посреди пачки.

## Изменения компонентов

1. `NativeProbe.h/.cpp`: явный вид запроса TrainingBurst/SinglePulseCharacterization,
   раздельные physicalInputCount/presentationPulseCount и mapping окон.
   Default остаётся TrainingBurst. Снимок transient presentation принадлежит
   executor, который восстанавливает его при любом терминальном исходе.
2. `ProbeSpec/ProbeObservation`, JSON encoder/decoder и Python reader:
   versioned purpose, original training-pattern hash, actual presented-pattern
   hash, physical input ID и pulse ID. Старые схемы сохраняют прежний смысл;
   неизвестные схемы и purposes отклоняются. Номер новой схемы определить
   после сверки всех текущих readers, не переиспользовать имеющуюся версию.
3. `FinalVerification`, TrainingCertificate и configured controller:
   явно отклонять characterization как основание local/final certificate,
   amplitude reference capture или продвижения search. Проверяется production
   путь, не только отдельный decoder.
4. `TimeLearnerProbeJob.cpp` и общий runner: opt-in diagnostic job с полным
   stopped-state import, отдельным trial ID и явным diagnostic-only итогом.
   Не вызывать retarget, не менять Neuron.TrainingPattern/owner configuration.
5. Корневой пакет: prepare/analyze отдельного study, строгий provenance,
   channel recorder, временные графики всех сом с фактическим input overlay.
   Полный cache остаётся на M40; Git хранит primary и выбранные рисунки.

## Транзакция предъявления

```text
require idle native controller and legal consumed boundary
validate full source model, original target and source pattern
capture plain-value dataset dimensions, matrices and persistent controls
capture source/profile identity and model/controller/reference hashes
stop source through native controls
apply transient P=1 presentation through native dataset property mechanisms
read back dimensions, values, links and actual generator identity
perform native preparation/reset; arm recorder before first stimulus
native scheduler calculates the unchanged physical tree
record complete waveform, actual onsets and actual LT/channel signals
close or cancel observation with its true completeness/validity
stop source; restore routing and original dataset shape, values and controls
verify restored target/source/model/controller/reference identities
release boundary only after restoration; otherwise reject and hold diagnostics
```

Plain-value snapshot не использует Alloc/Copy как checkpoint. Порядок
восстановления: размерности/MaxSpikes → полная MatrixData → MatrixClasses →
controls → effective readback. До применения проверить connected properties:
если штатный setter не даёт безопасно наложить и снять overlay, закончить
явным unsupported diagnostic до изменения, а не отсоединять связь молча.
Если native Build необходим для Ready, он допускается только в подготовке
между пробами и с проверкой сохранности графа; не добавлять «будящий» Build
каждый тик. Восстановление после уничтожения/замены компонентов проверяет
native lifetime handles и не пишет через старые указатели.

## Обязательная адресная приёмка

* Реальные Classic/Branch, N=1,2,4 и >4; Branch k≠0, P=1 и штатная P=N пачка.
* Один actual stimulus, полное окно и конечные отсчёты; missing/duplicate onset,
  NaN, обрыв записи и неизвестная схема не дают валидного итога.
* Отдельно waveform completeness и наличие/однозначность пика: полная волна
  с тремя максимумами остаётся допустимой диагностикой, не training PASS.
* Отмена до подготовки, после применения overlay, после первого sample,
  в финальном callback; callback exception и budget exhaustion. Проверять
  полное восстановление source pattern, shapes, controls и links.
* Повтор штатной пачки после characterization совпадает с контролем, где
  characterization не выполнялся: native reset, graph/hash, onsets, все soma
  samples и LT events. Сравнивать при одинаковом абсолютном/относительном
  времени с явно ограниченной floating roundoff, не широким допуском.
* Старые job schemas и default TrainingBurst дают прежние JSON/CSV; новая
  диагностика не принимается ни одним production certificate consumer.
* Единая частота дерева2000/20000Гц; неподдерживаемый multirate отклоняется.
  Проверить effective generator coefficients после изменения частоты.
* Normal/ASan на указанных серверах, actual runtime/source closure, closed
  process groups и released leases; ASan detect_leaks=0 не доказывает leaks.

После приёмки сначала сравнить одиночную волну с префиксом штатной пачки
до второго фактического onset. Затем исследовать перекрытие и обратную связь
контролируемыми вмешательствами с отдельными model revisions. Только эти
измерения могут обосновать новое правило assignment; этот контракт его
не вводит и не отменяет исторические августовские4/8–6/8.


## Кандидат native API

В отдельной feature-ветке добавлены ProbeSpec schema4 с обязательным
SinglePulseCharacterization (sourceTrainingPatternHash, physicalInputCount,
selectedInputIndex), production подготовка/восстановление DatasetMatrix и
строгий JSON roundtrip. Старые схемы1–3 не получают дополнительных полей.
Обучающие protocol consumers допускают только1–3; дополнительная проверка
отвергает diagnostic marker даже при подмене номера схемы в памяти.
Число физических сом и topology bindings не меняются.

Добавлен настоящий integration fixture для двух топологий, N=1/2/4/6,
2000/20000Гц, сравнения штатной пачки до/после, ошибок preparation/sample/
финального sample и сохранности исходного InputPattern. Эти проверки пока
не считаются прошедшими. Native Build используется только для временного
DatasetMatrix в подготовке/восстановлении; neuron Reset — на штатной границе.
Если восстановление не удалось, executor сохраняет snapshot и не разрешает
следующий edit/Queue, вместо объявления исходного состояния восстановленным.

Native reader и его controls добавлены; адресная серверная проверка выполняется
отдельно от первоначальных21 tests. Console job4, admission и paired stock CLI
подготовлены в следующем кандидате, но ещё не скомпилированы/не проверены на
реальных archived models. Полный cancellation/connected/replacement fault scope
не закрыт. Существующий Console job3 сохраняет прежнее поведение.


## Кандидат Console job4 и paired study

Job4 явно содержит presentation.kind=single_pulse_characterization. Его
источник — полный stopped-state archive; запрещены одновременная Rs intervention,
assigned-burst policy и изменение stimulus physics. Новый строгий reader читает
ProbeSpec/Observation4 отдельно от training reader, проверяет actual onset,
полноту/clock/числа, physical selector и независимое соответствие peak полному
CSV. Полная волна при ambiguous peak остаётся диагностикой с training_eligible=false.
Возврат current base revision должен подтверждать восстановление модели.

`python -m Scripts.StructTrain.TimeLearner.stock_single_pulse STUDY --runtime RUNTIME --output NEW`
готовит обе пары jobs до первого native действия: исходная пачка с каналами
и один импульс с теми же каналами. Exact candidate выбирается прежним правилом
first invalid probe == archived model revision; последняя отличающаяся модель
не подставляется. Перед каждой пробой проверяются source-state/packet/trace hashes.
Сначала полный burst сравнивается с исходным Train; затем single-pulse trace
сравнивается с burst строго до второго фактического onset. После этого момента
равенство не требуется: предъявления различаются по объявленному протоколу.

Выход study содержит фактические локальные максимумы каждой сомы и записи
LT/Feedback; они не становятся назначенными response waves или сертификатом.
Совместный plotter различает в заголовке burst replay и одноимпульсную
характеристику. Primary должен быть опубликован в Git до построения такого
verified report. Результаты запуска этого кандидата пока отсутствуют.


## Адресная normal-приёмка native API

[Срез rootb5cfae4/Pulse302124b](SinglePulseCharacterizationNativeVerification.json)
прошёл37 native функций и13 readers на M40. Это включает четыре функции
размерностей/частот, два before/after burst controls и три fault функции,
каждая из которых проверяет обе топологии. В первичном corpus40 записанных
проб:24 schema4 diagnostic и16 before/after burst, отдельно от старых burst
controls. Exact относится здесь к совпадению recorded ordinates; training
certificate не создаётся. Проверки не устанавливают пригодность произвольной
физики, всей lifecycle/storage матрицы или итоговую разделимость.

Две ошибки стенда сохранены: первая запись файлов под одинаковыми именами
между тестами; затем неверный каталог reader corpus в оболочке. Все37 native
tests второй попытки прошли. После исправления пути отдельно выполнены13 readers
на тех же исходных файлах, без нового расчёта модели. ASan, второй сервер,
полный fault scope и фактический stopped-model Console job4 остаются открытыми.
