# Парное сравнение поиска на разных версиях кода

Production CLI:

```text
python -m Scripts.StructTrain.TimeLearner stock-recovery-compare BASELINE CANDIDATE --output NEW.json
```

Оба входа — каталоги полной восьмиусловной stock recovery серии. Новый анализ
не исполняет модель, не выбирает порог и не меняет исходные данные. Он нужен
для сравнения Pulse416 с opt-in fair-domain traversal при неизменной задаче.
До дорогого нового Train следует проверить декларации через `match_designs`;
полный CLI требует также законченных preflight/Train manifests и primary.

Сначала штатный `audit_design` проверяет каждую матрицу, подписи, исходные
шаблоны, пары retry/advance и ConditionSpec. Затем условия сопоставляются по
topology, initial threshold и recovery policy. Положение строки и имя case
не являются scientific identity. Между соответствующими условиями сравниваются
все поля Train job, кроме sha-подписи и attempt run_id; отдельно сравнивается
полный expected cold graph. Нельзя незаметно изменить bounds, budgets,
tolerances, целевой паттерн, reset/stimulus protocol или физику.

Разные code identity и runtime fingerprints сохраняются раздельно: это
объявленное вмешательство в реализацию, а не изменение training declaration.
Сами fingerprints не переписываются и не объявляются равными. Проверка не
доказывает, что между версиями изменена только одна строка алгоритма: для
причинного вывода дополнительно требуется Git diff и runtime/source closure.

Перед выводом сравнения обе серии проходят полный production audit:
native package/CSV/context/physics, затем существующий coverage reader.
Сохраняются measured counts, отказы, причины остановки и hashes конкретных
моделей/summary/run manifests. Невалидная либо незавершённая серия не получает
положительный итог. Stopped-state остаётся отрицательным результатом Train.
Это сравнение обучения и зарегистрированного поиска, не оценка классификации.

Одинаковые run-manifest hashes явно обозначаются как `same_attempt`.
Сравнение серии с собой не создаёт восемь новых повторов. Разные manifests
также не доказывают независимость случайных повторов. Exhaustive feasibility,
успешная классификация и scientific PASS из этих данных не выводятся.

Подготовлены шесть серверных checks: actual self-comparison полного native
корпуса; перестановка design rows; две внутренне валидные матрицы с другими
sweep budget/length bounds; наличие только design без native results;
CLI отказ при существующем output и отсутствующих primary. Это проверки
анализатора, не новая Train серия. До server receipt они остаются pending.
