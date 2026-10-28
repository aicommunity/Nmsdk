# Проверяемые физические основания N1 domain decisions

Рабочий подэтап `stage07/domain-decision-evidence`, отдельно от проверяемого
controller e875ca5. Численный поиск, CapturedPerInput, допуски и lifecycle не
меняются. Старые full runs не считаются проверкой этой новой сериализации.

## Дефект доказательности

Domain schema 1 содержит готовые a/b и endpoints, но не весь физический preview.
Из такого файла нельзя независимо проверить происхождение проводимостей, C,
трёх R, частоты или shared-bank ownership. Проверка primary trial CSV подтверждает
измерение, но сама по себе не подтверждает derived domain.

## Изменение

`ResistanceDomainAssessment` сохраняет immutable semantic preview model schema 2,
его hash, source amplitude, topology, policy ratio/floor и явный ownership map
синапсов. Storage-образы и live graph не изменяются; preview не рассчитывается.
Контроллер остаётся независимым от Qt: serialized model хранится opaque string.
`EncodeResistanceDomainAssessment` выпускает отдельную domain schema 2 и
используется также внутри training summary; схема самого summary не меняется.

`Scripts/StructTrain/TimeLearner/domain_evidence.py`:

1. Проверяет preview hash, schema, per-input geometry и ownership возбуждения.
2. Читает effective typed child properties и реальные SynapticInputs bindings.
3. Заново считает secretion bound по TC/frequency, Weight, PSI и analog/pulse
   drive; затем a/R+b, averaging и условие fixed-channel strict stability.
4. Считает channel no-crossing lower bounds по фактическим C/R/Rm/Rfb/f,
   policy floor/ratio, shared-bank singleton и сравнивает endpoints и коэффициенты.
5. Отделяет `physics_verified` от обучения и scientific verdict, который всегда
   остаётся null. Roundoff allowance — относительный binary64, без абсолютного
   порога 1 для малых проводимостей и без физического percentage tolerance.

Schema 1 допускается только через явный `--allow-legacy` и возвращает
`physics_verified=false`. Неизвестная схема является ошибкой. Unavailable,
unsupported и failed records не получают физического подтверждения допустимой
области. Доказательство отсутствия области и actual live-vs-preview comparison
остаются отдельными проверками; Python не выдаёт их за выполненные.

## Проверки и ограничения

Используются настоящие Classic/Branch previews и fixed/scaled inhibition,
полученные из production storage fixtures. Corruption controls меняют child C
или связи с пересчитанным semantic hash, a/b, канал, ownership, lock, endpoint,
nonfinite и schema. Проверяются legacy adapter и отсутствие положительного
результата для unavailable. Локально тесты не выполняются; сборка и проверки
разрешены только на двух заданных workers.

Native producer отвечает за поддержку конкретных C++ equations и отсутствие
неподдерживаемых connected parameters. Auditor пересчитывает записанный preview,
но не доказывает происхождение произвольно изготовленного файла и не заменяет
проверку реального графа, build/runtime closure, observations или сертификата.
Результат не означает Exact, PhysicalInfeasible либо распознавание 8/8.

Статус на момент первой фиксации: реализация подготовлена; runtime-проверка
и публикация новых артефактов ещё не выполнены.
