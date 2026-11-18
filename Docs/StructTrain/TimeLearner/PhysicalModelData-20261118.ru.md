# Перенос полной физической модели без повторного чтения истории

Статус на 18 ноября: код и native fixtures подготовлены в изолированных ветках
`codex/timelearner-physical-model-data` корня и PulseLib. Runtime-проверка
выполнена частично: SDK a3 собран,228 случаев выполнены,226 прошли.
Два roundtrip отказали только на требовании valid=true для неоднозначных
пиков; полные исходные/restored трассы совпали. Исправленный fixture пока
не проверен. В develop изменения не объединены; этап 5 остаётся частичным.

## Какой дефект устраняется

Существующие completed/stopped/recognition пакеты содержат полную физическую
модель вместе с историей измерений и поиска. Подтверждённый пример: из
136740081 байта компактного threshold-candidate JSON measurement_archive
занимает 122410018 байт; сам архив нейрона — около 4.76 MB. Повторный полный
proof import в каждой операции Test дорого обходится. Байтовый parser отдельно
убирает лишние копии входа, но не отделяет модель от истории.

Новый `timelearner_physical_model_data`, schema 1, хранит полные native
`neuron` и `dataset`, включая storage images, graph, классы и связи, реальную
неоднородную физику дочерних элементов, индивидуальные L/Ns/Rs/C, частоту и
порог. Сохраняются декларация, исходный target/protocol, model revision,
source solo revision и conversion record. Никакие поля старого evidence package
не удаляются: он публикуется отдельно и связан через `source_boundary.sha256`.

## Production-путь

```text
complete original native boundary
  -> existing full source importer and its proof checks
  -> capture whole physical graph + images + Dataset
  -> signed physical-model DATA document + source-boundary reference
  -> native image registration and Dataset/neuron import
  -> read effective graph, parameters, bindings and frequency
  -> compare model revision
```

PulseLib реализует ExportNativePhysicalModelData и PrepareNativePhysicalModelData.
Общий validator private children разделён с обычным NativeModelBuilder;
существующие проверки attached owner сохранены. Нет nested Calculate,
самоприсваиваний на тике, исправления defaults или изменения общих образов.

Console добавляет `--timelearner-physical-model-export <job.json>` с обычным
`--timelearner-output <new-directory>`. Job имеет kind
`timelearner_native_physical_model_export_job`, schema 1, implementation_id,
полный source_state и canonical sha256. Допускается существующий lossless
`checked-file-source-v1`; complete source_state восстанавливается до проверки.
Операция пишет model.json, input-projection.json и execution.json. Projection
явно ссылается на полный job/source; она не называется полным job.json.
Новый Python SOURCE_FIELDS и native transport fixture включают эту роль.

## Границы доверия

`data_only=true`, `dynamic_checkpoint=false`, `certificate=null` обязательны.
В возвращаемом объекте нет training service, reference/search history или
controller checkpoint. Полные исходные metadata внутри native archive — данные
об источнике, а не заново созданная proof authority. Существующие proof importers
новый kind отвергают. Порог переносится как физический параметр; калибровка
автоматически подтверждённой не становится.

Canonical digest обнаруживает изменение сохранённых байтов, но сам по себе
не доказывает происхождение произвольно заново подписанного документа.
Научный runner должен разрешить source_boundary в M40 archive, проверить
исходный пакет и его отношение к exported model. Без этого допускается
только явно обозначенное DATA/diagnostic исследование, не completed Train PASS.

## Подготовленные проверки

В Test_PulseLib_PhysicalModelData.cpp четыре native cases:

1. Classic: полный граф и несимметричные L/Ns/Rs, roundtrip, новый fresh owner,
   совпадение всех отсчётов Soma и actual stimulus через штатный scheduler.
2. То же для Branch, с native solo routing и восстановлением исходного графа.
3. Противоречие между графом и заново подписанным параметром/классом отвергается.
4. Certificate/checkpoint и противоречащий target не создаются переподписью.

Исходный fixture — реально созданная и явно остановленная cold модель N=2,
2000 Hz. Ни одного обучающего измерения или сертификата ей не приписано.
Проверяется ненулевая конечная реакция, а не только true от lifecycle-методов.
Отдельно сохраняется результат измерителя: полный перенос модели обязан
сохранять также неоднозначную реакцию. В a3 у обеих моделей зафиксированы
601 одинаковых отсчётов и `peak_ambiguous:input0` при complete=true. Это
не разрешает считать неоднозначный пик valid при Train. Fixture теперь
сверяет весь observation, кроме собственных run/trial ID, и допускает
только valid либо именно эту сохранённую диагностику; прочая invalidity
остаётся отказом. Порог, физика и окно не меняются ради теста.
При TIMELEARNER_EXECUTION_OUTPUT сохраняются полные source/restored Soma CSV
с входными импульсами и обе observation JSON; после server run по ним нужны
временные графики в масштабе, пригодном для визуального сравнения.

Новый transport case проверяет только lossless загрузку полного source_state;
он сам не доказывает корректность физической модели.

[Инвентарь следующего native gate](ValidationPlans/PhysicalModelData-20261118/INVENTORY.json)
сохраняет прежние218 Windows cases и добавляет4 parser +4 model DATA +1 source
role: всего227, для Linux228 с исходным symlink case. ID сверены с12 файлами
Root `3dce4532db40a5b14623a403e08437d8e1ca7bbc`, Pulse
`c54d9c0a65ac6eadeccfe1793672b7a9472ea559`; hashes относятся к Git blob bytes.
Это inventory новой правки fixture, ещё не выполненный gate этого снимка.
Все результаты a1–a3 сохраняются отдельно, включая отрицательные.
[Readback a3](../../../Reports/StructTrain/TimeLearner/PhysicalModelDataSdk-20261118/native-a3-readback.json).

## Что требуется до приёмки

- Сборка реального Console/PulseLib и native cases на разрешённом worker;
  source parser regressions и прежние prepared/model/archive fixtures.
- Полный исходный learned/recognition/calibrated package из настоящего опыта,
  экспорт, новый процесс, import, semantic identity и реакции на все 8 паттернов.
- Heterogeneous images, разрешённый C-trim, threshold, conversion и PostTune;
  потерянный узел, связь, образ или индивидуальный параметр запрещают перенос.
- Интеграция frozen evaluation и source-evidence resolver в корневой пакет;
  новый CLI export сам по себе не заменяет весь pipeline.
- Фактические размер, RSS и время, исходные данные в M40 archive, графики и
  проверенный Git/archive reference. Уменьшение RSS пока не заявлено.

Существующие immutable Linux Train и Windows SDK N1 не изменены. Их результаты
не являются проверкой этого нового формата. Научные эксперименты имеют приоритет
при восстановлении доступа: сначала наблюдение прежних handles и сохранение
их данных, затем новые проверки при свободных ресурсах.
