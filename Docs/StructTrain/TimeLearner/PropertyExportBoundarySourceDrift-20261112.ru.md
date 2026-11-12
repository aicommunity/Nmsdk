# Свойства и lifecycle после shared export boundary

Source-only сверка Pulse7b524b8d6c760c5ecfeea432b14b5f9d5045987d фактического предыдущего SDK с Pulsedfb9a98244f91b4f4029d8470465fd40116436ca нового SDK. Использован существующий production property_drift parser, читающий immutable Git blobs; компоненты локально не запускались.

[Полная квитанция217 регистраций](PropertyExportBoundarySourceDrift-20261112.json) не выявила добавленных/удалённых UProperty или изменений type/flags/registered_name/setter body/default mentions. Это ограниченная feature-delta: исходные reviewed211 и6 новых configured declarations не получают новой runtime-приёмки автоматически.

[Сверка методов](PropertyExportBoundaryMethodDelta-20261112.json) подтвердила неизменность18 lifecycle-related bodies Classic и20 Branch (имена Default/Reset/Build/Init/Calculate и производные). Из ранее существовавших методов обоих компонентов изменён только ExportNativeLearnedStateWithCapacitance; добавлены имена ExportNativeLearnedBoundary и NativeLiveTrainingSummary. Новые API не являются UProperty и не меняют число зарегистрированных параметров.

Общая новая логика находится в export/finalization helpers и Console caller: фабрика возвращает model+summary из одной проверенной границы; finalization удерживает source summary; Console сохраняет модель до последующих артефактов. [Контракт и конкретный дефект](RecoverySummaryExportTimeout-20261112.ru.md) сохраняют самостоятельный проверяющий summary API, native storage/import, отдельность модели/динамики и конечный execution manifest. Не вводятся новые проверки bool Build/Calculate/Reset, nested Calculate, uniform per-tick записи или мутация общего storage prototype.

Границы: равенство slices не доказывает effective child values, connected-property semantics, поведение меняющихся common helpers либо полную mode/physics/lifecycle matrix. Inherited Rdk properties сюда не включены. Реальные [M40](ValidationPlans/M40SharedExportBoundarySdkA1-20261112/STATUS.ru.md) и [Elder](ValidationPlans/ElderSharedExportBoundarySdkA2-20261112/STATUS.ru.md) SDK102 ещё выполняются; результаты не заменяются source-анализом. Старые runtime receipts относятся к своим snapshots и сохраняются.

До полностью актуального semantic/runtime реестра остаётся сверка более ранних helper/consumer изменений между историческим reviewed baseline и Pulse7b, inherited properties, active reference/search/recognition controls, effective-factor matrix и полная история экспериментов. Этап1 и исходный план целиком не закрыты.
