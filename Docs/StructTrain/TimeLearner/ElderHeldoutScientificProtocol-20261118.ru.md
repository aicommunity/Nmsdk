# Frozen-проверка трёх новых отвлекающих паттернов

Статус19.11: actual native Test и полный common source/model/scorer audit
завершены успешно; все4 полных окна valid/frozen. TP1/FP0/FN0/TN3. Модель и
порог после новых ответов не менялись. Это часть этапа11, не закрытие полной
научной матрицы или всего плана. Временные графики этих4 проб ещё не приняты.

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

Объявленные проверки native execution, common audit, неизменности источника и
модели и закрытия процессов пройдены. Native1420.02с, audit1437.16с, exit0,
соответствующие kernel Job/PID отсутствуют. Все окна имеют4001 sample.
Seen target дал один спайк0.4925с, через2.5мс после последнего входа; все3
новых foil дали0 спайков. [Полная квитанция](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-common-audit-closed.json).

Полный primary опубликован в M40 CAS:126928729 bytes,70 проверенных members,
3200472564 expanded bytes. Проверены ссылки на исходный Train и предыдущую
калибровочную публикацию. [Каталог и SHA256](../../../Reports/StructTrain/TimeLearner/SingleSweepBranch-20261118/frozen-heldout4-primary.archive.json).
Остаются визуальная отчётность и включение в следующий выпуск DOCX.
Исходный FP на phasea-row-4 сохраняется; новый порог по этим ответам не выбирался.
