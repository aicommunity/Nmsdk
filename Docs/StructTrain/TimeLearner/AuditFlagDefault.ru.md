# EnableTrainingAudit: явный Default и штатный reuse

Актуально 28.10: оба A3 full runs завершились успешно; исправление включено
в PulseLib develop merge `caf19a343b62e96c5076e84b6c4c2710114128bc`.
Подробности и ограничения: [PooledFullAcceptance](PooledFullAcceptance.ru.md).
Промежуточный readback «процессы живы» ниже относится ко времени до завершения.

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

## Адресная приёмка исправленной версии

Root `7fb92a4a57b9773ff56996cf2c7b8c75b2746cd8`:

| Worker / вариант | Lifecycle | UContainer | Ограничение |
|---|---|---|---|
| Elder-1, обычная сборка, A2 | 8/8 pass | 18/18 pass | Полный CTest — отдельный gate |
| M40, обычная сборка, A2 | 8/8 pass | 18/18 pass | То же |
| M40, ASan fixed-A1 | 8/8 pass | 18/18 pass | detect_leaks=0; не проверка отсутствия всех утечек |

Нет failures/errors/skips в этих адресных группах. Проверены сами native
components/property assignment/Default/Build/Reset/Return→Take, а не копия тела
функции. Исходный baseline сохраняет по одному Default failure на класс.

Git evidence: Elder-1 `663623949851db3a953191c81a036be9c96f9728`,
M40 `2a13c3fbbcc680370f8fd65ec02b3b6d617befd5`; каталоги
`Reports/StructTrain/TimeLearner/s04-audit-default-elder1` и `-m40`.
Локально проверены 41 stored SHA и 37 raw payloads.

После адресных A2 checks полный CTest не стартовал из-за ошибки построения shell
command: JS replacement интерпретировал dollar-quote и повредил filter quote.
Ошибочная команда также исказила имя неиспользуемого parallel hint CMake;
фактические build calls явно задавали -j2/-j1. Эти preparation failures сохранены;
они не являются ни ошибками научного эксперимента, ни полным PASS.

Новые полные прогоны `s05-pooled-full-a3` работают с теми же проверенными
immutable A2 binaries/runtime и новыми output directories. Их manifests явно
фиксируют reuse build. На момент readback три быстрые suites прошли, PulseLib
процессы живы; terminal verdict ещё нет. Предыдущие A1 остаются
interrupted_by_user. Исправление ещё не принято в develop; весь этап 4/5 открыт.
