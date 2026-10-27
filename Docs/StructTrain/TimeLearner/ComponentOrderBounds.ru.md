# Границы штатного перемещения компонентов Rdk

На этапе проверки транзакционного импорта обнаружен общий дефект
`UContainer::ChangeComponentPosition` и риск переполнения аргументов
`SetComponentPosition`. Исправление находится в Rdk, а не в learner.
Это не утверждение о причине августовских результатов.

## Дефект и исходная проверка

Rdk test-only commit `e2bcd8da5bab016bd3fd703c42e519e56b633081`, root
`892fa5ee96ef9e399a8495940841ec6b2a65f213` сохраняют исходный production body:

```text
result = index + step                  # int может переполниться
if result > index:
    for i = index .. result inclusive:
        children[i] = children[i + 1]  # чтение за концом при result=N−1
children[result] = moved
```

В отдельном Git checkout на M40 выполнен реальный native Rdk target
`Test_UContainer_Components`, без извлечения тела метода в тестовую копию.
В A2 крайний положительный step даёт failing order assertion; forward-to-last
на двух компонентах вызывает `AddressSanitizer: heap-buffer-overflow`.
Оба ненулевых exit codes и полный sanitizer stack сохраняются в
`/home/user/timelearner-refactor/readbacks/s04-order-baseline-a2`.

A1 остановилась до тестов: в новом CMake cache не был включён BUILD_TESTING.
Эта ошибка подготовки сохранена отдельно; A2 явно включает BUILD_TESTING.

## Исправление и контракт

Rdk `2cfda44d738f6291914217dba9cd223acae35bfd`, root
`eb82f7f7084b8bc84020ea9994648cd56221369d`:

```text
reject invalid source index
destination = wide_integer(index) + step
result = clamp(destination, 0, N−1)
if result > index:
    for i = index .. result exclusive:
        children[i] = children[i + 1]
else:
    for i = index down to result exclusive:
        children[i] = children[i − 1]
children[result] = moved
invalidate active order cache and rebuild ID lookup

absolute position:
    reject invalid source index
    position = clamp(position, 0, N−1)
    move(index, position − index)
```

Порядок, IDs, active cache и прежнее ограничение позиции границами сохраняются.
Lifecycle методов Build/Reset/Calculate не изменяется. Прямое восстановление
объектов после импорта продолжает использовать штатные native методы порядка.

## Доказательства и оставшаяся приёмка

M40 A1 fixed: **13/13 native UContainer tests прошли под ASan**, detect_leaks=0,
без skips/errors/failures. Включены три новых случая: forward-to-last с проверкой
объектов, IDs и active order; максимальный положительный step; минимальная
абсолютная позиция и недопустимые исходные indices. Остальные десять tests —
имеющиеся Copy/frequency/cache/lifetime проверки.

Обычная сборка Elder-1 также прошла 13/13 без skips/failures/errors. Оба пакета
опубликованы через Git: `Reports/StructTrain/TimeLearner/s04-order-bounds-elder1`
и `s04-order-bounds-m40`. Evidence commits:
`05b6b465da38bd23d3644e1707f932187c966469` и
`0d28c349fc32e409f263c41f4c6b8aaf9a87fcf6`. Локально проверены 26 stored SHA
и 22 raw payloads, включая failing baseline.

Native import rollback на M40 A13/A14 проверяет ошибку после attach нового
Dataset: прежние объекты, порядок, связи и waveform восстанавливаются. A12 дал
ложное расхождение из-за dangling QJsonValueRef самого нового fixture; A13
сохраняет owning JSON и проходит оба случая, production rollback не менялся.
A14 на root `51c54abb95881ced0942e5cfd14928609da00ac6` проходит 5/5 learned-state,
13/13 UContainer и 9/9 Python tests; независимый аудит — 62 training trials и
четыре rollback probes. Повторная обычная проверка Elder-1 и расширенный ASan
ещё выполняются. Нет утверждения об успешности запущенных проверок.

Elder-1 A14 также прошёл 5/5 learned-state, 13/13 UContainer и 9/9 Python tests,
с независимым аудитом 62 training trials и четырёх rollback probes. Rdk branch
принята в develop merge `ef4f033704d54f11d06e4da2b3518c313f3a9992`; его tree SHA
`d5fbbfe16fdd25b6bfdf43bc8349bb5af050cc47` совпадает с tree tested feature commit,
remote develop SHA повторно проверен через ls-remote. Root feature записывает
точный merge gitlink, но PulseLib/root develop ещё не обновлены этим подэтапом.

Полный CTest пока не завершён. Исторические manifests продолжают указывать
свои исходные Rdk SHA; этот узкий подэтап не означает завершения общей
lifecycle/physics матрицы.
