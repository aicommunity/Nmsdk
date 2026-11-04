# Актуальность каталога свойств TimeLearner

Состояние: статическая сверка выполнена локально по неизменяемым Git blobs;
серверное повторение utility пока ожидает восстановления связи. Это не новая
численная/runtime-приёмка. Действующий источник сравнения — принятый PulseLib
`456a5abdb0ff36a218b25943f7f2c6f9c2175190`, исходный обзор —
`025d809f7b86cc79e18ddd711c6adc40e2396bf8`.

## Что уже было сделано

PropertyReview.json содержит semantic catalog всех211 исходных деклараций;
ещё6 configured declarations описаны отдельно. Поэтому неверно трактовать
каждую из211 записей как заново неразобранную. Ранее выполненные дополнительные
10 control и18 search/timing reviews дают более точные anchors/owners и runtime
ограничения, а не заменяют отсутствующий основной каталог.

[Машинная сверка](PropertySourceDrift.json) хранит оба снимка:217 declarations,
типы/flags, external registration names, setter registration/body hashes,
ADefault source mentions и точные строки. Для каждого файла записаны full commit,
Git blob и SHA256. [Метаданные воспроизведения](PropertySourceDrift.validation.json)
явно исключают runtime и автоматическое semantic equivalence attestation.

```text
python3 -m Scripts.StructTrain.TimeLearner.property_drift \
  --pulselib PATH_TO_PULSELIB \
  --before 025d809f7b86cc79e18ddd711c6adc40e2396bf8 \
  --after 456a5abdb0ff36a218b25943f7f2c6f9c2175190 --output NEW.json
```

Utility читает Git objects и не требует checkout старого дерева. Она не создаёт
компоненты и не вызывает Build/Reset/Calculate. Отсутствующий registration,
неразбираемая declaration либо неоднозначный setter запрещают результат;
обычные перегруженные методы, например ClampResistance, не выбираются за setter.
Нельзя использовать эту проверку вместо полного compiler/parser или runtime.

## Действительные изменения property slices

Типы, flags и registration names всех217 деклараций совпали. Для201 записи
совпали также исследованные registration/setter/default slices. Это утверждение
о конкретных source slices: общие helpers и consumers могли измениться.
16 записей имеют прямые изменения:

| Записи | Изменение | Актуальный контракт/доказательства |
|---|---|---|
| EnableTrainingAudit, оба класса | ADefault теперь явно восстанавливает false. Это исправляет прямой Default после true; нельзя приписывать storage reuse тот же исходный failure | [AuditFlagDefault](AuditFlagDefault.ru.md), [PooledFullAcceptance](PooledFullAcceptance.ru.md) |
| IterationGap, SyncTolerance, PeakMeasureMargin, DelayAgreeMarginMin, оба класса | Локальные setter дополнительно отвергают NaN/Inf, прежние конечные диапазоны сохранены | [TimingFiniteValidation](TimingFiniteValidation.ru.md):120 rejected/preserved assignments на каждом worker,4 property/21 regression tests |
| Classic EstDelayPerSeg; Branch InitEstDelayPerSeg | Classic сохраняет >0 и теперь finite; Branch получил finite-only setter, конечные <=0 остаются fallback | Тот же адресно принятый finite контроль; seed Branch не равен динамическому Classic property |
| IsNeedToTrain, оба класса | Frozen recognition отвергает true; Native V2 owned false→true очищает immutable request intent вместе с transient control; Native false означает external stop | [ParameterControlContracts](ParameterControlContracts.ru.md), [NativeLiveFinalization](NativeLiveFinalization.ru.md) |
| InputPattern, оба класса | Retarget дополнительно очищает request intent до invalidation/cancel/new-plan failure | [TimingAndTargetPropertyContracts](TimingAndTargetPropertyContracts.ru.md); cold declaration не превращается в новый согласованный план автоматически |

SetData может пропустить setter при равенстве значения; connected/external
properties и SetDataDirect имеют собственный Rdk путь. Поэтому finite setter
не является доказательством проверки всех способов изменения параметра.
Не вводится новый смысл возвращаемых lifecycle bool: публичные Build/Reset/
Calculate не становятся протоколом ошибок обучения.

## Изменившиеся consumers и lifecycle

Только сравнение setter body не описывает следующие изменения, проверенные
в исходниках отдельно и отражённые в поддерживаемых документах:

- Graph aliases после Load/Copy разрешаются по окончательным именам через
  BindLegacyGraphRoles; readout dimensions и rest-state публикуются после
  штатного сброса физических детей. [LoadedLearnerReadout](LoadedLearnerReadout.ru.md),
  [HotLearnerReset](HotLearnerReset.ru.md), [HotXmlReset](HotXmlReset.ru.md).
