# Этап 5: перенос обученной модели

**Этап целиком не завершён.** Приняты 5.1 (идентичность native графа), 5.2
(native archive замкнутой физической модели с storage definitions) и 5.3
(явные stimulus-порты). Полный экспорт реального learner state, checkpoint
контроллера и Train → frozen Test pipeline ещё не реализованы.

## Подэтап 5.1 — semantic model identity

Реализованы общий API `IdentifyModel`/`VerifyModelIdentity` и отдельный Console CLI
`--model-identity`. Формат и ограничения: [ModelIdentity.ru.md](ModelIdentity.ru.md).

Реализация и native archive перенесены в PulseLib для использования контроллером;
механическое изменение проверено отдельно: [ModelGraphOwnership](ModelGraphOwnership.ru.md).
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

## Подэтап 5.2 — native ModelArchive и восстановление definitions

Реализованы ExportModelArchive/ImportModelArchive. Архив содержит native XML
физической модели и всех зависимостей storage, полную identity и metadata;
схема, payload/XML hashes, обязательные параметры, классы/число/порядок детей и
dependency closure проверяются до регистрации. Нативные C++-фабрики должны
существовать в runtime и сверяются с сохранённым effective image. Производные
образы создаются из сохранённых definitions без перезаписи existing prototypes.
После native Load/Init обязательно проверяется actual identity.

Состав, ограничения и владение результатом: [ModelArchive.ru.md](ModelArchive.ru.md).
API сохраняет supplied metadata с раздельными model_spec/learned_solo/recognition,
training/calibration/conversion; он не производит автоматически доказательство
сходимости. Declared calibration проверяется по действительной LTZone и её
threshold. Новый CLI `export` пока не объявляется доступным пустым stub.

На обоих серверах проверен root 46f707c249cfcc3d4765d6630744367c19e30412:

- Пять parent tests прошли; FreshProcessImport — helper, пропущенный в parent
  и фактически исполняемый в двух отдельных child processes.
- Native archive содержит 41 узел и 34 определения классов (7 native_required,
  27 derived_image), отдельные body/LT C, individual Rs/C, три синапса и PSI.
- При 2000/20000 Гц новый процесс, где custom-образов ещё нет, восстанавливает
  модель, сверяет все параметры/связи и получает тот же неплоский отклик.
- Удаление обязательного Rs, узла и смена класса отвергаются до загрузки даже
  с пересчитанными hashes. Удаление связей explicit mode 0 отвергается при
  сравнении actual graph; это не проверка одной лишь контрольной суммы.
- Четыре maintained CTest suites прошли. Полный PulseLib suite: 135 cases,
  134 passed и один helper skipped; два child imports выполняются внутри parent
  controls. Skipped helper не считается дополнительным passing test.

Отдельно выполнен реальный перенос M40 → Elder-1 через Git. Источник:
13e3830ae8cd2afc6b15e1a3f8b4af9bfeab578c, paths/blobs и hashes сохранены в
archive-cross-git-transfer.json.gz. Два новых процесса .11 импортировали
произведённые на .17 архивы, сохранив identity и waveform: 200/2000 отсчётов,
max pairwise error=0 при 2000/20000 Гц. Исходники и данные не передавались scp/rsync.

Артефакты опубликованы в s05-archive-m40 и s05-archive-elder1. Metadata явно
model_spec/not_trained: это implementation/characterization controls, а не
результаты cold train или распознавания. Initial logs сохраняют исправленные
ошибки нового fixture: conversion UEPtr и отдельный NModel, не установленный
в Environment. Runner теперь использует current model и одинаковое начало
model time; эти ошибки не приписываются алгоритмам learner. Нового ASan run нет.

## Оставшаяся реализация полного переноса learner → Test

Подэтап 5.3: ModelBoundary.ru.md описывает versioned stimulus ports, native
Connect/BreakLinks, независимый Test-источник и полный контроль slots. На обоих
серверах 16 targeted cases (15 passed, один helper skipped, четыре child imports)
и 4/4 CTest suites прошли; полный PulseLib — 140 cases, 139 passed, один helper
skipped. На M40 также прошли 4/4 ASan suites с detect_leaks=0. Два новых процесса
M40 импортировали портовые архивы Elder-1 через Git и сохранили identity и
200/2000 waveform samples с max error=0. Raw logs, начальные исправленные ошибки
новой реализации, runtime manifests и модели доступны в s05-ports-*.
Эти проверки по-прежнему имеют metadata model_spec/not_trained.

Native graph XML и definitions уже реализованы в 5.2. Следует завершить общий
контур с реальным learner adapter, а не набором parent overlays. Он включает profiles,
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

Нельзя обещать полноценный Train → Test по результатам 5.1/5.2. Для реального
learner остаются подключение API stimulus ports к реальному adapter, захват target/reference и
certificate/calibration/conversion provenance из владельцев, вся матрица
физических семейств/режимов, controller checkpoint на границе этапа и frozen
evaluation через общий ProbeSpec/Observation. Изменение solo → recognition и
PostTune должно заново привязывать сертификат к конкретному состоянию.

Registration transaction ещё не замкнута: ошибка может оставить новые unused
immutable образы; import storage после неё нельзя переиспользовать без проверки.
TL-014 теперь подтверждён двумя native ASan reproducer и исправлен в Rdk;
подробности — StorageCleanup.ru.md и s05-cleanup-*. Это позволяет продолжить
проверку cleanup, но не доказывает атомарность всего импорта и корректность
удаления произвольного графа зависимых образов. Существующие prototypes в 5.2
не заменяются; полный cold pipeline пока не запускается.
