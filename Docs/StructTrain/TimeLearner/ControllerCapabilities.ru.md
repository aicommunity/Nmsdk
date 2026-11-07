# Возможности TimeLearner: принятый код и проверяемый кандидат

Сверка07.11.2026. Этот документ отделяет реализованный и объединённый код от
последующего кандидата; он не является полной приёмкой режимов или научным отчётом.

Принятый PulseLib develop: `0ec9193e6620ae2439329eece5ecd6d6f167c70a`.
Проверяемый compiled SDK: Pulse `8f057e69f489ab3eddd5e7f889404b779a85e93e`,
root `36f598524b08ef9a5b72e26e50ef1f34501331e2`; normal137/137 и адресный
ASan38/38 приняты на M40. Docs-only Pulse `2f6b57253bd7ae380a19320ef3835a2701cb4d30`
имеет тот же Core. Это ещё не общий merge C++ в develop.
[Normal137](FairDomainTraversalNormal137Verification.json),
[ASan38](FairDomainTraversalAsan38Verification.json).

SDK2e061/Pulse12d и [сверка20 blobs](ControllerCapabilityReconciliation.json)
относятся к предыдущему срезу; их source hashes не подставляются новому SDK.
Native recovery уже исполнен в двух полных восьмиусловных stock Train сериях,
с production primary/CSV audits и публикацией данных. Все попытки остановлены
InvalidObservation, без certificate; native execution proof не означает
доказанной сходимости. [Последнее парное сравнение](FairDomainStockTrainVerification.json).

| Возможность | Принятый develop | Проверяемый кандидат / остающиеся ограничения |
|---|---|---|
| Совместимость старых конфигов | ControllerVersion по умолчанию1; V2 включается явно | Полная legacy/V2 A/B и multirate матрица открыты |
| Повторы N0 | Реализованы, адресно приняты; default1, schema2 задаёт>=2; N1 отвергает N0-only repeats | Это повторы измерения кандидата, не независимые случайные обучения; final repeatability и полная физическая матрица открыты |
| Порядок поиска N0 | Измеренная timing-ready геометрия может предложить соседние Ns; fresh исходные допуски сохраняются | Не гарантирует сходимости произвольной физической модели, не равен старому quantization tracker |
| Измеренный поиск L и Rs | Есть bounded measured proposal helpers и обычный ограниченный перебор | Локальный bracket не доказывает глобальной монотонности/PhysicalInfeasible |
| Полный learned-state перенос | Completed/stopped native packages, архив графа/storage и boundary restore реализованы; есть адресные проверки | Stopped не получает сертификата и Test как обученная модель; mid-probe checkpoint не обещается; вся matrix не закрыта |
| C₀ / разрешённые поправки C | Есть physical baseline/edit, owned correction и schema2 learned transfer | Наличие API не доказывает всю owner/growth/physics матрицу |
| Автоматический bounded C-search | В принятом BoundedTrainingConfig отсутствует | В кандидате отдельные TrainingCapacitance/MeasuredCapacitanceSearch и cold schema4; общий срез ещё не объединён |
| Legacy SyncCapacitanceTrim>0 в native Train | Отклоняется | Отклоняется и в кандидате. Новый C-search включается декларацией, а не этим legacy-полем |
| PostTune/calibration | Есть typed фазовые планы, native import/transactions и адресные runtime controls | Public legacy flags не заменяют план; все режимы/прерывания/независимая оценка остаются открытыми |
| Общее управление lifecycle | Общий native service уже есть; часть hooks ещё дублируется | NativeLearnerLifecycle и NativeRecognitionControl выделены в кандидате; полная совместимость не следует из механического выделения |
| Общий invalid budget попытки | Полная приёмка всей области остаётся открытой | Адресные проверки общего бюджета, journal/serializer и actual stock invalid-budget stops опубликованы; весь scope и все final/reset сочетания ещё не закрыты |
| Неидентифицируемая пачка | Старые конфигурации сохраняют retry/явную остановку | Opt-in AdvanceUnassignedBurst и fair traversal прошли адресные controls и actual stock Train/audit; все8 новых Train invalid, без сертификата, вся физическая матрица открыта |