- Frozen recognition, owned PostTune и live finalization подключены к native
  Before/After-children hooks. CalculateMode0 завершает запрос с учётом pending
  finalization и не перезаписывает connected/external provider. Новый Tick
  внутри контроллера не вводится. [NativeLiveFinalization](NativeLiveFinalization.ru.md).
- Public EnablePostTrainTuning допускается с согласованным заранее установленным
  native plan; без него сохраняется запрет. C-trim обязан оставаться0, старый
  AutoCalibrateFixedLTZThreshold —false. Реализованная grid-калибровка не является
  старым target-reference алгоритмом. [CalibrationPropertyContracts](CalibrationPropertyContracts.ru.md).
- Legacy PostTune transient pattern больше не присваивается training InputPattern;
  его измерительные окна читают фактически предъявляемую Dataset matrix.
  Новый inference attempt очищает sample validity даже при прежней cardinality.
  [LegacyPostTuneObservation](LegacyPostTuneObservation.ru.md).
- Branch RebuildCableForPostTuneProbes использует ReconstructNativeLearnerNeuron,
  проверяет Adopted и заново разрешает Neuron alias. Старые parent-C fallback,
  uniform overlay и повторный ApplyElementDefaults удалены. Ошибка transfer
  становится setup failure, не обученным Test. Адресные reconstruction modes
  не доказывают всю PostTune/search матрицу. [PhysicsPropertyContracts](PhysicsPropertyContracts.ru.md).
- Отдельно от owner setter изменён общий Rdk floating MDMatrix writer: сохранение
  decimal patterns использует max_digits10. Это owner serialization correction,
  не новое свойство или ослабление model identity. [ArchiveF64Precision](ArchiveF64Precision.ru.md).

Исходные отчёты старых ревизий и PropertyReview.source_commit сохранены.
Текущая сверка не переписывает наблюдения под новые критерии. Утверждения
промежуточных документов об отсутствии hook dispatch относятся к их снимку;
текущий runtime-контракт задаётся NativeLiveFinalization и связанными документами.

## Что остаётся для полного плана

После восстановления Automats2 выполнено независимое серверное повторение:
217 source records на каждом worker побайтно равны опубликованному JSON.
Receipts: 93d88621e25f43ea0fe9ecd841b53f38e274bbee (M40) и
30818dfb3a59a01c0eac63b2f9fc0bf6bc086fd2 (Elder), разделы
`s09-resumed-static-m40-a1` / `s09-resumed-static-elder-a1` в Reports.
Это read-only Git metadata проверка без исполнения исторического кода;
runtime/property coverage ею не расширяется. Соседняя миграционная проверка
обнаружила Bin worktree alias на Elder; диагностика сохранена, для чтения
точных Bin commits использован отдельный repository с корректным toplevel.

Полная runtime/property/mode/physics matrix открыта. Нужны текущие consumer/
helper evidence для каждой группы и реальные проверки применения факторов,
включая connected properties, heterogeneous images, рост, Load/Copy/reuse,
опциональные режимы и inherited Rdk properties. Последние не входят в217
объявленных learner UProperty и не должны исчезать из общего аудита.
Их девять shared source contracts и полная цепочка наследования теперь
описаны [отдельно](InheritedPropertyContracts.ru.md); server-reproduced
catalog не заменяет требуемую inherited runtime/connected/profile матрицу.
Сверка источников не доказывает полноту истории экспериментов, migration,
самостоятельный frozen Test или поддержку C-trim/target-reference calibration.


## Принятый PulseLib9ec: повторная сверка04.11

[Новый read-only catalog drift](PropertyAcceptedSourceDrift-20261104.json) сравнивает прежний принятый `456a5abdb0ff36a218b25943f7f2c6f9c2175190` с текущим `9ec4566d71bf56d4eeb5c8a920bbc683fcd85299`. По неизменяемым Git blobs найдено217→217 записей, без добавлений/удалений и без изменений исследованных declaration type/flags, registration name, setter/body и source default mentions. Source anchors, blob IDs и SHA256 для обоих снимков сохранены в JSON.

Это локальная статическая сверка production utility, не новый runtime gate и не server-reproduced receipt. Она не распространяет прежнюю runtime-приёмку на изменённые helpers/consumers и не подтверждает новую алгоритмическую семантику. Предыдущие217-record серверные receipts относятся к прежнему снимку456a5ab и остаются историческими. Pending Pulse cc971/8644 не становится принятым от этой проверки. Полная property/mode/physics matrix открыта.
