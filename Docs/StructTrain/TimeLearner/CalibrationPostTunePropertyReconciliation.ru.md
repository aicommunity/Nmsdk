# Сверка 44 calibration/PostTune записей, 08.11.2026

Исправлены текущие статусы 22 свойств каждого learner в
[PropertyReview.json](PropertyReview.json). Прежняя общая фраза «new native
calibration/PostTune not implemented» больше не описывает текущий SDK.
Она сохранена в `historical_review_status` вместе с прежним `factor_scope` и
исходным `source_commit`; первоначальные evidence и acceptance не переписаны.

Это сверка каталога и consumers, а не новые runtime-проверки. База root:
`9a782e211a7321b2253dacb018d2235a67b8a445`; её точный PulseLib gitlink:
`fcc3fed0dc63fc0d8ae8dcfdb0f85bd5d004baf8`. Полный [реестр соответствий](CalibrationPostTunePropertyReconciliation.json)
содержит для всех 44 записей before/after, роль public property, владельца native
фазы и отдельный support snapshot. Для 157 source references указаны полный
commit, Git blob, filepath:line, строки и SHA256 нормализованного excerpt.

## Три независимых статуса

1. **Public legacy property.** Наличие свойства, его сохранение и setter сами
   по себе не означают применение соответствующего фактора в native Train.
   Setter может непосредственно менять физику; это требует собственного
   контроля и не объявляется безопасным только по наличию typed API.
2. **Typed native phase.** NativePostTuneTransaction и
   NativeThresholdCalibrationTransaction реализованы. Live hooks также
   реализованы; configured вход с EnablePostTrainTuning=true допускается при
   заранее установленном согласованном NativeLiveFinalizationSpec.
3. **Support snapshot.** Наличие реализации не повышает runtime acceptance
   всех public properties, способов назначения, моделей и режимов. Для всех
   44 записей он остаётся partial; новые numerical runs отсутствуют.

## Отображение public properties

| Свойства обоих learner | Текущий владелец и граница поддержки |
|---|---|
| LTZThreshold, FixedLTZThreshold, UseFixedLTZThreshold | В native recognition — зеркала effective threshold проверенного package/hold. Public assignment не устанавливает подтверждённую калибровку. |
| TrainingLTZThreshold | Legacy training threshold; не определяет native threshold grid и не заменяет ModelSpec. |
| AutoCalibrateFixedLTZThreshold | Старый target-reference режим в configured/live пути должен быть false. Реализованная typed grid calibration не является поддержкой этого режима. |
| CalibrateLTZThresholdMode/Fraction/Min/Max | Старые формула и clamps; native grid/trials задаются отдельной явной декларацией. |
| CalibratedFixedLTZThreshold | Диагностическое зеркало. Ноль допустим как настоящий calibrated threshold и как значение без подтверждения; статус берётся из package/hold. |
| EnablePostTrainTuning | Условный запрос live finalization; при отсутствии согласованного runtime plan прежний отказ сохраняется. XML одного ControllerConfiguration не восстанавливает plan. |
| PostTrainTipResistanceMode, PostTrainMidMetric, EnablePostTrainMidThreshold | Public enums/flag проверяются относительно typed mode/metric/finalization. Это не blanket support всех сочетаний. |
| TipResistanceCanonFloor | Проверяется для CanonRmin/SearchSynthetic относительно canonicalFloor. |
| TipResistanceCanonLast | Проверяется для FlatLastR относительно canonicalLast. |
| PostTrainSilentThreshold | Проверяется, когда typed weightProbeThreshold явно присутствует. Не подменяет grid finalization. |
| PostTrainTipSearchIters | Проверяется относительно searchPasses для SearchSynthetic. |
| UseCandidateMidOnNonSeparableTest | Legacy Test-time fallback в live finalization должен быть false; native calibration не разрешает скрытый подбор на Test. |
| PostTrainSyntheticFoilCount | Legacy cap. Реальный native design объявляет trials и budgets явно; сохранённое число не доказывает предъявление этих patterns. |
| PostTrainTuneComplete, PostTuneResult | Legacy diagnostics; не заменяют typed Report/Execution, validity, Exact или recognition verdict. |

Точные источники в PulseLib fcc3fed:

- `Core/TimeLearner/ConfiguredNativeOwner.h:9` — admission с/без live plan.
- `Core/TimeLearner/NativeLiveFinalization.h:43` — public controls и ограничения;
  `:118` — вход в native conversion/PostTune после реального Train boundary.
- `Core/TimeLearner/NativeLearnerLifecycle.h:19` — native BeforeTick dispatch.
- `Core/TimeLearner/NativePostTuneTransaction.h:6` и
  `Core/TimeLearner/NativeThresholdCalibrationTransaction.h:31` — отдельные typed API.
- `Core/TimeLearner/NativeRecognitionOwner.h:44` — threshold mirrors и смысл нуля.

Имеющиеся scoped runtime receipts остаются в
[CalibrationPropertyContracts](CalibrationPropertyContracts.ru.md),
[NativeLiveFinalization](NativeLiveFinalization.ru.md),
[NativePostTuneController](NativePostTuneController.ru.md) и
[NativeThresholdCalibration](NativeThresholdCalibration.ru.md).
Их compiled revisions не заменены текущим fcc commit. Эта сверка не выполняет
новую проверку каждого архива и не переносит старые runtime verdicts на весь SDK.

## Проверка изменения

[Машинный receipt](CalibrationPostTunePropertyReconciliation.validation.json)
проверяет 211→211 исходных записей, ровно 44 изменённые и 167 неизменённых;
шесть новых configured declarations учитываются отдельным прежним каталогом.
Возврат historical runtime/factor fields и удаление двух новых metadata fields
восстанавливает каждый исходный выбранный record полностью на уровне JSON values.
Все 157 excerpts сверены с immutable Git objects PulseLib fcc3fed; текущих
stale runtime statuses осталось 0, исторических сохранено 44.

Это завершает только указанную reconciliation. Отдельные source findings о
public setters и внешнем training flag находятся в
[PropertyOwnershipReviewFindings-20261108](PropertyOwnershipReviewFindings-20261108.ru.md).
Они не исправлены этим изменением; support, mode/lifecycle matrix и этапы 1/4/7
не объявляются завершёнными.
