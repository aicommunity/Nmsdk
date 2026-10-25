# Этап 5: перенос обученной модели

**Этап целиком не завершён.** Принят только подэтап 5.1 — описание и проверка
идентичности фактического native графа. Полный экспорт обученного состояния,
storage definitions, явные внешние порты и Train → Test pipeline ещё отсутствуют.

## Подэтап 5.1 — semantic model identity

Реализованы `IdentifyModel` и `VerifyModelIdentity` в Console, отдельный CLI
`--model-identity`. Формат и ограничения: [ModelIdentity.ru.md](ModelIdentity.ru.md).
Сравниваются параметры каждого узла, частоты, вычислительный порядок, все
действительные binding slots, aliases и индексы дочерних компонентов. Динамика
не подменяет параметры модели. Код/runtime identity остаётся отдельным manifest.

Expected identity проверяется до сравнения с новой native моделью: schema,
обязательные поля и hash собственных данных. Изменённый Rs/C или связь не может
быть принят за совпадение на основании сохранённой строки sha256. Неизвестная
схема, nonfinite, внешний источник без объявленной границы, unsupported parameter
и неполный cached index не получают положительного fingerprint.

В ходе проверки найден дефект индексирования: свежая асимметричная модель и
native XML roundtrip сохраняли одинаковый граф и физику, но разный порядок
`Membranes`. Корневой failing snapshot:
b6de31a8bdb8c74ee813b462d3724992ee4c4a49. После исправления NPulseNeuronCommon и
NPulseNeuron завершают Build индексом в порядке именованной таблицы детей.
Scheduler не переставляется дополнительно. Индекс не исключён из сравнения,
а зависимость от истории создания устранена в его владельце.

На .11/Qt5 и .17/Qt6 прошли семь адресных native cases и четыре maintained CTest
suites на root 7fe8d66dbffe1e68f599a2606e303044feb180cc. Это production API,
native Take/Init/Save/Load, а не извлечённое тело функции в тестовой копии.
Полный PulseLib suite содержит 129 cases; raw CTest details сохранены.

Отдельно Console открыла реальные Classic и Branch Test-проекты и без расчёта
получила валидные identities для 609 и 440 узлов. Первоначально Branch был
отклонён из-за штатной пары строк StatisticDoubleMatrix.AverageInput: добавлено
явное представление типа, параметр не удалён из описания ради PASS.

Оба сервера получили одинаковые fingerprints шести сохранённых случаев:
четыре native fixture artifacts и два реальных проекта. Native асимметричный
source и restored совпадают также по полным данным model, а deliberate reorder
даёт другой hash. CLI controls подтверждают отказ от calculation, двух
inspection modes одновременно и перезаписи существующего артефакта.

Артефакты: Reports/StructTrain/TimeLearner/s05-identity-elder1 и
s05-identity-m40. M40 содержит исходный failing log, source/post-negative-control
описания и runtime provenance. Файл asymmetric-reordered.json в baseline снят
после намеренной перестановки в негативном контроле, а не сразу после Load;
это отдельно обозначено в README. Нового ASan прогона в 5.1 не заявляется.

Проверены все 246 хешируемых файлов опубликованного раздела после checkout,
включая gzip и полные данные source/restored. Принятый PulseLib develop merge:
4af8184275e182b943bb43df7447f8f7a065d73d. Tested SHA не заменяются merge SHA.

## Следующая реализация — полный ModelArchive

Нужно реализовать единый versioned архив с native graph XML и проверяемыми
зависимостями storage, а не набор parent overlays. Он должен включать profiles,
морфологию, реальные Ns/TipRs/C/связи, частоту, targets/references, порог с
calibration provenance и solo/recognition/conversion сведения. Сохранённая модель
не является controller checkpoint или checkpoint незаконченной физической пробы.

```text
export at a completed native stage boundary:
    capture immutable class/profile closure and actual learned graph
    declare stimulus boundary ports; reject every undeclared external binding
    capture targets, references, conversion and calibration provenance
    serialize native graph and versioned metadata
    identify actual graph and bind certificate to that identity
    validate archive completeness and retain all referenced artifacts

import for Test:
    validate archive schema, hashes and profile definitions
    register immutable images in dependency order, checking collisions
    construct/load through native storage and set frequency before final build
    perform native initialization/reset
    verify archived identity against actual complete graph at declared ports
    freeze model and calibration, then enable evaluation
```

Нельзя обещать полноценный Train → Test по результату семи tests 5.1. Остаются
непроверенными регистрация архива в свежем storage/процессе, отсутствие используемого
профиля/узла/класса/связи, все физические семейства, полный frozen waveform
roundtrip и интеграция экспорта с реальным learner/runner. Тест неизменности
модели при probes и checkpoint на границе этапа также ещё предстоит выполнить.
