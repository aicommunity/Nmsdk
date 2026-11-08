# Подключение matched omission к обучению: следующий интеграционный блок

Это постановка оставшейся реализации, не свидетельство завершённого Train.
Production selector и nativeN+2 group подготовлены отдельно; их normal/ASan
приёмка не заменяет перечисленные ниже изменения.

## Математическая цель

CapturedPerInput, опорный входN−1, N0/N1 и исходные train tolerances сохраняются.
Измеряемый результат — raw potential и время реальной вершины полной пачки.
Контрольные исключения используются для operational assignment, не как
разложение нелинейной модели и не как новая амплитудная цель. Общий максимум
пачки не подставляется в Train. Shared/unknown высокий отклик остаётся
Ambiguous; отсутствие пика постороннего импульса само по себе не мешает.

## Типы доказательств и совместимость

1. В FinalVerification добавить явно версионированный composite measurement
   protocol с method `matched-omission-assigned-maximum-v1` и собственной policy.
   Старые VerificationProtocol/ProbeSpec schemas1–6 не менять по смыслу.
2. Не создавать искусственный успешный ProbeObservation schema3 из полного
   schema6 trace. Raw schema6 остаётся самостоятельной native observation.
3. Новый validated measurement должен содержать raw/full maximum, plateau,
   actual stimulus/origin times, signed residual inputs и bindings полного
   witness: group/trials, model/base/effective revision, epoch, target,
   physical channel, reset/instance и method/policy identity.
4. Получать validated measurement только через production validator полного
   composite evidence. Один diagnostic packet, успешный process или завершённая
   группа не являются достаточным входом для CapturedReferences/certificate.

## NativeTrainingService и BoundedTrainingSession

```text
select next reference/search/final-verification input
freeze candidate parameters, target, epoch and C0 witness
start bounded FullBefore -> omit0..omitN-1 -> FullAfter group
for every actual native trial:
    preserve packet and samples
    validate native lifecycle/source/model/capacitance binding
    restore full presentation before the next boundary
if cancelled, incomplete or budget exhausted:
    preserve partial group; never submit a measurement
otherwise:
    replay/validate composite witness
    pass measured full maximum through the declared assignment method
    capture reference / consume candidate / verify final input
only then permit the next structural edit
```

NativeTrainingService::Request сейчас устанавливает onPrepared с search->Arm.
В новом пути Arm вызывается ровно один раз для measurement group по первому
FullBefore, а не повторно на каждом контрольном omit. Старые evidence sinks
получают все реальные пробы с уникальными IDs. Внутренний sub-FSM не вызывает
Calculate/Reset learner; physical reset остаётся штатной подготовкой executor.

Добавить отдельный ConsumeMatched путь bounded search, используя общий
валидированный измеренный результат для timing/amplitude residuals и bounded
L/N/R поиска. Не снимать требования schema3 validator и не объявлять его
невалидные waves валидными. После effective edit уничтожать незавершённую
группу и инвалидировать зависящие наблюдения. Финальная проверка каждого входа
выполняет свежую полную группу, включая reference input.

## Бюджеты и остановка

Различать search actions/measurement groups и фактические native bursts.
Одна группа стоитN+2 проб; native/model/wall/sample budgets ограничивают всю
работу, включая references, repeats, retries и final verification. Старое
maximumProbes не должно незаметно менять единицы в compatibility режиме.

Остановка/retarget не создаёт convergence. Отмена восстанавливает transient
presentation/routing; исходный training target сохраняется до явного retarget.
Параметры меняются только после закрытия группы на legal edit boundary.
N1 использует проверенный алгоритм single-impulse selection; это требует нового
training proof path, не автоматического повышения диагностической schema5.

## Export/import и independent reader

Добавить production codec полного composite witness: обе full traces, все
omit traces, реальные события/входы/окна, параметры policy, raw native packets,
производные support sets и выбранный full maximum. Первичные CSV сохранять
сжатыми в Git; result summary не заменяет исходные данные.

