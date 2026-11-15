# Classic N4/N1: конечный опыт с recovery budget16

## Вопрос и граница опыта

В предыдущем full-domain запуске после четырёх разрешённых восстановлений пятый ambiguous завершил поиск: [исходный результат](../M40ObservationDomainTrainA1-20261112/RESULT.ru.md). Проверяем, позволяет ли бюджет16 найти допустимые кандидаты дальше, сохраняя назначение пика закреплённому импульсу. Неоднозначный/отсутствующий пик не становится valid. Это один заранее ограниченный cold Train, без автоматического расширения серии.

## Источники и единственный изменяемый фактор

- SDKRoot448b153f2fea3486ff40f3a626b8f1110b9e3ee2, Pulse7b524b8d6c760c5ecfeea432b14b5f9d5045987d, controller/source7bd3684732e1d3f7a0aa038d659fd52bc95892bf.
- [Восемь свежих cold probes](../M40CurrentFullDomainCold8A2-20261112/RESULT.ru.md) на этом runtime; production prepare проверил valid/complete observations, initial graph и provenance. Из них штатно получены cold7, затем full-domain cold8.
- В Classic job изменён только search.maximum_invalid_observations:4→16; job заново подписан, ConditionSpec пересоздан production-сериализатором, index обновлён. Подготовленный Branch job сохраняется в штатной двухтопологической схеме, но здесь не запускается.
- CapturedPerInput, anchor3, 2000Hz, N4/N1, исходная пачка, физика storage без LTMembrane, amplitude_absolute1e-5/relative0, minimum_amplitude1e-6, SyncTolerance0.02 сохраняются. C-trim/PostTune/calibration выключены. Full-domain candidate window0..3600 frames.
- Относительно прежнего full-domain опыта текущий SDK содержит оптимизацию export/evidence; это не побайтно тот же runtime. Поэтому сравнение маркируется как последовательный опыт, а не строго идентичное бинарное A/B.

## Конечные ограничения и исполнение

Search:128 probes,1280 edits,128 candidates/input,4 sweeps; model budget7200s, search wall1800s. После16 разрешённых восстановлений следующий отказ завершает обучение. Native finalization allowance300s; outer job3600s,2GiB controller memory,128 tasks,2GiB output и минимум2GiB свободно. Дочерний native process получает штатные ограничения production runner.

Задание s07-full-domain-budget16-train-m40-a1 на M40 выполняет существующий StockObservationDomainTrainTest только для Classic. Он запускает native preflight, cold Train, проверяет physical/model package и фактический полный domain каждого измеренного candidate. Ни модель, ни порог не подменяются шаблоном.

## Что считать результатом

После терминального состояния сохранить learning outcome отдельно от execution/validity, число поисковых и физических проб, реально измеренные L/Rs, временные/амплитудные остатки, причины missing/ambiguous и свежую финальную проверку входов, если алгоритм до неё дошёл. Предоставить читаемый отчёт с временными графиками сомы и фактических входов для ключевых решений; при полученном пригодном learned state — отдельный frozen Test всех паттернов с полными окнами.

InvalidObservation/BudgetExhausted/SearchUnresolved являются допустимыми научными исходами, но не доказательством PhysicalInfeasible или успешной классификации. Если17-й отказ снова остановит поиск, не увеличивать бюджет автоматически: разобрать измеренные решения и адресно пересмотреть правило поиска/назначения. Новые общие framework-проверки и новая сборка для этого опыта не требуются.

[Точный prepared plan](prepared/index.json), [request](request.json), [Git-источник подготовки](preparation-origin.json).
