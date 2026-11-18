# Источник для проверок LT readout и сохранения калибровки

Статус: изменение fixture подготовлено; новый native серверный прогон ещё
не выполнен. Не изменение алгоритма/допусков и не новый научный результат.

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
