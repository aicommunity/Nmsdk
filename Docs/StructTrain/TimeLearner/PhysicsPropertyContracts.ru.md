# Семантика исходных свойств: C-trim, overrides и торможение

Code review PulseLib `025d809f7b86cc79e18ddd711c6adc40e2396bf8`:
**35 исходных записей**. Все fields ниже ptPubParameter без setter, кроме
отдельно указанных state flags. Штатное сохранение XML/Copy не подтверждает
effective child physics и не восстанавливает скрытые trim/search histories.

## Optional C-trim: восемь свойств обоих классов

| Свойство | Тип/default/единицы | Legacy consumer и ограничения |
|---|---|---|
| SyncCapacitanceTrim | int, 0 | Значение>0 включает trim и повторное ApplyDendriteCapacitances после Build/relink; любой positive int ведёт себя как On. Native training сейчас отклоняет >0. База нового алгоритма должна завершаться честно при Off |
| SyncCapTrimTolerance | double, 0.0005 секунды | При abs(arrival error)<=tolerance trim не делается. Не заменяет SyncTolerance и не подтверждает законченный timing certificate |
| SyncCapTrimMaxRel | double, 0.3; относительное отклонение C/C0 | Consumer max(0,configured) задаёт C0*(1±max_rel). Finite/range setter отсутствует; нужны допустимость обеих границ и фактический clamp |
| SyncCapTrimMinTau | double, 0.00075 секунды | Legacy lower C bound выводится из tau_floor=max(configured,dt*1.000001) и одной effective membrane resistance. Это локальное правило не является полной проверкой численного интегратора, суммарных conductances/PSI/Ns |
| SyncCapTrimGain | double, 0.8; безразмерный | Consumer использует >0 gain, иначе 1; положительные >1 не отвергаются. Коррекция C_old+gain*timing_error/interval_length/R. Требуются finite и ограничение шага |
| SyncCapTrimMaxSteps | int, 8 | Ограничение попыток на dendrite/pulse; попытка увеличивает скрытый CapTrimSteps даже если C не изменилось. При <=0 попытки блокируются сравнением. Не путать с SyncCapTrimCount |
| DendriteCapacitance | vector<double>, пустой; Фарады; **ptParameter|ptState** | Classic ck пишется всем ExcChannel/InhChannel сегментов соответствующего пути. Branch ck пишется интервалу max(1,L[k+1])+1..L[k] общего кабеля. Empty/<=0 legacy entries пропускаются или заполняются scalar C0 при trim |
| SyncCapTrimCount | int, 0; **ptPubState** | Число фактических изменённых C, а не всех попыток. Reset/cold reset очищают; сам по себе не хранит временные ошибки, revisions или стабильность |

ClassCapacitance обоих learner читает только положительный Neuron.MembraneCapacity,
иначе возвращает 0. Он не вычисляет исходные capacities heterogeneous children.
ApplyDendriteCapacitances заменяет Exc и Inh capacities одним ck; такая процедура
не сохраняет исходную неоднородность. Classic legacy инвалидирует timing
изменённого input, Branch — соответствующего pulse; новый общий кабель требует
консервативной invalidation всех затронутых наблюдений и fresh final sweep.

Новый trim обязан хранить per-segment baseline эффективных каналов, применять
разрешённый scale, проверять каждый канал и conductance/integrator после edit,
сохранять roundtrip. Подстановка 1nF при отсутствующем parent C запрещена:
legacy PostTune Branch reconstruction — отдельный незакрытый риск, не часть
валидного storage-owned import. До такой реализации V2 On не поддерживается.

## Пять parent overrides обоих классов

| Свойство | Default/единицы | Фактическая область применения |
|---|---|---|
| OverrideMembraneCapacity | double, 0 Ф | Legacy ApplyNeuronClassOverrides пишет Neuron.MembraneCapacity до Build |
| OverrideExcMembraneResistance | double, 0 Ом | То же для Neuron.ExcMembraneResistance |
| OverrideInhMembraneResistance | double, 0 Ом | То же для Neuron.InhMembraneResistance |
| OverrideExcSynapseResistance | double, 0 Ом | То же для Neuron.ExcSynapseResistance |
| OverrideInhSynapseResistance | double, 0 Ом | То же для Neuron.InhSynapseResistance |

