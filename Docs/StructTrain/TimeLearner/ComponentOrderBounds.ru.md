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
for i = index .. result inclusive:
    children[i] = children[i + 1]      # чтение за концом при result=N−1
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
for i = index .. result exclusive:
    children[i] = children[i + 1]
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

Обычная сборка на Elder-1 ещё проверяется. Native learned-state rollback tests
с искусственной ошибкой после attach нового Dataset, полный CTest и обновлённый
ASan подэтап также ещё выполняются. Нет утверждения об успешности запущенных
проверок. Все результаты должны быть опубликованы через Git до принятия Rdk
branch в develop, затем согласованного root merge. Исторические manifests
продолжают указывать свои исходные Rdk SHA.
