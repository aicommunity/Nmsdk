# Native PostTune: измерительный контроллер

Рабочая реализация `NativePostTuneTransaction<Owner>` добавлена отдельно от
механического выделения guards. До серверных gates ниже она не принята.
Этап 8 и исходный план 0–12 остаются открытыми.

Контроллер действует между native ticks и не вызывает Calculate. Он принимает
полностью импортированную исходную recognition-модель с conversion spec schema 1.
Для каждого кандидата заново выводит полную модель из immutable solo и исходного
conversion spec, применяя typed PostTune edit. Никакой реконструкции с fallback C,
изменения storage prototype, повторного parallel scaling или XML-overlay нет.

Алгоритм:

```text
validate source model, complete labelled trial design, metric and budgets
create initial candidate:
  Off/KeepDone: inherited recognition Rs
  CanonRmin: declared floor except last, declared last on reference input
  FlatLastR: declared last on all inputs
  SearchSynthetic: same declared canonical seed
for each allowed proposal:
  derive candidate privately; reject illegal physics with an explicit reason
  deduplicate actual effective model identity after individual clipping
  import candidate through native lifecycle at an idle boundary
  present the entire declared target/foil matrix in its declared order
  validate every actual observation against its independent request
  gap = minimum(target trial peaks) - maximum(foil trial peaks)
  keep the best actually measured gap; ties retain the earlier candidate
  for SearchSynthetic propose coordinate factors 0.5, 1, 2 from the best measured
    effective Rs; default 12 passes, declared proposal/recording limits
if no measured gap exceeds declared minimum:
  restore the complete original recognition state
  return SearchUnresolved or BudgetExhausted, never PhysicalInfeasible
otherwise:
  rebuild the selected candidate from its immutable archive
  execute the existing real threshold grid and fresh confirmation
  commit the resulting native calibrated state only on confirmed success
  otherwise restore the complete original recognition state
```

Metric Auto означает LTZone.Potential для Classic и одновременную сумму
фактических соматических потенциалов для Branch. LTZone и SomaSum можно выбрать
явно. Максимум начинается с −∞, не с нулевого rest state. Все значения должны
быть конечны, окна — полны; отсутствующий пик/данные не заменяются прогнозом.
Это измерения полных пачек, не single-pulse characterization.

Положительный gap — лишь основание проверить выбранные веса калибровкой.
Кандидаты измеряются при реальном действующем пороге; новый порог затем
проверяется физическими прогонами с его собственным обратным влиянием на динамику.
Никакого offline threshold sweep по единственному spiking CSV нет. Успешная
калибровка не повышает исходный training outcome до Exact и не доказывает
разделимость независимой матрицы. Полный weight-search и threshold-grid provenance
хранится в transaction report; schema-1 calibrated package не объявляется
доказательством оптимального выбора по всей истории.

Typed fixed-mode candidates сохраняются как раньше. Для управления полным поиском
введён отдельный `NativePostTuneControllerMode::SearchSynthetic`; его нельзя
смешивать с `NativePostTuneMode::SearchSyntheticCandidate`, означающим один
неизмеренный вектор в model archive.

Передача управления threshold-контроллеру использует общий guarded scope:
обновления lifecycle/context после разрешённых native imports видят оба уровня.
Проверяется соответствие owner и implementation ID. Отмена родителя отменяет
только собственную пробу или поручает отмену дочернему контроллеру. Чужой trial,
Reset, смена частоты/clock или идентичный внешний import не дают права откатывать
чужое состояние: результат RecoveryRequired сохраняет его для явного восстановления.

Лимиты: максимум 4096 предложений и 128 passes; default 256 предложений и 12 passes.
Дубликаты/отклонённые предложения расходуют proposal budget, не считаются
независимыми опытами. Default stored-sample budget 2 млн ограничивает weight
observations и заранее проверяет верхнюю границу grid+fresh-confirmation.
Исчерпание proposal budget отдельно записывается даже при подтверждении лучшего
из уже измеренных кандидатов. Это не заявление об оптимальности решения.

Первая normal попытка root c1895c4b / PulseLib bdcc762 завершилась с двумя
отказами новых test cases при восьми прошедших ownership regressions. Ложное
`calibration_observation_budget` возникало из-за использования разрешённого
`maximumSamples=1 000 000` как ожидаемого размера каждой короткой пробы.
Исправление ограничивает размер физическим числом native ticks:
`min(maximumSamples, ceil(duration * frequency) + 2)` для каждой пробы. Частота
дерева едина; +2 учитывает обе границы и один запасной тик закрытия. Request cap,
модель, длительности, допуски и критерии не меняются. Реальный слишком малый
sample budget по-прежнему завершает поиск честным BudgetExhausted. Отдельно
проверяются форма N×1 и возможность менять порог до первого физического прогона.

Адресная native fixture использует настоящие Classic/Branch N1/2000 Гц и все пять
режимов, реальную калибровку, silent-grid rollback, recording budget, отмену до
и после передачи управления и отказ от отмены чужой пробы. Все raw observations
записываются в report. Сначала должны пройти отдельные scope A/B grid/ownership
gates; их первый запуск пропустил восемь ownership cases из-за отсутствующей
fixture-переменной и не считается 10/10. Recovery сохраняет фактические два
grid-контроля и выполняет восемь ownership controls отдельно на обоих binaries.

Открыты: серверная приёмка этого контроллера, независимый report auditor и полные
временные графики, Console/learner public dispatch и параметрический codec,
continuation с уже завершённого PostTune/calibrated checkpoint, вся матрица
N0/N1/частот/размерностей/физических профилей/общих attach positions и научная
серия. Отказ от nested PostTune source сейчас явный; поддержку continuation нельзя
считать реализованной только из-за существования model export/import.
