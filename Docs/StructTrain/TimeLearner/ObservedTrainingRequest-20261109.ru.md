# Наблюдённый повторный запрос IsNeedToTrain

Статус: **source candidate, не runtime acceptance**. Pulse768ff93c5b02796783a59f69ffcdbfa3fe0ed892 основан на C0 holder candidate f1; оба изменения требуют фактической приёмки. Работающие SDK22ac на M40 и4eb на Windows не меняются и не содержат этого нового исправления.

PROPERTY-CONTROL-RISING-001: локальный setter при V2 false→true переводил service в Idle, а connected GetData и SetDataDirect обходили setter. После внешней остановки Finished service не проходил configured autostart predicate. Rdk property implementation не изменяется: Attach/SetPointer остаётся connected-read, не ExternalDataSource writable alias.

## Управляющий контракт

Общий NativeLearnerLifecycle читает request в штатном BeforeCalculate после обработки recognition/finalization phases. Service хранит только transient `observedTrainingRequestLow`; этот флаг не является параметром модели, storage profile или обученным состоянием. Фактически прочитанный false взводит запрос. Постоянный true не создаёт новой сессии; false→true между чтениями без наблюдения false не обещается как обнаруженный переход.

```text
observe request at native owner boundary:
    false: arm an observed-low request; leave active cancellation to native service
    true with no observed-low: do nothing
    true while Idle: disarm; existing configured autostart handles the request
    true while active / physical boundary unavailable / raw delivery pending:
        retain the armed request
    true after Finished at a closed physical boundary with raw notifications drained:
        ResetControl, clear old request intent and reset probe control
        let existing configured autostart begin the next session
```

Общий BeforeCalculate применяется к обоим learner только при ControllerVersion2 и отсутствии NativeEditFailure. Native scheduler рассчитывает children штатно, вложенных Calculate/Reset/Build не добавлено. Existing local setter semantics и явный BeginNativeTraining сохраняются. Никакой общий prototype, порог, C/R, dataset или training target на каждом tick не переписывается. Build/Calculate/Reset продолжают возвращать true; исключение управляющего пути отражается typed InvalidModel diagnostic.

ResetControl/InvalidateTarget снимают transient latch; freshly restored controller не наследует незавершённый input edge. ResetControl сохраняет первоначальные references/family/C0/историю в рамках существующего контракта. Перед новым Start последний certificate остаётся только историческими DATA. Прежняя raw cancellation должна быть полностью собрана до reset; пустая notification queue, нулевая dispatch depth и edit boundary проверяются дополнительно к Finished. Несовместимая конфигурация по-прежнему требует Build. Возможность активации реального ExternalDataSource у этого свойства ещё не доказана и тестами через SetPointer не имитируется.

## Проверки кандидата

В production integration TU добавлены13 cases NativeObservedRequest: один guard test настоящего service; Classic/Branch × connected/direct × CalculateMode0/1; четыре stop-on-first-sample/restart controls. Используются реальные storage profiles, configured cold7, model scheduler и реальные probes. Проверяются отсутствие бесконечного restart при постоянном true, unobserved ABA, новый session number, сохранение исходных source/family/capture epoch, targets после полного capture, байтов первого raw trial и продолжение после частичной отмены. Off не должен создавать C0. Пакеты cold/stopped/warm и request-boundary.json сохраняются через production serializers.

Эти13 cases пока **не собраны и не выполнены**. Перед приёмкой нужны также C0 present/asymmetric, lifecycle Reset/Default/import/retarget, raw callback reentrancy/authority regressions и полный native119 на согласованной версии. Один guard test и source review не заменяют runtime матрицу. Кандидат не закрывает export/import mismatch, scorer16, Console Train→Test, scientific N4 или весь этап6/7.
