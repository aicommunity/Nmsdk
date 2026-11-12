# Summary8 повторно строит полный архив: подтверждённый blocker

## Доказательство

[Classic budget16 A2](ValidationPlans/M40FullDomainBudget16TrainA2-20261112/RESULT.ru.md), compiled SDKRoot448b153f2/Pulse7b524b8, завершился native timeout2100s. Последний probe был отменён по search-time budget; последующий SIGTERM stack находится внутри EncodeAndValidateNativeCandidateWindowServiceArchive, вызываемого CompositeSummary<5,8>. Полной модели/summary нет. Это не подтверждённый training outcome и не ошибка SSH.

NativeCompositeLearnedState.cpp::CompositeSummary, ветка Summary==8, строит целый архив только ради EncodeCandidateWindowRecoveryLedger. NativeCandidateWindowStateFactory::ExportImpl затем самостоятельно вызывает тот же тяжёлый encoder. NativeCompositeTrainingEvidence.cpp::EncodeAndValidateNativeCandidateWindowServiceArchive кодирует все CSV, base64 primary_blobs, hash документа и декодирует/проверяет полный архив. Эти вызовы подтверждены исходниками; точная доля времени и RSS каждого шага ещё не измерена. Предыдущая оптимизация export не закрыла этот путь summary8 на67 группах.

## Адресное изменение следующего подэтапа

Цель: одна проверенная неизменяемая граница export, из которой summary получает только нужные сведения и recovery ledger; тяжёлые primary сериализуются не более одного раза. Возможный механизм — общий checked boundary object для model+summary либо отдельный checked metadata view. Выбор требует проверки всех callers; нельзя просто убрать проверку ledger или довериться произвольному JSON.

Компоненты: Core/TimeLearner/NativeCompositeLearnedState.cpp/.h, NativeCompositeTrainingEvidence.cpp/.h, recovery ledger validator и Console TimeLearnerTrainingJob caller. Проверить также ProbeEvidenceJson.cpp::EncodeNativeTrainingState и integration fixtures, использующие раздельные summary/model API. Сам поиск, CapturedPerInput, назначение пика, Rs/C, lifecycle и bool методов не менять.

Контракт:

1. Summary8 сохраняет текущую схему, все references/candidates/rejections/counters и тот же verified recovery ledger.
2. Модель сохраняет весь прежний semantic/physical fingerprint и проверку primary; не теряются partial groups, cancelled probes и отрицательные результаты.
3. Checked boundary привязан к revision/epoch/attempt, records/references/finals и recovery deliveries; после изменения данных повторное использование запрещено. Не вводить неинвалидируемый глобальный cache.
4. Декодирование недоверенного сохранённого архива продолжает полностью проверять bytes/hashes/geometry/ledger. Оптимизация внутреннего producer не ослабляет import.
5. Внешний конечный manifest публикуется только после завершения файлов; обрыв не создаёт видимость полного результата.

Проверки: существующие реальные recovery service fixtures Classic/Branch, stopped и completed boundaries, неполная последняя проба, повреждённый ledger/source/primary; semantic equality до/после оптимизации. Выполнять на указанных Linux workers. Отдельно измерить размерность не меньше67 groups/398 raw trials: wall time, peak memory и число материализаций primary. Итоговая выгрузка должна укладываться в уже объявленные300s, без увеличения времени Train ради сокрытия дефекта. Использовать production код, не копию тела функции.

После адресной приёмки — один повтор исходного ограниченного scientific job с теми же математическими условиями. Пока исправление **не реализовано и не принято**. Весь план остаётся частичным.

Для адресной диагностики исходный индекс270193422 bytes сохранён: он содержит67 measurement records и primary blobs; production DATA reader независимо пересчитал их за66.82s. Это даёт готовый регрессионный корпус без повторного Train. Наличие полного measurement archive не заменяет отсутствующую финальную модель и summary/controller state. Периодичность записи этого тяжёлого индекса и доли расходов следует измерить, а не предполагать.

## Уточнённый конкретный caller и порядок

App/NeuroModelerConsole/TimeLearnerTrainingJob.cpp имеет одинаковый Git blob60f7f23f69142abf83cfbe531646e594491ac020 в compiled Root448b153f2 и текущем root. Подтверждён порядок:

```text
package = owner.ExportNativeLearnedState(...)
PublishNativeCompositeArchive(output, package, artifacts)
Write(summary_name, EncodeNativeTrainingState(service,...))
Write(package_name, package)
Write(execution.json, final_manifest)
```

Таким образом, package уже был получен в памяти и archive index опубликован, но запись файла модели отложена до повторного тяжёлого EncodeNativeTrainingState. Этим объясняются сохранённый индекс и отсутствующая модель при SIGTERM внутри summary8.

Адресный путь исправления: фабрика export формирует model+summary из одного уже проверенного boundary/archive; Console использует этот результат без второго кодирования primary. Сначала атомарно сохранять полученный package, затем остальные файлы, а положительный execution manifest — только последним. Даже если последующая запись оборвётся, отдельный package не делает весь run успешным. Сохранить standalone summary API для совместимости и проверить все его callers; не подставлять произвольный непроверенный JSON ledger. Постоянный service cache с новой схемой invalidation для этого не требуется.
