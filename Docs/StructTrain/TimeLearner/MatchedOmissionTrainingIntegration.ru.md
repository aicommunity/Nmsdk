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
