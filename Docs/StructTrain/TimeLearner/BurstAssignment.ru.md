# Сопоставление волн пачке: проверенный измерительный подэтап

Дополнение: [AssignedWaveSelection](AssignedWaveSelection.ru.md) вводит
явный выбор назначенной волны в широком окне. Описанная ниже исходная
семантика одиночного оконного максимума сохраняется как IsolatedWindow.

Ветка stage07/burst-assignment ответвлена от принятого develop
aee8c2a0b64b2dcec5dbbe1d9f291ef9a8440157. Реализация прошла указанную ниже
адресную и серверную приёмку. Configured ControllerVersion=2 и основной поиск
этим подэтапом не реализованы.

## Недостаточность одного окна

В контролируемом примере стимулы p0/p1 подаются в 0.1/0.3 с, их измеренные
волны имеют максимумы в 0.4/0.8 с. Окно 0.3…0.55, подписанное p1, содержит
единственный положительный максимум 0.4 и даёт положительную delayFromStimulus.
Прежняя WindowOnly схема принимает его. Подпись окна не доказывает, что это
вторая волна: фактически окно выбрало задержанную первую.

Пример проверяет production ProbeRecorder, без копирования тела измерителя.
WindowOnly schemas 1/2 сохраняются для воспроизведения прежнего критерия;
их valid не превращается задним числом в доказательство полного assignment.

## Новый явный протокол

Schema 3 требует typed source profile и WaveAssignmentPolicy::OrderedWholeBurst.
Schema 1/2 не разрешают этот flag, schema 3 не разрешает WindowOnly. Тот же
выбор хранится в VerificationProtocol, references и certificate context.

Для каждого используемого физического канала recorder после закрытия полного
окна выделяет все положительные локальные максимумы выше уже объявленного
minimumAmplitude. Плато сохраняет реальные первую/последнюю sample timestamps.
Число волн должно совпасть с числом фактических ожидаемых стимулов; их IDs и
строгое временное упорядочение должны совпасть. Начальный/конечный обрезанный
максимум, недостающая или лишняя волна запрещают принятие. Прогноз задержки не
восстанавливает отсутствующую волну.

В рамках объявленного order-preserving протокола k-я измеренная волна относится
к k-му стимулу и не может предшествовать ему. Выбранный оконный peak должен
точно совпасть с этой волной по measured time/plateau/raw/amplitude. Иначе
результат Ambiguous с burst_window_assignment_mismatch. Нельзя вместо этого
молча расширить окно или выбрать другой максимум по выгодному временному остатку.

FinalVerification повторно проверяет число/каналы/порядок/конечность evidence,
raw−baseline, causal timing и соответствие выбранного peak полной assignment.
Одного valid=true недостаточно. Изменение policy/schema не переносит старые
references или certificate в новый протокол.

Дополнительная проверка перед приёмкой связала input с физическим владельцем.
Для schema 3 порядок inputs совпадает с порядком actual stimuli; Classic input i
измеряется на soma channel i, с полной размерностью baseline N. Branch использует
channel 0, а native prepared context сообщает фактический selectedInputIndex;
он должен совпасть с запрошенным индексом verifier. Native preflight отклоняет
неправильный channel, selector↔stimulus mapping и усечённое ожидаемое число
стимулов до предъявления. Это исключает capture reference другого входа при
формально верных ID/числах. Новые guards и отрицательные controls проверены
отдельно от снимка 9357c93; прежние 269-case данные остаются данными его кода.

## Область применимости

Это проверка наблюдаемой последовательности при предположении одного
разрешённого положительного отклика на стимул с сохранением порядка. Она не
доказывает идентифицируемость причины для произвольной нелинейной модели:
например, потеря одной волны и дополнительная осцилляция другой могут дать то
же общее число максимумов. Для configured controller такое предположение
должно быть отдельно проверено для профиля и протокола; полную physics/inhibition
матрицу этот подэтап не заменяет. Неидентифицируемые случаи требуют отдельной
характеризации/вмешательства либо явного unresolved, а не Exact по догадке.
Single-pulse characterization остаётся отдельной пробой, а обучение проверяется
штатной пачкой.

Новые допуски по времени или амплитуде не вводятся. CapturedPerInput остаётся
собственным raw reference входа; timing tolerance и алгоритм поиска не меняются.
Существующий native executor принимает schema 3 через тот же scheduler/reset/
routing путь. Проверки реальных Classic/Branch при 2000/20000 готовятся отдельно
от контролируемого примера; результаты ниже относятся только к указанным случаям.

