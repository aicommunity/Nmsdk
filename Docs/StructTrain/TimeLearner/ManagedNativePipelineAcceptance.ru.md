# Managed Train → export → frozen Test: normal приёмка

На Elder source `c3445128cd6b62aa9ae0ce1b9e448186a1b4c62c` прошёл **8/8** реальных checks без failures/errors/skips:

- Четыре новых холодных N1 Train: Classic/Branch × ModelSpec1/2. Каждый получил настоящий Exact certificate при исходных допусках; экспорт использовал только результат нового Train. Отдельный frozen Test сохранил полное recognition state и закончил все объявленные пробы.
- Четыре старые декларации Classic/Branch × N0/N1 на этом runtime дают budget_exhausted без completed boundary. Публичный экспорт stopped state как завершённого источника отклонён до создания выходного каталога и запуска нового процесса модели.

Проверены16 отдельных managed native units:12 фаз положительных цепочек и4 stopped Train. Все связаны с точными lease/unit IDs, ядро подтвердило закрытие каждой группы; тестовые schema3 leases released. Глобальный operational reserve освобождён лишь после закрытия controller и всех16 внешних нативных групп. Controller256MiB, native4GiB, aggregate4.25GiB. Это проверка реальной production политики, не только portable self-consistency.

Runtime неизменяемый: root `f679d0410dd00a36995f9d32cc03812438819bb7`, Pulse `541bf89b9966f63ca5131fa57a31a9ae3f5820ea`. Новый Python backend не пересобирал SDK и не менял физику, Rdk lifecycle, допуски или native control flow. Тесты использовали реальные компоненты и публичные CLI-команды. Положительные декларации восстановлены из `s05-model-spec-production-normal-a4`; это прежний двухвходовый engineering LT профиль, не научный stock четырёхвходовый результат.

## Неудачные предшествующие попытки

A1 ошибочно выбрала четыре старые pipeline-декларации как положительные. Они исторически выполнялись на rootd5ef1fa1, а на проверяемом f679 дали stopped/budget_exhausted. Попытка4/4 failed сохранена: экспорт и Test не выполнялись, готовая старая модель не подставлялась. Это несовместимость предпосылок теста, не доказанная регрессия managed backend или физическая недостижимость.

A2 использовала отдельные ранее проверенные Exact N1 seeds, получила четыре настоящих Exact Train, но тест неправильно ожидал run_id запроса без штатного `/session/1`. Четыре положительных проверки остановились на этом assertion; четыре negative controls прошли. В A3 исправлено точное ожидаемое имя первой сессии; параметров обучения это не меняет. Исходные failed verdicts не переписаны. После каждой неудачной попытки свежая проверка всех4/8 external groups и controller разрешила только global lease recovery; диагностические ledgers и журналы сохранены.

## Доказательства и границы

Proof `28f7d2fe6f59232f19b33e5b24f4d4011eddfffb`, accepted parent8b231dae9: [компактные primary и receipts](../../../Reports/StructTrain/TimeLearner/s10-managed-native-pipeline-normal-a3/README.ru.md). Положительный архив4 541 640B, SHA256 `190c22f03a712e040122af8d73e466068ec0f1df41cec3428a99f722d5d025ff`; всего трёх попыток2728 member hashes и283 Python source blobs каждой версии независимо сверены локально по Git. [Машинная сверка](ManagedNativePipelineVerification.json).

Это приёмка данных normal-подэтапа. Implementation branch ещё не продвигается в develop. Положительные N0, актуальный joint SDK, M40 ASan/полная kernel suite62, native calibration/PostTune, interruption/recovery и общий production dispatcher остаются открытыми. Frozen пробы используют объявленную матрицу, independent partition не подтверждён; Exact обучения не означает успешную классификацию. [Графики всех объявленных frozen проб и реальный отрицательный классификационный итог](ManagedNativePipelineVisuals.ru.md) теперь опубликованы; полный кэш остаётся на M40. Этапы1–12 остаются частичными.