Completed-boundary model export включает references и final proof groups.
Импорт сначала пересчитывает fingerprints, native packet readback и assignment,
затем residuals/certificate; потерянный control, другая policy/model/C0 или
неполное окно запрещают Exact. Mid-probe resume не обещается.

Python reader независимо воспроизводит grid/source/profile matching,
repeatability, measured maxima, support/unknown/shared classification и выбор
вершины. Его итог сравнивается с C++ по настоящим native группам. Схема scorer
и оценка распознавания сохраняют отдельные execution/validity/training/
calibration/evaluation axes.

## Приёмка

Pure cases покрывают delayed-prior wave, nonlinear interaction, missing unrelated
peak, меньшие extrema, ties/plateau/clipping, unknown influence, actual tick drift,
model/source/reset/instance changes, missing/duplicate controls и бюджеты.
Native cases проверяют Classic/Branch,2000/20000 Гц, all-channel raw capture,
restoration, stop и edit между пробами. Затем расширить N1/2/4/>4, heterogeneous
physics, N0/N1, references/search/final certificate, retarget и model roundtrip.

После этого выполнить cold Train и frozen Test с полными графиками всех
паттернов. Приёмка алгоритма может содержать честные Ambiguous/Unresolved;
8/8 не требуется. До выполнения всего блока новый путь не рекомендован вместо
compatibility и не считается закрытием исходных этапов6–8.


## Уточнение до включения в Train: область назначения пика

Независимый replay десяти native groups (evidence
`515a86c42509c136211d46cc5e021145e804b618`) подтвердил, что full-trace v1
может запрещать ранний exclusive maximum из-за более высокого позднего shared
maximum. Legacy собственное окно Expected[i]+delay не тождественно этому
full-trace критерию. Механически заменить измеритель learner на v1 нельзя:
сначала нужно явно проверить соответствие математической цели и сохранить
compatibility-контроль. Ни наличие окна, ни predictor не доказывают отсутствие
более высокого отклика закреплённого импульса за его пределами.

Пока допустимы две раздельные роли:

- Строгий v1 witness используется только в заявленном полном наблюдаемом
  горизонте и с его явными ограничениями. Ранее сохранённые verdict не меняются.
- Owned-window candidate — отдельная диагностическая подсказка для выбора
  следующих L/N/R кандидатов. Она не становится schema3 observation,
  CapturedReferences, committed input или доказательством Exact. При отсутствии
  валидного witness результат поиска остаётся unresolved/ограниченным бюджетом;
  диагностический лучший кандидат сохраняется отдельно.

Если будет введён оконный метод, нужны собственные method/schema/policy identity,
заранее зафиксированные offsets относительно фактического assigned event,
эффективные grid boundaries и правила полного покрытия plateau/halo. Нельзя
двигать окно после просмотра пиков, чтобы скрыть shared/unknown peak. Изменение
кандидата, физики, reset, selector или target инвалидирует окно и наблюдения.
Новая оконная процедура потребует отдельного обоснования применимости к исходной
задаче; это не разрешение заменить её максимальным пиком всей пачки.

Обязательные дополнительные regression cases:

1. Exclusive assigned peak внутри окна и более высокий shared/unknown снаружи:
   diagnostic candidate сохраняется, исходный v1 verdict не повышается.
2. Общая вершина в перекрывающихся окнах: геометрия не назначает её двум входам;
   shared/unknown support сохраняет неоднозначность.
3. Plateau на границе окна и неполный comparison halo: явный clipped/unresolved,
   без обрезания плато или молчаливого сокращения области сравнения.
4. Отсутствующий actual assigned event, неверный ordinal, сдвиг retained event
   или смена модели/epoch/reset внутри группы: invalid/cancel, без retarget окна.
5. Детерминированное proposal-window после candidate edit получает новую identity;
   старые residuals/reference не переносятся. Exploratory window grid допустим
   только как диагностика с полным учётом проб и бюджета.
6. Negative test: window-only hint не может создать TrainingCertificate. Более
   низкие посторонние пики сами по себе не требуют отказа или ровно N максимумов.

Все пункты этого раздела — постановка следующей реализации; оконный метод и
его подключение в NativeTrainingService пока не реализованы.
