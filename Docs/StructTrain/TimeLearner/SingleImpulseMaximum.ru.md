# Выбор наибольшего пика одиночной пробы: кандидат этапа7

Реализация находится в отдельной ветке `codex/timelearner-impulse-maximum`,
созданной от develop с merge предшествующей SDK feature. Серверная приёмка
нового кода ещё не выполнена. ASan storage SDK8702 относится к прежнему коду.

Добавлена явная native ProbeSpec schema5, `single_impulse_maximum`. Она
разрешена только в диагностическом предъявлении ровно одного импульса.
Закрытое окно, реальные timestamps, baseline и revision обязательны.

```text
require complete finite window and exactly one actual declared impulse
find the highest measured peak after window closure
retain the count of all positive local maxima as a diagnostic
if largest peak is clipped: Clipped
if distinct highest peaks tie: Ambiguous
otherwise preserve measured amplitude, timestamp and plateau endpoints
if peak precedes actual impulse: invalidate response, retain the signed delay
```

Контроллер и scheduler не рассчитываются вложенно, физика между A/B не меняется.
Используется штатный single-pulse native путь; Return/Take, storage profiles и
целевой паттерн не подменяются изменениями на каждом тике. Native ProbeSpec
schema4 и её IsolatedWindow остаются неизменными по смыслу.

В Python `prepare_single_pulse_job` имеет opt-in `peak_selection` с прежним
default `isolated_window`. Console выбирает schema5 только при явном новом
значении; burst с этой политикой отвергается до модели. Независимый reader
проверяет максимум по raw samples и запрещает скрывать peak до фактического
onset. Чтение schema4 сохраняет прежний критерий, schema/policy relabel
отвергается. Результаты по-прежнему diagnostic_only/training_eligible=false.

## Область и незакрытые требования

Этот шаг не заменяет обучение штатной пачкой. Одиночная проба предъявляет
первый source impulse выбранному физическому входу; это не доказательство
реакции на закреплённый pulse i внутри Train. Общая принадлежность волн при
наложении остаётся открытой. Ни одна старая InvalidObservation не становится
Exact из-за введения новой схемы. CapturedReferences и FinalVerification
диагностическую schema5 отвергают, даже если её максимум корректно измерен.

Предусмотрены семь recorder controls и пять native tests: две топологии,
2000/20000Гц, A/B полной waveform и возврат физики при prepared/sample/final
sample faults. Положительный native A/B использует явно объявленный высокий
порог100; это инженерный контроль измерителя, не смена default и не научный
результат на stock threshold. Архивные low-threshold многопиковые ответы
обязаны пройти отдельный Console replay и визуальный анализ.

План адресного normal gate на Elder: прежние26 storage/prepared controls +
12 новых =38 native;19 прежних readers +5 новых =24 без skips. После него
нужны ASan нового кода, Console replay и общая training assignment приёмка.
Локально разрешены только Git/AST/schema/hash metadata проверки.
