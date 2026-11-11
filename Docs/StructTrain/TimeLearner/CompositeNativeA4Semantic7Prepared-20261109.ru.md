# Actual A4 semantic7: подготовленные файлы и границы результата

Root выполнил разрешённую metadata preparation. Полученный readback сохранён без изменения bytes в `CompositeNativeA4Semantic7Prepared-20261109.actual-readback.json`. Его статус на момент записи — `prepared_bytes_verified_tests_not_dispatched`; это исторический результат подготовки, не результат семи tests.

Подтверждены157 regular files из шести actual A4 exports,74,969,578 bytes и fixture fingerprint `78f286701300c7d365e16d25bb64fca430a06b23e08b638396249a87b89056db`. Plan+fixture занимали100,155,392 allocated bytes при cap128MiB. Actual elapsed preparation8.17357537895441s. Собственный prep lease освобождён; другой старый stock-recovery lease не изменялся. До/после совпали632 материализованных Scripts files CEC, package fingerprint `629bd6fe86318b5e38251ab4f822a07d01debf4c8a9ab3d88a8896c0636de20d`.

Remote metadata record: `/media/user/Data/TimeLearnerRefactor/plan-composite-native-a4-semantic7-m40-a1/fixture-preparation.json`,3196bytes, SHA256 `47861beea29a81ce844094a95ce49729a15a2967fbbdc98ae4a1009dbfbf973d`. Его actual hash не подменяется хешем локального wrapper JSON. Suite/request остаются исходными Git9d blobs; fixture — исходными Gitb4feb bytes. Новый seventh bundle отсутствует. A4 source/runtime, конфигурации, CSV и модели не исправлялись.

## Отказ подготовки и воспроизводимость Git closure

Первая попытка GNUprep остановилась на `git status --untracked-files=all` **до** reserve/flat files/создания fixture: в sparse metadata donor отсутствовал исходный `.gitignore` object. Отрицательный transport receipt сохранён Root. Затем Root добавил только original `.gitignore` и `.gitmodules` objects в тот же новый PLAN Git ODB и повторил прежнюю fixed preparation command. Данные и source code при этом не редактировались. Локальное последующее исправление разбора stdout в Root JavaScript повторно читало сохранённый вывод, а не запускало preparation заново.

Все прежние V1/V2/V3 packs/descriptors оставлены. V1 helper receipt был исправлен до фактической доставки: отдельный V2 существующего операционного helper сохраняет SSH/stdin/default behavior и выдаёт `omitted_paths` по actual physical prefix absence, а также фактические sparse patterns. Старый helper не изменён.

Для воспроизводимости офлайн подготовлен полный V4 Git pack:4,123,008bytes, SHA256 `c79524436b40f0a09c01b0bbf58d6730bee31ab109e68a6586b77feffac461e1`,3853 objects. Он содержит те же два commits/trees, семь Docs blobs, original b4 archive/bundle и три служебных root objects **только в ODB**:

| Path | Original Git object |
| --- | --- |
| `.gitattributes` | `5bba2f9531c39afb69d1fd482a68f401d02f6fec` |
| `.gitignore` | `ffaf86e6d33ce18a901d396fb436d0077406467e` |
| `.gitmodules` | `878b41e2626ac2cc6a132f498949e89306ed122b` |

Checkout по-прежнему состоит из семи reviewed Docs; дополнительных source files нет. V4 — локальный reproduction artifact: его нельзя доставлять поверх уже успешно подготовленного PLAN и нельзя повторять preparation. Pack SHA — привязка операторского artifact, а fixture identity по-прежнему определяется original archive и157 исходными file hashes. Полные bindings/receipt hashes и границы сохранены в сопутствующем `.json`.

## Единственный последующий запуск

После preparation Root отдельно сообщил об авторизации и **одном** dispatch существующего production `owned_python_job run PLAN/request.json`. Root ведёт единственное наблюдение; этот агент не выполняет SSH, повторный launch, повторную preparation или новые tests. Local transport PID15480/Node task key `semantic7-production-readers` не являются remote MainPID/cgroup proof.

Штатный `run` сам создаёт новый job и `supervisor.log`; shell redirect, `nohup`, новый launcher или заранее созданный job directory не требуются. Значимые readbacks — actual STARTED binding, `process/contained` manager/kernel observations, `worker/validation/{result.json,unittest.log,suite.json}`, source/fixture snapshots, `controller-result.json`, `monitor-final.json` и `closure-and-reservation.json`. Чтение progress не запускает tests повторно.

Reader result здесь не утверждается. Приёмка требует exact7 ID без skips/errors/failures, прежних suite/request/package/fixture bindings, successful worker/controller result, закрытия всей собственной cgroup и освобождения именно её lease, затем публикации и независимой проверки. Другой lease не освобождается по факту завершения этого job. Потеря stdout/transport сама по себе не является разрешением на retry.

Даже положительный reader7 подтвердит только заявленный portable archive/config/closure/geometry/accounting scope. Он не создаёт нового native execution witness, Train certificate, scientific verdict или полной stage3/5/package/CLI приёмки.
