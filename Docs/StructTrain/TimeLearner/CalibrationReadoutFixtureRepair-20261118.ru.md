# Источник для проверок LT readout и сохранения калибровки

Статус: новый Linux native прогон выполнен:19/21 PASS; два отказа — коллизия
имён артефактов между readout и persistence cases. Исправление имён подготовлено,
повторная native проверка не завершена. Алгоритм и допуски не изменены.

Полный Windows247 остановился в шести NativeThresholdPotential и
NativeCalibrationPersistence cases до целевого readout: общий источник Train
не дал certificate при ISI .01/.08 и коротком ограниченном кабеле. Совпавший
old/new A/B precondition сохранён, его отказ не объясняется DATA API.

N1 CalibrationBoundaryFixture теперь использует уже существующий
productionCalibrationSeed из NativeCalibratedState/ModelSpec2: ISI .01/.03,
uniform storage physics, исходные SyncTolerance .02 и CapturedPerInput;
L0=1..3, anchor L1=1, Ns1, Rs0=43..86MΩ, anchor86MΩ. Источник проходит
настоящее native обучение и свежую финальную проверку; сертификат не
подставляется. Без Exact downstream-проверка по-прежнему не выполняется.
N0 сохраняет прежний источник. Калибровка и ожидаемые readout assertions
не ослаблены. Расчёт 20kHz maximumSamples привязан к duration×frequency:
ceil(0.26×f)+20, то есть прежние540 при2000Hz и5220 при20000Hz.

Это другая объявленная постановка transport fixture, а не ретроспективное
исправление измерений исходной .08-серии. Её heterogeneous physics и узкий
домен сохранены как NativeCalibrationPrecondition negative. Добавлены
Classic/Branch negative при20000Hz; прежние2000Hz и ModelSpec2 negatives
сохранены. Нельзя выдавать их BudgetExhausted за PhysicalInfeasible.

Проверка: сначала шесть readout/persistence и шесть negative precondition,
затем общая актуальная матрица. Во всех случаях необходимы реальные
Environment/storage/Calculate, native proof и отсутствие пропусков.
После этого продолжить блокированные calibration ownership fixtures и
полную Linux/Windows матрицу. Успех этого подэтапа не закрывает весь этап8.


Изолированная Linux-проверка запущена: source Root
`6433f59f9e112d3806df7485cbfe5f305c149fc9`, Pulse5f8b281,
`s08-calibration-readout-sdk-m40-a1`. Каноническая подготовка успешно
завершена за158.54с, kernel group отсутствует/закрыта; native build21
подтверждён живым в отдельной группе. Gate21 включает шесть readout/persistence,
шесть старых negative preconditions, два timing-neighbourhood controls и семь
physical DATA tests. Это адресный набор, не полный прежний frozen DATA cohort Linux248/Windows247.

Общий N1 helper также обслуживает четыре NativeThresholdCandidate cases.
Они требуют отдельной последующей проверки на этом же immutable runtime;
планируется восемь candidate cases вместе с четырьмя N0 controls, которые
сохраняют прежний источник. Не считать Gate21 проверкой этих восьми.
Восемь CalibrationOwnership cases требуют ещё и опубликованных grid source
fixtures; их отсутствие не устраняется этим изменением readout source.


Повторная literal inventory проверка выявила, что исходный frozen DATA cohort
248/247 вообще не выбирал NativeCalibrationPrecondition и NativeThresholdCandidate.
Поэтому добавление двух TEST не меняет тот прежний cohort автоматически.
Новый явный [расширенный cohort](ValidationPlans/CalibrationReadoutCompletion-20261118/INVENTORY.json)
содержит262 Linux/261 Windows: прежние248/247 плюс все6 negative preconditions
и все8 threshold candidate cases. Он только объявлен, не выполнен. Прежний
INVENTORY и отрицательный Windows247 сохранены. Обновлённый Windows cohort
потребует сборки исправленного Root643, текущий scientific runtime Root28
не выдаётся за неё. Gate21 M40 остаётся своим неизменным адресным заданием.

## Установленная причина двух отказов

В фактическом полном JUnit Gate21 все assertions двух failed cases относятся
только к Artifact(file.open(WriteOnly|NewOnly)), строка211. ThresholdPotential
и CalibrationPersistence вызывали один и тот же helper с одинаковыми аргументами,
поэтому второй case повторно использовал имена всех файлов первого. Четыре
ThresholdPotential (обе топологии,2k/20k), шесть сохранённых negative preconditions,
семь PhysicalModelData и два timing-neighbourhood контроля прошли. Это не
доказательство дефекта сохранения калибровки; отдельный persistence outcome
всё равно не принят из-за отсутствующих независимых артефактов.

Для persistence добавлен явный suffix `_persistence` в имя rig и всей его
цепочки proof/trial/export файлов. Прежние имена остальных cases сохранены.
NewOnly остаётся обязательным; ошибки теперь сообщают путь и file.errorString.
Проверка должна запускать обе пары readout/persistence **в одном процессе**
и подтверждать наличие обоих наборов, а не запускать их изолированно для
сокрытия коллизии. Ни один файл исходного rejected Gate21 не перезаписывается.
[Полный разбор всех JUnit failures](../../../Reports/StructTrain/TimeLearner/CalibrationReadoutCompletion-20261118/linux21-artifact-collision-diagnosis.json).