## Версии схем — разные оси

- `ControllerVersion=1/2` — выбор компонента управления, а не версия архива.
- Cold `ControllerConfiguration` schema1/2 поддерживаются принятым кодом;
  schema2 задаёт повторные измерения N0.
- В кандидате cold schema3 добавляет capacitance_history, schema4 —
  capacitance_search. Эти поля не являются legacy SyncCapTrim* properties.
- Feature cold/summary schema5 объявляет recovery поверх base1..4; это не
  ControllerVersion5. Reader mutation checks60/60 на обоих серверах используют
 18-cell historical корпус; отдельно исполнены реальные schema5 native Train
  и их полные audits в stock сериях. Ни то, ни другое не доказывает все
  сочетания C-search/PostTune/reset или завершение обучения. Старые1..4
  сохраняют прежний retry.
- ModelSpec1/2 — версии физической декларации; одинаковая модель в двух
  сериализациях не является двумя независимыми экспериментами.
- Completed/stopped package schema2 с capacitance_state — перенос C₀;
  это не cold schema2 и само по себе не включение bounded C-search.
- Production job, observation, scorer и runtime manifest имеют собственные
  версии; ни одна из них не подменяет model identity или trial completeness.

## Откуда взялись уточнения статуса

[N0 repeats](N0CandidateRepeats.ru.md) и [порядок кандидатов](N0CandidateOrdering.ru.md)
имеют опубликованные адресные приёмки. Соответствующий repeat merge и fix
boundary summaries являются ancestors принятого PulseLib; первоначальные слова
«пока не объединён» больше не являются текущим статусом этих подэтапов.

[Learned-state API](NativeLearnedState.ru.md), [repeat boundary](RepeatBoundaryState.ru.md)
и [C₀ transfer](CapacitanceStateTransfer.ru.md) реализованы позднее первоначальной
постановки ModelArchive/Configured controller. Cold marker удерживает неверный
путь загрузки, но не означает отсутствия отдельного полного native import.

Для кандидата уже приняты [normal304](SharedSdkNormal304Acceptance.ru.md),
[normal8+133](IntegratedSdkResults-2026-11-05.ru.md),
[ASan build/focused8](SharedSdkASanFocusedAcceptance.ru.md) и
[сквозной инженерный coordinator](IntegratedCoordinatorAcceptance.ru.md).
[ASan lifecycle133 принят](IntegratedSharedAsan133Verification.json) для
SDK2e/Pulse12d. Он не подтверждает последующие изменения recovery/fair traversal;
для нового SDK отдельно принят ASan38 в указанной области, без leak check.
Старый isolated ASan304 относится к SDK802. Реальные исходные manifests
сохраняются; merge SHA не подставляется задним числом.

Новые эксперименты должны сохранять точный root/child/runtime и действующего
владельца каждого параметра. Успех загрузки UProperty не доказывает влияние
фактора: например, legacy IterationGap не задаёт V2 протокол, а SynapseClassName
не заменяет выбор реальных storage-образов. Полный production factor preflight
остаётся открытым. Все исходные этапы1–12 частичны;8/8 не условие рефакторинга.


### Проверка public readers — 06.11.2026

Source5a6dd77dedca3595087570fa4153cff3c78309fe прошёл60/60 Python checks
без пропусков на M40 и Elder. Корпус:18 случаев base1..4,312 файлов;
хеши сверены с исходными архивами в Git. Schema5 envelopes в этой проверке
добавлены к копиям исторических данных: native выполнение нового recovery
и полный pipeline этим не подтверждаются. Elder A1 завершился по120с timeout
с неизвестным числом выполненных тестов и потерянным stdout; A2 с неизменными
тестами и бюджетом900с прошёл за142.07с.
[Подтверждение и точные commits](CandidateRecoveryApiVerification.json).
