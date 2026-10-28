# EnableTrainingAudit: явный Default и штатный reuse

## Подтверждение исходного дефекта

M40, `s04-audit-default-baseline-a1`, root
`bde7032a2af0fe2c670453809f0baa50d25f7cd6`, PulseLib
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`, Rdk
`1223bcc18cf1ba106e8f8a17f20cce8c000c104d`.

Штатный Test_PulseLib_StorageComponents под ASan выполнил два новых native
TimeLearnerNativeLifecycle cases: ClassicAuditFlagDefaultAndReuse и
BranchAuditFlagDefaultAndReuse. Оба завершились с одним ожидаемым failure:
явный learner Default не восстанавливал fresh EnableTrainingAudit=false.
Перед Default в обоих случаях обычные Build/Reset сохранили явно включённый
audit, как и должны для параметра конфигурации.

**Return→Take через штатный образ в этих случаях уже восстанавливал false.**
Соответствующие assertions не отказали. Это уточняет предварительный code
finding: нельзя приписывать stock storage reuse тот же воспроизведённый сбой,
который обнаружен при прямом Default. При reuse применяется class image.

SSH transport оборвался во время сборки; после восстановления связи job был
проверен по тем же output paths. Сборка не перезапускалась. Terminal test exit=1,
XML tests=2/failures=2/errors=0 и validation сохранены на worker. Это не ошибка
доступности теста и не результат обучения/распознавания.

## Исправление

PulseLib `4919bac2bd359118b13310862e54bcd24492967d` явно задаёт
EnableTrainingAudit=false в ADefault обоих learner рядом с EnableDebug=false.
Свойство остаётся ptPubParameter с тем же именем и типом. Обычные Build/Reset
не переопределяют явную настройку; XML/class image по-прежнему может её задать.
Общий Rdk Default/Copy/Take контракт не меняется. Физические параметры,
математическая цель и численные допуски не изменены.

Runtime-приёмка исправленной версии ещё предстоит: все native lifecycle controls
под ASan и обычная сборка, затем повторные full maintained suites в новых runtime.
Предыдущие s05-pooled-full-a1 остаются interrupted_by_user. Никакого PASS им
задним числом не присваивается. Исправление ещё не принято в develop.
