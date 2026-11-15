# Исправление control fixture на границе C-cursor budget

Source-only follow-up от frozen
`1292babb67ee653d04316f7f6927a3d23d5d682c`; production Python/C++ математика,
runtime2 schema, физика и критерий измерения не меняются. Локально только
AST/Git/text checks; исправленный test ещё не исполнялся.

Исходный серверный gate73 выполнил 73 methods: 72 PASS, 1 FAIL, zero errors/
skips. `test_C_region_and_context_count_limits_are_checked` ожидал исключение
на `maximum_cursor_elements=271`, но оно не возникло. Whole10 synthetic joins
прошли только в DATA scope; full73 не принят. Original source1292, plan03b7 и
failed raw run сохраняются. Новая A2 preparation/dispatch допускается только
после pin исходного negative evidence и отдельного review/authorization.

Причина в test expectation. Общий C++ owner
`BoundedTraining.cpp::ValidateCapacitanceSearchPolicy` и Python runtime2 validator
оба считают:

```text
lengths = min(maximum_candidates_per_input, maxL-minL+1)
counts = maxNs-minNs+1                  # N0
contexts = 1 + unique seed inventory
reserve = maximum_cursor_elements // contexts
```

Fixture получает `maximum_candidates_per_input=4`, L bounds1..8, Ns1..128.
Следовательно lengths=min(4,8)=4, counts128, итого132. Constant unit domain
даёт один уникальный seed и плюс один baseline, то есть contexts2.
При271 reserve135 достаточно, отказ был бы ошибкой production validator.
Корректная соседняя граница — **264→reserve132, допустимо; 263→reserve131,
отказ**. Она продолжает различать ошибочные baseline/context counts и
неправильное игнорирование candidate limit.

Патч меняет только эти два test values/comment и добавляет явные asserts
исходных fixture limits, чтобы будущая смена helper declaration объяснялась
на месте. Assert ожидаемого `C_cursor_budget` сохранён; проверки production
не понижены. Полный actual service5/runtime2/archive2 gate остаётся отдельным
обязательным пунктом даже после будущего PASS73.
