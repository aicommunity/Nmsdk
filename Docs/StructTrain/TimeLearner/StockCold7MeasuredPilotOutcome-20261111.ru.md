# Stock N4/N1: исходы measured-window cold Train — 11.11.2026

Это первые два ограниченных cold Train после восьми fresh stock-проб. Нового успешного классификатора нет; Test не запускался. Оба исхода и все закрытия сохранены раздельно.

| Топология | Выполнение | Валидность | Обучение | Состояние |
|---|---|---|---|---|
|Classic|timeout после1800.337s native wall; controller1824.707s|unverified_execution|не установлено|702 raw observations; финальный package отсутствует|
|Branch|completed,1700.819s native/2143.846s controller|valid|budget_exhausted: maximum_probes_exhausted|Остановленный diagnostic package, без сертификата|

SDK `22e9714bbe66d29a661bb6829e1c992f24fc1362`, Pulse `165d49da7e65cd6ac59bca2812ce52884ddd50c2`; управляющий Python `8eb6efbfba4ffbcda8f06aac7f3dd54c11e0e119`. Профиль NSPNeuronGen без LT-мембраны; N4,2000Hz,N1, CapturePerInput (математическая цель CapturedPerInput), anchor3 с неизменяемым Rs. Amplitude absolute1e-5,relative0,minimum1e-6,SyncTolerance0.02; C-trim/PostTune/calibration Off. [Полная постановка](StockCold7Pilot-20261111.ru.md). Предсказание29frames/segment задавало candidate-window, не подтверждало пик или сходимость.

Branch:4 reference+128 search logical groups,792 native probes,2851992 samples,116633100 retained primary bytes,64 edits. Все группы заново проверены production package reader по первичным traces; публичный exact=null, certificate отсутствует. Последний граф: attach lengths[3,3,2,1], Rs[86M,86M,65956354.083223864,86M]Ω. Проверены4мембраны/8каналов; LT-мембраны нет, threshold и feedback connections сохранены. Все native/controller groups закрыты, обе managed leases released.

[Classic execution и исходный FAIL](ValidationPlans/M40StockCold7ClassicTrainA2-20261111/actual-result.json), [Branch execution, physical/package audit и PASS записи отрицательного исхода](ValidationPlans/M40StockCold7BranchTrainA2-20261111/actual-result.json). PASS здесь означает достоверный завершённый запуск и честную запись исчерпанного бюджета, а не сходимость или классификацию. Portable reader не восстанавливает живую process authority; исходное выполнение подтверждают отдельные сохранённые native/controller записи.

## Ограничение поиска, которое теперь воспроизведено

[Фактическая история](ValidationPlans/M40StockCold7BranchTrainA2-20261111/search-history-diagnostic.json):64 уникальных candidate physics, все для input2; повторов одинаковой физики не обнаружено. После начальных L1/L2/shared-bank вариантов поиск остался на L2 и перебирал Rs. У последних12 кандидатов timing residual примерно−0.231s, существенно вне0.02s, пока amplitude residual оставался вне1e-5. Это не доказательство физической невозможности.

Source review Pulse165 `Core/TimeLearner/BoundedTraining.cpp`, `NextDomainCandidate`: выдача одного Rs и переход к следующей geometry включены только при `invalidMeasurementRecovery==AdvanceUnassignedBurst`. Фактический runtime выбрал `retry_same_candidate`; при валидных наблюдениях это оставляет полный Rs-grid одной geometry впереди других длин. `PrioritizeMeasuredLength` не прерывает уже открытый N1 domain; `ProposeMeasuredResistanceRefinement` требует measured points withinTiming. Вместе эти решения допускают расход всего конечного бюджета на амплитудную нормализацию заведомо несинхронной длины. Принадлежность пиков сама по себе в этой истории не была причиной остановки.

Следующее адресное изменение этапа7:

1. Отделить обход geometry/Rs от политики восстановления invalid observation. При валидных пробах режим retry не должен сам по себе лишать остальные длины доли бюджета.
2. Ввести ограниченный fair обход legal geometry, сохранив native per-geometry Rs-domain reassessment, допустимые attach orders, индивидуальные bounds, deduplication и свежие paired anchor измерения.
3. Проверять временной остаток до дорогого уточнения Rs; measured length proposals остаются предложениями. Не предполагать общей монотонности, не переносить bracket между разными полными background physics/C0/source profiles.
4. Прямые production C++ проверки: retry/advance при одинаковых valid observations исследуют последующие legal lengths до исчерпания локального Rs-grid; locked/shared Branch banks и unavailable domain не создают illegal edits; invalid peak policy остаётся прежней; ни один stall не становится PhysicalInfeasible.
5. Затем native A/B на одинаковых fresh stock условиях и budget; отдельно измерить стоимость model revision checks/primary audit. Один SIGTERM stack с IdentifyModel не устанавливает причину медленного расчёта. Не увеличивать tolerance или менять CapturedPerInput ради PASS.

Полная compact primary публикация этих двух Train и адресные waveform-отчёты пока открыты. Успешные августовские4/8–6/8 относятся к исходному историческому протоколу и данным не отменяются. Все этапы1–12 остаются частичными.
