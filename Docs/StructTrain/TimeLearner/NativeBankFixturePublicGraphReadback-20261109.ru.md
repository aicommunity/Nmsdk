# Native bank fixtures: доступ через публичный граф

Статус: исходники подготовлены, компиляция и выполнение не проводились.
Code commit `029c720a8cff5c9c082d1cb318b60632c5546748` — обычный потомок
Root `f015db2d4f6ac8c239e07c050ff596524604060c`. Pulse gitlink остаётся
`f7a0e3e63ec29d4647790a695606d1ca32164ef3`; production-файлы не менялись.
Работа выполнялась в отдельной ветке `codex/timelearner-public-bank-descriptor-fixture`.

Предыдущий actual37A3 собрал Pulse library, затем отказал при компиляции test TU:
три обращения к protected `NativeProbeModelBindings` и два `EXPECT_THROW` на
одной физической строке. Исходный отрицательный запуск сохраняется отдельно.
Этот patch не является его повтором или подтверждением исправления на сервере.

## Изменения

В `Test_PulseLib_CompositeTraining.cpp` добавлен fixture-local
`ObservedBankBindings`. Он формирует публичный `NativeProbeBindings` как
read-only DATA для существующих production helpers:

- owner, neuron, dataset и input count получаются из реального owner через
  публичные свойства и `GetComponentL`;
- в подготовленной Branch-пробе рекурсивный обход реального neuron через
  `GetComponentsList`/`GetComponent` находит синапсы, чьи фактические Input
  connections ведут к `DatasetMatrix.Generator1.Output`;
- подготовленная Branch-проба в этом fixture обязана иметь ровно один такой
  синапс; ожидаемый ordinal или bank path не участвует в его выборе;
- descriptor создаётся заново при каждом обращении, не сохраняет прежние
  child pointers между изменениями модели или lifecycle boundaries.

Область применения явно ограничена текущими fixtures: Ns=1 у каждого входа,
пустая declared inhibition policy. Перед пробой actual Ns и memberships
продолжают проверяться `ReadNativeCandidateWindowPhysical` и независимыми
ожиданиями из fixture model specification. Для расширения на Ns>1/inhibition
нужно отдельно определить полный порядок наблюдаемых members и новые controls.
Это ограничение test adapter, не утверждение о невозможности такой физики.

`ActualBankData`, `ActualDistinctBankRouting`, `ActualWrongSelectorDataIsRejected`
используют этот descriptor вместо protected getter. Сами
`ReadNativeCandidateWindowPhysical` и
`ValidateNativeCandidateWindowPreparedSelector` не изменены. Сохранены проверки
declared attachments/bank paths, фактических connections каждого входа,
selected ordinal, effective identity, N+2 closure и восстановления исходного
графа, а также отрицательный контроль с подменённым descriptor member.

В `ReferenceAndLegacyTokensCannotEnterWindowFinal` два `EXPECT_THROW` перенесены
на разные строки без изменения проверяемых выражений и исключений. Это устраняет
коллизию GTest labels, использующих `__LINE__`.

## Граница доказательства

Observed descriptor свидетельствует о прочитанном графе. Он не утверждает
доступ к private executor list, не создаёт live authority и не передаётся в
`NativeProbeExecutor`. Фактический native attempt по-прежнему использует private
production bindings, scheduler hooks, owner lifecycle/control guards и прежние
правила admission. Новых friends, публичных методов, derived learner classes,
`const_cast`, вложенных Calculate или записей параметров нет.

Ровно один C++ файл изменён. Набор TEST IDs не увеличен: непосредственно затронуты
10 существующих `NativeCandidateWindowBanks.*` и
`NativeCandidateWindowTrainingCore.ReferenceAndUnqualifiedLegacyApiCannotArmFinal`.
Точные IDs, строки и Git-byte source fingerprint приведены в соседнем inventory.

Локально выполнены только проверки Git diff, source IDs и расположения macros.
Компиляция, numerical/unit tests, SDK/source projections и серверные команды не
выполнялись. Перед серверным повтором обязательны сохранённый negative37A3,
root source review, новый точный compiled inventory и production preparation.
Будущий runtime2 gate14 должен включить этот общий test-only fix обычным merge;
его прежние immutable pins и отрицательные evidence не переписываются.