## Промежуточные результаты

Root a312505 (полный SHA в runtime manifest) на M40 прошёл 40 адресных tests:
семь контролируемых assignment cases, 14 recorder regressions, 15 final-verifier
cases и четыре native Classic/Branch × 2000/20000. Elder-1 также прошёл эти
40 tests. Это ещё не full CTest или полная физическая матрица.

В следующем диагностическом fixture два стимула разделены 1 мс, без изменения
storage physics. Сравниваются WindowOnly и OrderedWholeBurst на настоящем
нейроне: ожидаемое слияние двух волн должно оставаться явным missing/ambiguous
assignment, даже если локальное окно содержит измеримый максимум. Первичные
CSV/JSON сохраняются раздельно. Root 9d795e2d1142868b01d72fdb6764935d8e0b4260
прошёл четыре парных native controls на обоих серверах: WindowOnly даёт valid,
а WholeBurst фиксирует одну волну вместо двух и burst_missing. Это нарушение
идентифицируемости по выбранному протоколу, а не доказательство непригодности
нейрона для распознавания. Root 9357c93 прошёл на обоих серверах ещё шесть
native schema 3 controls: Classic/Branch × N=1/4/6 при 2000 Гц. N=1 проходит
реальную повторную FinalVerification с Exact constraint certificate; N=4/6
проверяют всю последовательность на каждом используемом канале. Для этого
снимка прошли четыре maintained CTest suites на обоих серверах (PulseLib 269:
260 pass, 9 standard skips) и 44 адресных M40 ASan tests с detect_leaks=0.
Пакеты s07-burst-elder1/m40 опубликованы в Git; проверены 440 artifact hashes.
Эти результаты относятся к 9357c93 до дополнительных owner guards.

Отдельный анализ первичных файлов на обоих серверах подтвердил побайтовое
совпадение CSV WindowOnly/WholeBurst и одинаковые actual stimulus timestamps
для каждого из Classic/Branch. Analysis сохранён как
s07-burst-merged-waveform-comparison.json. Execution status в обоих режимах
completed: меняется validity наблюдения, а не факт исполнения окна. Этот
пример не меняет исторический критерий и не отменяет августовские 4/8–6/8.

Усиленная привязка physical input проверена отдельно на root
2b97f4fbb74776a8f44f254a5910fe59ba1e51f4 / PulseLib
e46a00b2dbb11c54daf727ede0d14ba60a8e6552: 46 адресных tests прошли на обоих
серверах. Неправильный Classic channel и Branch selector дают ожидаемые
native_input_channel_mismatch/native_solo_selector_mismatch до arm и до первого
sample. Full CTest этого снимка прошёл на обоих серверах: четыре maintained
suites, PulseLib 273 cases, 264 pass, 9 standard skips. M40 ASan — 48 адресных
tests, detect_leaks=0. Пакеты s07-burst-final-elder1/m40 опубликованы; проверены
386 artifact hashes. Older manifests не переименовываются в новую closure.

После интеграции принятого model API из PulseLib отдельно проверен root
4bd02ff03a6169a92a579b0fa27b40d05aaf0354 / PulseLib
dc62a3e70426c4e97fa696e3f5e23f1b12f97611. На обоих серверах 61 адресный case
дал 60 pass и один стандартный helper skip; четыре NativeArchive parents явно
выполнили fresh child processes. Все 16 native burst CSV, model hashes и
валидность/статусы совпали с предыдущим снимком до переноса. Проверены ещё 130
artifact hashes в s07-burst-combined-elder1/m40. Это проверка взаимодействия
изменений, не повторный full CTest или ASan совместной closure.

Итоговые пакеты:
[Elder-1 full](../../../Reports/StructTrain/TimeLearner/s07-burst-final-elder1/README.md),
[M40 full/ASan](../../../Reports/StructTrain/TimeLearner/s07-burst-final-m40/README.md),
[Elder-1 combined](../../../Reports/StructTrain/TimeLearner/s07-burst-combined-elder1/README.md),
[M40 combined](../../../Reports/StructTrain/TimeLearner/s07-burst-combined-m40/README.md).
Все проверки source/result transfer выполнены через Git; локально проверялись
хеши и целостность gzip как данные, без численных прогонов.
