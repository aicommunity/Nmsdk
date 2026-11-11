# Настоящий строгий N4/N1 cold8 Train — закрытый cohort12.11.2026

**2/2 инженерных проверок PASS**:оба реальных cold Train процесса completed/0, native группы закрыты; production package/primary/physics audit принят для каждого. **Обе training outcome invalid_observation**, reason rejected_candidate_window:missing, certificate=null. Это не сходимость, не валидный отрицательный результат классификации и не PhysicalInfeasible. Калибровка/Test не выполнялись.

| Case | Logical groups | Native probes | Samples | Search probes | Edits | Final L | Native wall,s |
|---|---:|---:|---:|---:|---:|---|---:|
| Classic-stock-cold8-N1 | 24 | 144 | 518544 | 20 | 9 | 7,1,1,1 | 778.70 |
| Branch-stock-cold8-N1 | 28 | 168 | 604968 | 24 | 11 | 7,7,7,1 | 403.24 |

Все Ns1/Rs86MΩ; CapturedPerInput/anchorN−1, SyncTolerance0.02, amplitude abs1e-5/relative0,2000Hz и stock Gen physics без LTMembrane сохранены. References captured fresh; исходный cold graph каждого Train точно совпал с объявленным stock identity. Данные технического N2/Sync0.2 пилота не использовались для обучения.

У каждой модели5recovery deliveries:четыре cursor_advanced, затем invalid_budget_stop при invalid4→5. Delivery count не равен числу успешных восстановлений. Отсутствующий assigned peak не заменялся общим максимумом пачки. [Точные конечные поля и hashes](closed-outcomes.json).

[Suite result](completed/worker/validation/result.json), [unittest](completed/worker/validation/unittest.log), [outer execution](completed/controller-result.json), [closure/released lease](completed/closure-and-reservation.json). Source/tool/fixtures before/after побайтно одинаковы, heartbeat_errors пуст. [SHA256 сырых readbacks](completed/readback-integrity.json). Все5outer/native units закрыты. Начальный INTERIM относится к ещё выполнявшемуся Classic и не заменяет этот финальный статус.

Полный первичный corpus (1167files/473097215bytes) включён в [декларацию collection](../M40StockCold8ClosedCorpusA1-20261112/README.ru.md); создание/публикация XZ ещё не приняты на момент этого отчёта. Содержит оба stopped model states, source7/summary8/execution5, все raw/omission observations и decision/recovery ledger.

Следующий шаг — независимый geometry replay исходного/полного окна и временные графики всех controls для настоящих rejected groups. Они должны различить промах proposal window и реальную потерю/слияние assigned peak; никакое post-hoc расширение не создаёт Train certificate. Подготовлен [source7 diagnostic/report gate](../../RecoveryN4DiagnosticReplayPreparation-20261112.ru.md). Полный исходный план1–12 и научная матрица не завершены.
