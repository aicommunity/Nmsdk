# Frozen-проверка трёх новых отвлекающих паттернов

Статус: протокол объявлен до исполнения; bounded Windows prepare подтверждён
живым. Результата новой классификации пока нет. Это часть этапа11, не закрытие
полной научной матрицы или всего плана.

Зафиксированы recognition revision
`3e7234958d0539f9ee022580ab6149ea4255cb5536a6c9123e75f226ba9d7985`
и threshold0.09874840158355691. Никакого нового Train, выбора модели или порога.
На исходной матрице фактический native Test и полный audit дали TP1/FP1/FN0/TN6.
Полный исходный и новый native corpus опубликован во внешнем архиве:
[проверяемая квитанция](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/baseline-and-fixed-threshold-native-primary.archive.json).

## Заранее объявленные пробы

| ID | Метка | ISI, секунды | Участие в прежней матрице |
|---|---|---|---|
|seen-target-control|target|0.01,0.08,0.16,0.24|Да: положительный контроль|
|heldout-permutation-1|foil|0.01,0.08,0.24,0.16|Нет|
|heldout-permutation-2|foil|0.01,0.16,0.24,0.08|Нет|
|heldout-permutation-3|foil|0.01,0.24,0.08,0.16|Нет|

Новизна проверяется по pattern hashes всех восьми calibration rows; target
должен точно совпадать с исходной целью. Это оставшиеся перестановки трёх
межимпульсных интервалов target. Положительный контроль уже использовался
при калибровке; три foil не использовались. Одна детерминированная модель
и три новых foils не доказывают обобщения на произвольные паттерны и не
являются независимыми обучениями.

Протокол:2000Hz,2с/reset-per-trial,4001 samples на пробу, полный response
window от onset; фактические спайки и времена входов, отдельная проверка
ответа до/после последнего входа. Native conversion identity; весь полный
stopped source и исходный threshold100 сохранены, intervention ровно один.
Состояние Train остаётся BudgetExhausted, certificate=None.

Controls`fd140bbbca5435dfbcc282ebdc5297bdae7c7262`:
`C:/Projects/TimeLearnerWorker/controls/elder-frozen-heldout4-a1`.
Job`windows-elder-frozen-heldout4-a1`, native Root28f748a/Pulse5f8,
Python actor7207184. Prepare20GiB, native16GiB, audit20GiB; каждая фаза
bounded3600с. Предыдущие runtime и Test не меняются.

До приёмки нужны native execution, полный common source/model/scorer audit,
неизменность исходного источника и распознающей модели, закрытие процессов,
внешний primary и временные графики всех четырёх проб. Любое нарушение полноты
либо frozen revision запрещает положительный итог. Обнаруженные FP сохраняются;
новый порог по этим ответам не выбирается.
