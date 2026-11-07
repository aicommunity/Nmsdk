# Одна измеренная вершина и независимые закреплённые импульсы

07.11.2026. Исправлен конкретный дефект проверки сертификатов: один максимум
одного канала мог учитываться как два независимых отклика разных импульсов.
На контролируемых данных исходный код пропускал такой пакет в references и
выдавал `Exact`. После исправления обе операции отказывают с причиной
`shared_measured_peak_between_stimuli`.

Это проверка production C++ на контролируемых сигналах, без расчёта физических
нейронов. Общий вопрос принадлежности волн штатной пачки остаётся открытым в
[контракте измерения](PeakMeasurementContractReview-2026-11-07.ru.md).

## Дефект и исправление

`ProbeRecorder` для исторических WindowOnly schema1/2 независимо измеряет окна.
Два окна одного канала могут содержать один максимум и получить разные stimulus
IDs. Запись остаётся пригодной для диагностики в историческом смысле, но её
`valid=true` не доказывает независимость назначенных откликов.

`Core/TimeLearner/FinalVerification.cpp`, общий `CheckedMeasurement`, раньше
проверял каждый максимум отдельно. Он не проверял совместимость назначений.
Контрпример: p0 и p1 предшествуют одной вершине channel0; оба окна получают
одинаковые измеренные время, raw potential и положительную задержку. Каждый
максимум формально согласован с метаданными, хотя независимых откликов нет.

Теперь после проверки конечности, контекста и отдельных измерений выполняется:

```text
group validated peaks by measured channel
sort each group by measured peak start
if the next start <= the preceding plateau end:
    reject shared_measured_peak_between_stimuli
continue only with mutually disjoint peak/plateau samples
```

Интервалы `[time, plateauEnd]` замкнуты: общий отсчёт конца/начала также запрещён.
Допуск по времени не расширяется и новый epsilon не вводится. Перестановка
окон не влияет на результат. Совпадение пиков разных каналов разрешено: оно
может быть необходимым результатом синхронизации.

Проверка общая для capture references, поиска через `ValidateProbeMeasurement`
и финального прохода. Диагностический recorder, serialization schemas,
CapturedPerInput, reference N−1 и допуски сохранены. Публичный lifecycle Rdk,
физические параметры и вычислительный порядок не изменены. Schema3 уже требует
собственного физического канала Classic либо одного выбранного окна Branch.

## Проверки до и после изменения

| Срез | Код | Результат |
|---|---|---|
| До исправления, M40/ASan | root `2b945d6365feec7c93287a9a3b8120b29cf66b68`, PulseLib `c17ebd2cc75abd3a1562492907c90782232c2ea6` | 23 tests, три новых отрицательных контроля выявили дефект; остальные 20 прошли |
| После, M40/ASan/Qt6 | root `90a0a917b32eeb21925b414cc18450fbdbeaba03`, PulseLib `9e0640964945ad5903a4fff1c5091ebf71a69810` | 23/23 passed; instrumented production sources и фактически загруженная libasan подтверждены |
| После, Elder/normal/Qt5 | те же root/PulseLib | 23/23 passed |

Три отрицательных контроля проверяют повторное назначение вершины, пересечение
частей плато при разных начальных временах и отказ capture/final certificate.
Отдельный положительный контроль сохраняет совпадающие времена на разных
каналах. Полный набор включает прежние проверки reference provenance,
общего финального прохода, signed residuals, исходных tolerances и schema3.

Компилировались настоящие `ProbeObservation.cpp` и `FinalVerification.cpp`,
полный `Test_PulseLib_FinalVerification.cpp` и штатный capture main. Тела
функций не извлекались в тестовые копии. Runtime, команды компиляции,
dependency hashes, реальные mappings, stdout/stderr, JUnit, closure и
освобождение leases сохранены. Leak check не заявляется.

Две неуспешные подготовки M40 сохранены: A1 отклонён из-за регистрации файла
вместо дерева каталогов; A2 собран, но процесс теста не запущен из-за
несовпадения `QT_QPA_PLATFORM`. A3 использовал проверенный неизменившийся
бинарник A2 после исправления окружения. Эти отказы не являются результатами
измерения модели и не переименованы в успешные тесты.

## Первичные доказательства и ограничения

- M40: commit `745c0bd2455745259f8c4a461cb1ddf6b3f8b172`,
  [bundle](../../../Reports/StructTrain/TimeLearner/s07-assigned-vertex-unit-m40-a1/bundle.json):
  130 members, 52 340 байт сжатого primary.
- Elder: commit `25b29c0b94cf4cb6ba49dcbc73a42bbbd3d4b4f5`,
  [bundle](../../../Reports/StructTrain/TimeLearner/s07-assigned-vertex-unit-elder-a1/bundle.json):
  44 members, 43 028 байт.
- [Независимая проверка](AssignedVertexUnitVerification.json): все archive
  members, JUnit inventory и 16 привязок project source/header к Git проверены.

Запрет общей вершины необходим, но не доказывает принадлежность двух разных
вершин разным импульсам. Он не снимает ограничение ordinal/count schema3,
не заменяет штатную пачку single-pulse Train и не даёт нового результата
классификации. Августовские 4/8–6/8 этим опытом не переоцениваются.

В корневой CMake добавлен быстрый `Test_PulseLib_VerificationAlgorithms` с
теми же production-файлами и cases, которые входят в StorageComponents.
Полный SDK configure/build на Elder теперь завершён: 23/23 cases нового
target и 21/21 native storage/training cases (17 NativeBurstAssignment,
4 NativeBoundedTraining) без skips/errors. Исходники root
`0f03bdca386a59583a3404b8045ce026a147cf07`, PulseLib
`9e0640964945ad5903a4fff1c5091ebf71a69810`. Новый реальный merged-burst
контроль сводит два окна к одной измеренной вершине Soma0 и получает
`shared_measured_peak_between_stimuli` при попытке capture certificate.
Это проверка честного отказа, не сходимость или классификация.

Evidence `ab6bd5f109f51ee46e527cefad04358adfa1d8e1`: 193 members,
814392 bytes compressed primary, включая CSV полной native пробы, JUnit,
runtime mappings и закрытие всей группы. Дополнительно 7/7 тестов reader
прошли на настоящих трассах Elder, включая повреждения данных. Независимая
[metadata-сверка](AssignedVertexSDKVerification.json) подтвердила каждый
archive member и 782 source hashes против Git. Старые runtime неизменны.
Численных локальных проверок не выполнялось. ASan SDK gate на M40 ещё
выполняется; визуальный отчёт этого нового контрольного случая ещё не готов.

Изменения остаются в
`codex/timelearner-assigned-peak-ownership`; merge в develop не выполнен.
Этапы 6/7 и полный план остаются незавершёнными.
