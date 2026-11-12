# Полный compact primary Combined: сохранён без изменения исходов

Collector completed/exit0, operation_passed=true, whole owned group closed и lease released. Actor/source snapshot до/после совпал побайтно. [Controller](completed/controller-result.json), [closure](completed/closure-and-reservation.json), [raw hashes](completed/readback-integrity.json).

Сохранены все 2279 archive members: 690847303 expanded bytes, 42246064 compressed bytes. [Первичный архив](../../../../../Reports/StructTrain/TimeLearner/ObservationDomainCombinedPrimary-M40-20261112/primary.tar.xz), [полный manifest](../../../../../Reports/StructTrain/TimeLearner/ObservationDomainCombinedPrimary-M40-20261112/bundle.json), [collection proof с before/after](../../../../../Reports/StructTrain/TimeLearner/ObservationDomainCombinedPrimary-M40-20261112/collection-proof.json), [origin](../../../../../Reports/StructTrain/TimeLearner/ObservationDomainCombinedPrimary-M40-20261112/ORIGIN.json). Все Git-полученные файлы проверены по размеру/SHA256. Namespace и closure проверены production collector до и после упаковки; исходные файлы/исходы не переписывались.

A1 сохраняет общий отказ: Classic valid/invalid_observation:ambiguous, Branch timeout/unverified_execution без итогового package/summary. Отсутствующий Branch package не достраивается. Обычный Test этих незавершённых обучений не запускался.

A1 collector отказал из-за file bound128MiB; A2 — из-за потери точности link timestamps при JS пересериализации декларации. A3 использовал исходные байты A1 с единственной текстовой заменой bound на256MiB. Обе неуспешные попытки сохранены отдельно. [Git transport](git-transport.json). Независимый semantic replay большого пакета и temporal отчёт ещё нужны; архивирование не подменяет эти проверки и весь план0–12.
