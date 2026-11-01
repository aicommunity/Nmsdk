# Native-проверка конечности временных параметров

Этот подэтап исправляет PARAM-FINITE-001 из
[семантического review](ParameterSearchContracts.ru.md).

На Elder исходный root `c9e82b7a4aabda5d4eca2d06cd60b14a23082f1c` с PulseLib
`70f467d3b66ea4defdec2f58b84e76b692ab3602` воспроизвёл проблему:4/4 gtests
завершились failure без skips/errors. Каждый case проверяет реальный storage
TakeObject, обычное UProperty::SetData, возврат в storage и повторное получение.
Частоты2000/20000 Гц; обе topology; пять свойств на topology; NaN/±Inf.
Из120 неконечных назначений84 были приняты: по20 на Classic case и22 на Branch
case. Исключение отсутствовало и прежнее конечное значение было потеряно.
Это воспроизведение property-path, а не гипотеза о поведении XML parser.

Исправление PulseLib `ecf35a6c322f58fc9c4ffdfb998bf882f990252a` добавляет
isfinite в четыре общих timing setters, Classic EstDelayPerSeg и новый setter
Branch InitEstDelayPerSeg. Конечные домены сохраняются: margins/gap >=0,
Classic estimate >0, Branch seed может быть <=0 для прежнего fallback.
В тесте отдельно проверяются эти различия и сохранность прежнего значения
при EPropertySetterFail. Не используются копии функций или unsafe casts.

Исправление пока в feature-ветке; normal/ASan проверки и публикация primary
evidence ещё не приняты. Baseline process_error с returncode1 сохраняется.
Нельзя считать четыре неуспешных gtests успешным gate.

SetDataDirect и connected/external supplier следуют Rdk; они не покрыты
утверждением об отказе обычного локального setter. Build/Reset/Calculate
данным изменением не исправляются. LIFECYCLE-BOOL-001 остаётся открытым.
V2 tolerances/windows имеют отдельного владельца — ControllerConfiguration.
Полные этапы1/4/6/7/9 остаются частичными; научный verdict отсутствует.
