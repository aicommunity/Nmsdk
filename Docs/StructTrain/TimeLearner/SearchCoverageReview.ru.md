# Покрытие поиска stock recovery: отдельный аудит

Добавлен production search_coverage.py и команда:
`python -m Scripts.StructTrain.TimeLearner stock-recovery-study coverage STUDY --output NEW.json`.
Сначала выполняется прежний полный native study audit, включая raw probes/CSV,
и только затем строится сводка. Она не подменяет финальную проверку сходимости.

Каждый measured CandidateEvidence и typed recovery event группируется по
candidate-input, всему вектору L и Ns. Сохраняются реально встреченные Rs,
trial IDs, отдельно measured input/controlled input, число валидно измеренных
кандидатов и typed unassigned observations. Rejected entries без полного
parameter witness не получают выдуманную геометрию из конечной модели.
Legacy summary1 не сообщает общего invalid counter: в отчёте он unknown,
а не пересчитанное Rejected.size(). Producer counter schema5 не выдаётся
за независимо пересчитанный счётчик всех отказов.

Code review Pulse416: BoundedTrainingSession::NextCandidate перечисляет длины
при фиксированном normalizer, а NextDomainCandidate перечисляет все Rs одной
assessed geometry до AdvanceDomainGeometry. Это различные порядки; для native
N1 с индивидуальными dynamic bounds действует второй. AssessedDomain строит
Rs из исходного значения, low/high и log mesh subdivision4, до17 значений.
Measured length proposal переставляет будущую длину по валидным measurements;
невидимый/неоднозначный пик не используется как измеренная задержка.

Предварительная сверка текущих stock summaries показала: Classic low advance
потратил33 invalid observations на две геометрии L1/L2 с17 различными Rs
каждая;32 recovery transitions разрешены, следующий отказ останавливает Train.
Classic high сначала имел по17 measured candidates для L1/2/3, затем proposals
L54/L52 дали missing waves и исчерпание invalid allowance. Полный search box
L1..100 не исследован. Это ограничение покрытия в объявленном бюджете,
не доказанная ошибка расчёта и не PhysicalInfeasible.

Перед возможным изменением очередности нужны подтверждённая сводка primary и
отдельные A/B checks. Рассматриваемая гипотеза: fair interleaving нескольких
assessed geometries вместо всех Rs первой geometry. Нельзя вычёркивать Rs из
неудачной geometry: сопротивление само может изменить wave assignment. Каждый
возврат требует fresh domain assessment/эффективных bounds, а deduplication
должна включать normalized physics scope и C-context. Общий invalid budget,
referenceN−1, captured targets и fresh final gate остаются прежними. До этих
проверок изменение default поиска не реализуется и положительный эффект не
обещается. Этот документ не переименовывает честный budget stop в algorithm bug.

Подготовлены4 проверки на всех восьми реальных completed-execution Train
пакетах: полная сумма свидетельств, invariance гистограммы к порядку строк,
unknown legacy charge и запрет duplicate/relabelled trial. Исходные модели
не пересчитываются; серверная проверка нового coverage reader ещё ожидается.


M40 job s07-search-coverage-a1 запущен с source9cb944fd58ad90a286900d2c991440065001c1c7.
Owner1228078/start306980048 подтверждён живым; tests/CLI verdict ещё ожидается.
[Снимок задания](SearchCoverageJobs.json) не доказывает его состояние после
времени наблюдения. C++ порядок поиска этим подэтапом не изменён.
