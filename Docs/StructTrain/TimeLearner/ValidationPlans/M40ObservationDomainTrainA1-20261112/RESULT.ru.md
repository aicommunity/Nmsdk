# Полный домен N4: Classic проверен, Branch timeout — закрытый A1

Оба unittest cases выполнены: **Classic PASS, Branch FAIL**, общий cohort failed.
[Исходный log](completed/worker/validation/unittest.log), [результат](completed/worker/validation/result.json).
Source/tool f71bb4dd411922f28b3a5e419b6ffcc1184641a3; native SDK8362/Pulse111,
runtime61f3e2f0. Отсутствие общего PASS не скрывается результатом Classic.

| Случай | Выполнение | Валидность | Обучение | Итоговая геометрия |
|---|---|---|---|---|
| Classic |completed|valid|invalid_observation: rejected_candidate_window:ambiguous|L45,1,1,1; Ns1; Rs86MΩ|
| Branch |timeout1920s|unverified_execution|неизвестно: итоговый пакет отсутствует|финальный граф не подтверждён|

Classic:42 logical groups,252 native probes,907452 sampled frames;38 search
probes/18 edits. [Аудит пакета и физики](completed/worker/native-full-domain/Classic-stock-cold8-N1/index.json),
[summary8](completed/worker/native-full-domain/Classic-stock-cold8-N1/runs/train/native/train_stopped_summary.json.xz).
Сертификата/Exact нет. Новый derived test проверил фактические candidate frames:
полный записанный домен0..hard_last, без перемещения окна при изменении модели;
исходные reference capture windows сохранялись. Все влияющие physics checks
прошли. Это runtime-проверка применения окна, а не сходимости.

Пять recovery deliveries Classic относятся к ambiguous при L54,52,50,48,45:
четыре cursor_advanced и один invalid_budget_stop. Не следует называть это
пятью успешными восстановлениями или доказанной PhysicalInfeasible. Rs не
были неизменяемым фактором: в valid evidence есть проба Rs≈2.8800716MΩ при
L1, хотя конечный диагностический граф имеет Rs86MΩ. Границы входов0–2:
L1..100/Rs1M..86M; anchor3 зафиксирован L1/Rs86M.

Branch закрылся по процессному лимиту во время ExportNativeLearnedState,
записав652 raw trial CSV и packet JSON. Полного state/summary/execution нет,
поэтому нельзя вычислять training outcome по имени файла или давать обычный
Test как обученной модели. [Точный разбор](../../ObservationDomainFinalizationTimeout-20261112.ru.md).
Отдельная [Branch A2](../M40ObservationDomainBranchFinalizeA2-20261112/RESULT.ru.md)
с900s финализации относится к другой попытке и не исправляет статус этого A1.

Whole cohort закрыт; [controller/leases](completed/closure-and-reservation.json)
фиксируют released, heartbeat_errors отсутствуют. Снимки actor/source/fixtures
до и после побайтно совпали. [SHA256 raw readbacks](completed/readback-integrity.json).
Полные первичные данные/модель [опубликованы компактным corpus](../M40ObservationDomainCombinedClosedCorpusA3-20261112/RESULT.ru.md),
[независимый DATA replay принят2/2](../M40ObservationDomainPrimaryIndependentA1-20261112/RESULT.ru.md);
[Подробный temporal разбор ambiguous завершён позднее](../../ClassicFullDomainAssignmentScientificReport-20261112.ru.md): извлечены причины всех5 отказов, построены full/omission графики групп12/14/42,3 выбранных изображения просмотрены. Это анализ того же закрытого опыта, без нового Train и без смены его результата.
Test, калибровка и classification verdict не выполнялись. Этапы1–12 не закрыты.
