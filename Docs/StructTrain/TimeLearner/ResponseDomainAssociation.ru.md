# Контракт частичного сопоставления областей

Подготовлен production utility PulseLib `ResponseDomainAssociation.h/.cpp`.
Он использует общий `MeasuredResponse`, требует полный набор конкурирующих
пар channel×stimulus и сохраняет измеренные признаки при отказе сопоставления.
Модель, протокол, hash паттерна и фактические observation IDs связаны явно.

Это диагностический шаг этапа7. Hypothesis — единственный наибольший максимум
под объявленными областями; это не Valid origin и не разрешение обучать.
Shared вершины/плато, ties, clipping, nonfinite, gaps, неполнота и stale context
получают разные причины. NoCandidate не считается PhysicalInfeasible.

Включён counterexample предыдущей задержанной волны внутри формально
подходящей области следующего импульса: он доказывает, почему даже эксклюзивная
оконная гипотеза не является доказательством происхождения. API всегда
TrainingCertificateEligible=false; контроллер, schemas1–6 и сертификаты
не переключались. Signed offsets actual peak/onset сохраняются отдельно от
утверждения о принадлежности. Описание API — PulseLib
`Docs/TimeLearner/ResponseDomainAssociation.ru.md`.

Приёмка использует настоящий production CPP в target
`Test_PulseLib_ResponseDomains`. Fixtures охватывают меньшие/поздние/равные
максимумы, плато и onset внутри него, конкурентов, отсутствующие отклики,
guard samples и исходные индексы, N=1/2/4/6, разные physical channel IDs,
перестановку domains, absolute clocks, stale pattern/model/protocol и
неполные/повреждённые записи. Отдельная native applicability-проверка и
интеграция в обучение остаются необходимыми; unit PASS их не заменяет.

На Elder прошли все 26 проверок без пропусков. Evidence commit:
`aa9051831d1014185969686a7d64852fb083b51e`; compiled root:
`bd6722a49c59e337065c53d63411cb0095443adc`; PulseLib:
`a21adcb1cf0d0b9fb9f29cfdb3722414b1fcae3e`.
Независимо проверены все 66 членов архива, исходники по Git, JUnit inventory,
фактически загруженный executable, неизменность runtime и освобождение lease.
Receipt: [ResponseDomainNormalVerification.json](ResponseDomainNormalVerification.json).
На M40 также прошли 26/26 без пропусков с ASan. Evidence commit:
`68440c23ba1832e25d012aa3c3383fbec8658d84`, receipt:
[ResponseDomainAsanVerification.json](ResponseDomainAsanVerification.json).
Это отдельная сборка production utility, не полная сборка SDK. Проверены
все 100 членов архива, включая две неудачные подготовительные попытки:
неверную привязку worker script и подключение вложенного CMake Google Test
без родительской настройки версии. Исправления запускателя не меняли
проверяемые C++ исходники. Native bridge ещё не принят.
На локальной машине численные тесты не выполнялись.

## Следующий этап: bridge штатной пробы

Это подготовка интеграции, а не разрешение использовать Hypothesis в Train.
Production-адаптер должен получить `PreparedVerificationProbe` и фактический
`ProbeSpec` из `NativeProbeRequest.onPrepared`, отсчёты и `newStimuli` из
`onSample`, а complete/result — после закрытия штатной пробы. Он не вызывает
`Calculate`, не меняет target, storage, структуру или правила сброса.

Компоненты: PulseLib `Core/TimeLearner/NativeProbe.h/.cpp` и отдельный
diagnostic adapter; корневые `Tests/Integration/Libraries/Test_PulseLib_NativeExecution.cpp`
и reader в `Scripts/StructTrain/TimeLearner`. API adapter отделить от
`NativeTrainingService`: отсутствие результата/ошибка artifact sink не должны
превращаться в успешное измерение. У незавершённой пробы нельзя достраивать
complete по числу уже полученных отсчётов.

Сохранять spec и observation, base/effective revision, epoch, routing,
Branch selector, идентичность реальных физических каналов, actual onsets,
baseline и максимальный допустимый gap, полный список измеренных максимумов,
исходные индексы, plateau bounds, знаковые смещения и причины отказа.
Результат связывать с hash первичной трассы и версией метода. Reader повторно
вычисляет результат из первичных данных на сервере; проверка только hash
самого JSON не подтверждает правильность его численных полей.

Обязательные проверки native bridge:

- Classic/Branch через штатный scheduler: фактические каналы, routing и
  selector совпадают с effective graph; дополнительные Calculate отсутствуют.
- Полная обычная пачка и отдельный single-pulse режим представлены разными
  протоколами; один не заменяет другой.
- N=1/2/4/6, 2000/20000 Гц; повторное чтение пакета не меняет результат.
- Поздняя предыдущая волна, общая вершина, plateau с onset внутри,
  меньшие экстремумы и поздний более высокий максимум; отсутствие отклика
  постороннего импульса не аннулирует независимую диагностическую гипотезу.
- Подмена timestamp, source index, pattern/model revision, physical channel
  или selector, пропуск конкурирующей области, gap и incomplete запрещают
  положительный diagnostic receipt.
- Уже сохранённые 14 high-threshold условий разобрать тем же production
  методом на сервере. Они являются исследовательскими/отрицательными
  контролями и не обязаны превращаться в успешное обучение.

Отдельно после bridge требуется метод `AttributionEvidence`: область
применимости, подтверждающие пробы, конкурирующие объяснения и причины
unresolved. Single/omit-пробы способны опровергнуть назначение, но не дают
универсального разложения нелинейной пачки. Эксклюзивность окна не является
такой приёмкой. Только после неё согласованно версионировать Train-контракт,
`ProbeObservation`, `FinalVerification`, `NativeTrainingService`, serializers
и Python readers. До этого `TrainingCertificateEligible=false` сохраняется.
