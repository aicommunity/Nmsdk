# Исправление actual raw delivery composite service

Статус: подготовлен исходный код, требуется проверка родительским агентом,
серверная сборка и выполнение матрицы. Локальных численных запусков нет.

Основание: Elder A3 Root `6dacdb3d4fb3245649aba3a5d69ba8f83f611c8e` /
Pulse `f925e37247bb987980fce80da47831a1c31d04c9` выполнил 12 checks и остановился
на `ClassicPreparedStopHasSingleRawResult`: actual closed=0 при expected=1.
Negative evidence `90af73022c3c0955eaafa368ef5a7e00702147b1` сохраняется.
Ожидание не ослаблено, алгоритм выбора максимумов/окон и допуски не изменены.

Исправление Pulse `1ac4be9d6583120c3229bda7036a9c6a72f20c05` разделяет
сохранение фактического packet и application notification. Включены capture
до validation, собственный run/trial cancel guard, cursor текущей группы,
exactly-once staged service delivery после внутренних изменений, lifecycle и
generation guards после callbacks, защита callable/actor lifetime, реальное
wall time перед consume/certificate. Подробности в
[документе PulseLib](../../../Libraries/Nmsdk-PulseLib/Docs/TimeLearner/CompositeRawCancellationDelivery.ru.md).

[Точный inventory](CompositeCancellationDeliveryGateInventory.json) содержит
старые **206** IDs и **24** новых Classic/Branch checks: cancellation sink
throw/reset/default/retarget/recursive stop, warm без исторического replay,
normal sink throw/reset, фактическая порча физики с доставкой raw packet,
реальная задержка sink, destructor без callback, устаревший actor против новой
отдельной пробы. Всего **230** обязательных cases; compiled gtest inventory
необходимо сверить до запуска. Старые cohort inventories остаются описаниями
своих сохранённых снимков; новое полное задание использует этот inventory.

Slow-sink checks обоих типов используют реальный steady clock и 16-секундный
sleep последнего полного raw callback при объявленном 15-секундном wall budget.
Они обязаны войти в callback реальной Completed пробы и закончиться
BudgetExhausted без references/certificate; early timeout до callback не PASS.

Порядок приёмки: source review → scoped server build → старый prepared-stop
и новые callback/lifetime controls → все 230 → actual6 archive exports →
независимый Python replay и legacy C0 graph controls. Будущие package5/Console
и новые candidate-window bridge ветки в этот исходный снимок не подмешаны.
Пока source не принят, существующие серверные runtime/source не обновляются.
