# N1: допуск кандидата в совместном поиске геометрии, Rs и C

Статус: реализовано, новые регрессии ещё не выполнены. Это продолжение
[исследования соседних длин](N1TimingNeighbourhoodReview-20261117.ru.md),
а не новая математическая цель обучения. CapturedPerInput, опорный вход,
физика, исходные допуски и отдельная финальная проверка сохраняются.

## Что выявил Windows-прогон

SDK Root `ddb2dcadd33ddd683cf73662f306c2bc6383e325` / Pulse
`eb5c07b0bd56897e4b67d2e644d066ee6340fe11` скомпилирован. Исходная
сборка не принята: после успешного linker exit оставался дочерний процесс.
Production backend закрыл его; отдельный closed-build audit прошёл.
Это разрешило независимую проверку бинарника, но не переписало отрицательный
результат исходной сборки.

Фактически выполнены 216 случаев: 215 прошли, один упал. Все четыре новых
случая timing-neighbourhood / candidate-pair budget прошли отдельно.
Набор целиком не принят: дополнительно ожидались 217 случаев, хотя один
закрыт `#ifndef Q_OS_WIN`. Ошибка декларации относится к подготовке Windows
cohort; Linux обязан выполнить этот случай. Изменять строгую проверку JUnit
или считать отсутствующий случай пройденным не требуется.

Упавший `EmptyBranchIntervalsDoNotCreateRedundantDomainContexts` ожидал
одну domain-оценку, но получал две. Его provider объявлял другую physical
preview revision при тех же скалярах. Для настоящего no-op он должен
возвращать исходную revision; это исправление контракта fixture.
Отдельные новые регрессии ниже проверяют собственно дефекты алгоритма.

## Исправления production-контроллера

1. Признак productive Rs pass устанавливается после допуска кандидата,
   после проверки дублей между C-контекстами. Предложение, отброшенное как
   дубликат, не покупает новый проход Rs и дополнительные domain-запросы.
2. Ключ совместного native N1 кандидата включает физическую preview revision.
   Равенство L/Ns/Rs и C ещё не доказывает равенство реальных связей,
   выделенного графа и дочерней физики. Разный preview требует штатных
   edit/readback и новых anchor/input измерений. Для N0 и standalone режима
   без native domains прежняя семантика ключа сохраняется.

```text
propose a finite geometry/Rs candidate in its C cursor
obtain its native physical preview identity
if (parameters, effective C, physical preview) was already admitted:
    advance C cursor; do not mark its Rs pass productive
else:
    record admitted candidate; mark its Rs pass productive
    realize any changed physical preview through the native adapter
    measure a fresh anchor/input pair
```

Файлы: `PulseLib/Core/TimeLearner/BoundedTraining.{h,cpp}` и
`Tests/Integration/Libraries/Test_PulseLib_CapacitanceContexts.cpp` в корне.

## Проверки и ограничения

Новые production-session cases:

- `DuplicateCProposalsDoNotStartAnotherResistancePass`: baseline и два
  C-контекста с пустым Branch-интервалом; L2 явно unavailable. Проверяет
  точное число оценок, отсутствие edits и ложного Exact.
- `EqualScalarsCannotSuppressADifferentNativePreviewModel`: одинаковые
  скаляры и C при другом physical preview; требует реального edit и новых
  evidence с другой revision.

Это controlled-response проверки настоящих session/recorder, не проверка
физического отклика нейрона. Их надо выполнить вместе с полным затронутым
cohort: 219 literal TEST на Linux, 218 на Windows. Единственное Windows
исключение должно явно указывать исходник, SHA и `#ifndef Q_OS_WIN`:
`NativeJobSourceTransport/SymlinkSourceCannotReplaceTheOwnedSnapshot`.
Legacy TEST_F fixtures не входят в этот узкий cohort и остаются в физической
матрице. Новые SDK строятся отдельно; два работающих cold Train не меняются.

Полное terminal best-state восстановление, разделение модели/истории,
all-input сходимость и actual frozen8 Test этим изменением не закрываются.
Merge в develop допускается только после соответствующих проверок.
