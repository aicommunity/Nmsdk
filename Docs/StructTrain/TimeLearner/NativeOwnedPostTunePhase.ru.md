# PostTune как фаза native owner

Статус: реализация опубликована в feature-ветке; серверная приёмка продолжается.
Это подэтап 8, а не завершение этапа или автоматического Train → Test.

## Область действия

Оба learner предоставляют BeginNativePostTunePhase(spec, implementationId),
NativePostTunePhaseDone(), NativePostTunePhaseReport(),
NativePostTunePhaseExecution() и CancelNativePostTunePhase(reason).
На входе требуется установленная, Ready/Init Recognition-модель без ошибки
модели и без другой незавершённой фазы. Существующая транзакция принимает только
поддерживаемое исходное состояние; параметры и наблюдения проверяются её общим
production-путём. Частота всего поддерева owner должна совпадать и быть ненулевой.
Multirate не объявляется поддержанным этим контуром.

Begin пока вызывается явно. Автоматический выбор момента перехода из живого
Train, преобразование Solo → Recognition и построение полной спецификации по
публичным настройкам остаются отдельной незавершённой интеграцией. Ограничители
неподдерживаемых configured optional modes не сняты.

## Порядок выполнения

```text
owner BeforeCalculate:
    if phase exists and is running:
        retain phase across native child replacement
        enter internal lifecycle scope
        phase consumes prior completed observation
        phase queues trial or installs next model through native import
        close administrative request if transaction became terminal
    validate recognition hold
    prepare queued native trial before first stimulus

native scheduler:
    refresh actual child list after BeforeCalculate
    calculate children in normal order

owner AfterCalculate:
    collect actual native trial observation
```

Внутренний код не вызывает Calculate модели. Транзакция может вызвать штатные
Build/Init/Reset при установке кандидата между пробами. Собственный depth scope
отличает эти действия от внешнего прерывания; число внутренних событий записывается
в execution receipt. NativeLifecycleDepth и NativePostTunePhaseDepth имеют разный
смысл и не подменяют друг друга.

Внешние Construct/Adopt/Import и управление recognition trials блокируются во
время активной фазы. Это не блокирует законные внутренние действия транзакции.
Параметры физики по-прежнему применяются через существующие storage/import пути.

## Завершение и прерывание

Done означает любой терминальный исход существующей транзакции. WeightsSelected,
Calibrated, SearchUnresolved, BudgetExhausted, Cancelled, Failed и RecoveryRequired
остаются различными результатами. Закрытие запроса не создаёт сертификата обучения,
успешной калибровки или распознавания.

При CalculateMode=0 локальный, не подключённый IsNeedToTrain снимается напрямую
как административное завершение. Реальный внешний источник не изменяется.
При CalculateMode=1 запрос остаётся под внешним управлением. После закрытия Need
может быть снят без изменения выбранной модели; исходные controls/bindings остаются
в immutable boundary. Остальные изменения controls по-прежнему запрещены.

Внешний Reset/UnInit/Default или разрушение owner прерывают активную транзакцию
без попытки импорта в разрушаемое дерево. Состояние RecoveryRequired не обещает
восстановления исходной модели. Cancel является отдельным явным действием и
использует существующий guarded rollback. Default удаляет фазу; Reset сохраняет
диагностический report. Контрольная точка посреди пробы не поддерживается.

## Доказательства и оставшаяся проверка

Новый native набор содержит восемь completed сценариев Classic/Branch ×
CalculateMode0/1 × local/connected и два внешних Reset. Внешних Advance в этих
сценариях нет. Проверяются запрет конкурирующих действий, внутренние lifecycle
события, завершение запроса, сохранение controls и модели после снятия Need.
Он запускается вместе с 65 адресными регрессиями предыдущего контура: всего 75.
До терминальных receipts и публикации это runtime-unverified.

Две начальные обычные попытки выявили ошибки подготовки replay fixtures:
публичное Need=true начинало новое обучение, а frozen import правомерно заменял
локальные mirrors. Production-контракты для исправления тестов не ослаблялись.
Третья обычная попытка остановлена preflight из-за свободного места до checkout.
Удалены только 56 GNU ar файлов неиспользуемых owned runtime-каталогов:
601710782 байта, 14 ELF файлов сохранили SHA-256. Receipt сохраняется в readbacks.
Исторические primary не удалялись. Устаревший ASan тест отменён штатным pidfd
runner, а ожидавший его следующий supervisor остановлен до checkout. Нулевой
EXIT-trap status такого supervisor не является успешным выполнением native gate.

Независимый reader owned_posttune_evidence проверяет исходные Train primary,
finalization boundary, controls/bindings, временную последовательность и все
полные измеренные матрицы. JSON receipt не удостоверяет сам по себе запуск native
scheduler: process/runtime receipts и C++ integration tests требуются отдельно.
Для каждого из десяти records предусмотрены десять corrupt-data controls.

render_owned_posttune использует общий renderer с managed финализацией. Полные
матрицы показывают все паттерны и каналы сомы, реальные входы и временные
увеличения без прореживания. Неполные активные матрицы сохраняются первичными
данными и не выдаются за полные реакции. Полные рисунки хранятся как кэш M40;
Git получает компактные primary, metadata и выбранные рисунки. Визуальная
приёмка и научный результат остаются отдельными от автоматических проверок.

Не закрыты этим подэтапом: автоматический dispatcher, live Train handoff,
полная матрица физики/режимов/частот, independent Test, внешний UnInit/Cancel и
неоднородная частота как отдельные отрицательные runtime controls. Цель плана
0–12 сохраняется полностью.


## Production Console: следующий подэтап, проверки ещё не выполнены

Console PostTune переводится с внешнего Advance на BeginNativePostTunePhase и
обычные тики outer model. Standalone calibration сохраняет существующий driver.
Новый PostTune execution schema2 сохраняет прежние поля и добавляет четвёртый
артефакт phase-execution.json; подписанный execution связывает его hash/размер.
Reader сохраняет schema1 compatibility, проверяет все полные матрицы и дополнительно
связывает число before-children вызовов с model_ticks, частотой и begin/end времени.
Нулевой tick допустим только при явно связанном нулевом интервале отменённого job.
Это production replay Recognition, а не автоматический handoff живого Train.
Серверные build/18-mode Console corpus и re-signed corrupted-receipt checks пока
не выполнены; наличие кода не считается подтверждением.


Проверка Console выявила отдельную ошибку orchestration: при запуске всего
модуля NativeCalibrationRunProvenanceTest сортировался до класса, создающего
его два настоящих CLI runs, и без отдельного env был skipped. Fail-closed gate
остановился, хотя 26 операций и 15 остальных checks прошли. Новый maintained
owned_posttune_worker_checks выполняет явные классы в порядке 4+3+8+4, задаёт
все paths и сохраняет typed результаты после каждой группы. Provenance checks
не запускаются до появления реальных CLI probes. Любой skip запрещает успех.
Начальный skip сохраняется; исправление setup не меняет код моделей и не
превращает неудачную попытку в успешную.