В legacy helper только value>0 переписывает parent default, <=0 оставляет прежнее.
Эффект зависит от UseElementDefaults и штатной структурной настройки нейрона:
parent numbers не доказывают параметры LTMembrane/каждого child. Функция
ApplyElementDefaultsToMembrane применяется локально, чтобы не стирать Rs других
входов; общий ApplyElementDefaults способен перезаписать все синапсы.

Native CheckNativeOwnerOverrides требует **все пять ==0**, в том числе отвергает
отрицательные legacy placeholders; ненулевые значения дают
native_model_requires_images_instead_of_parent_overrides. Для новой uniform
physics использовать отдельный immutable storage profile и цепочку
channel/synapse → membrane → neuron, затем readback всего графа. Нельзя менять
общий prototype работающих экземпляров или компенсировать его каждый тик.

Проверки: effective child params/response после fresh Take, reuse, Copy, XML,
Build/growth и full archive; коллизии имён profiles; сохранение heterogeneous
physics и learned individual Rs; частота и производные synapse coefficients.
Существующие StorageProfiles/NativeModelBuilder/ModelArchive cases покрывают
части, но не всю матрицу исторических overrides.

## Торможение: общие свойства и Branch override

| Свойство | Тип/default | Реальные consumers и ограничения |
|---|---|---|
| EnableNextSegmentInhibition | bool, false | Legacy создаёт InhSynapse1 в L+1, добавляет headroom и связывает с тем же stimulus. Branch mute должен учитывать Exc и Inh. В комбинации с SegEI при delta==1 NextSeg link пропускается, чтобы не дублировать один узел |
| EnableSegExcInh | bool, false | Legacy создаёт Inh в attach+delta и задаёт сопротивление через alpha. Требует actual synapse class, inhibitory type, cable extent и связи; включение bool без реальной связи не доказывает вмешательство |
| SegExcInhDelta | int, 8; сегменты | Consumers ограничивают delta снизу 1. Значение1 совпадает с NextSeg; нельзя анализировать комбинацию как два независимых inhibitory contacts без graph readback |
| SegExcInhAlpha | double, 1.0; безразмерный | InhResistance=ExcTipRs/max(alpha,1e-12) с фактическими topology-specific clamps; <=0 не эквивалентно явному отключению свойства. NaN/Inf не отсекаются setter |
| Branch NextSegInhResistance | double, 0 Ом | При >0 заменяет NextSeg inhibitory Rs через ClampResistance; иначе берётся SynapseResistanceBase/fallback. Не применяется к произвольным SegEI contacts или PSI kinetics |

Native ModelSpec.editPolicy хранит явные inhibition entries и scaling policy;
legacy parent flags не должны подменять их. При совпадающих Branch attach points
нужно проверять реальное множество contacts и routes, а не N×ожидаемое число.
PSI включается физическими profiles синапсов и не является отдельным learner
switch из этой таблицы. Полная inhibition matrix и вмешательства остаются
приёмкой этапов 7/8/11, независимо от наличия полей в XML.

## Источники и обязательная доказательность

Прочитаны ClassCapacitance, ApplyDendriteCapacitances, TrimSyncCapacitances/
TrimSyncCapacitanceForPulse, DelayLenOf, defaults/reset/CapApplyPending;
NNeuronTimeLearnerScopedDefaults.h и вызовы ApplyNeuronClassOverrides;
Ensure/RelinkNextSeg/SegExcInh/WireAllInh и headroom logic обоих learner;
NativeModelOwner/NativeModelBuilder/NativeModelEditor/ConfiguredNativeOwner.
Подтверждены code findings и ограничения; они не объявляются общей runtime
неработоспособностью старых экспериментов. Исторические результаты сохраняют
свои физические версии и протоколы.
