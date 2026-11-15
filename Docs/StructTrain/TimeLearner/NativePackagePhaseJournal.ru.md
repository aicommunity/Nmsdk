# Ограниченный журнал фаз package6

В `Test_PulseLib_CompositeTraining.cpp` добавлен диагностический journal к
существующим production cold/import/reexport/warm путям. Причина — C0
SDK355 завершился OOM после сохранения исходного обученного package, но без
достаточных границ последующих операций. Move-кандидат сам по себе этот OOM
не устранил. Не менять математическую постановку или memory limit ради
получения положительного результата.

При заданном `TIMELEARNER_COMPOSITE_OUTPUT` journal сохраняет маленькие JSON
`package6-phases/<suite>.<case>/source-<variant>/<phase>.json`:

- создание и настройка source fixture;
- начало/возврат штатного training loop;
- live XML capture, export и сохранение source;
- создание destination, начало/возврат import и reexport;
- создание comparison views и возврат сравнения;
- warm Reset/Start, loop, export и Prepare.

В training/warm loops раз в10 wall seconds обновляется один `*-loop-latest`
файл. Число файлов не растёт с числом ticks. Каждая запись создаётся через
`QSaveFile` с atomic commit; повторное обращение к той же фазе заменяет её
последнее наблюдение. Отсутствующий output env сохраняет прежний no-artifact
режим. Невозможность сохранить запрошенную диагностику завершает test error,
не создаёт положительный результат.

Schema1 `native_package6_phase` содержит monotonic wall time, actual model time
из Environment, текущие state/outcome enum codes, наличие certificate и простые
counters. Counts — decimal strings. На Linux self process lifetime peak RSS
получается через getrusage; на других ОС поле null. Это не current RSS и не
пик всей группы процессов. Enum/variant codes интерпретируются с source commit
запуска; они не являются универсальным научным scorer API.

Journal не вызывает Calculate/Build/Reset, graph capture, hashing, export или
EncodeNativeTrainingState. Он не меняет stimulus, scheduler order, модель,
допуски, решения контроллера и существующие asserts. Phase `returned` означает
только возврат вызова; например, import содержит отдельный status_code/reason,
а приёмка остаётся за исходными assertions и полным JUnit.

На момент подготовки серверная компиляция и runtime-проверка нового journal
ещё не выполнены. Предыдущие15 PASS относятся к исходному SDK355 и не являются
его приёмкой. Следующая проверка должна сохранить4GiB C0 profile, реальные
компоненты/полные первичные данные и отрицательный результат при его повторении.
Новые файлы — диагностические observations, не training certificate, scientific
PASS или замена waveform/CSV.
