# Точка продолжения после остановки пользователем 27.10.2026

Работа остановлена по явной просьбе пользователя из-за остатка недельного лимита.
Цель не завершена. Не запускать новые сборки/эксперименты без возобновления работы.

## Код и Git

- Root: `stage05/native-trained-state`; последний test-only commit перед этой
  записью — `2063e41e1cbd46eee6c2903001d12906d04e71f6`.
- PulseLib: `stage05/native-trained-state`,
  `025d809f7b86cc79e18ddd711c6adc40e2396bf8`.
- Rdk: `stage04/pooled-property-bindings`,
  `1223bcc18cf1ba106e8f8a17f20cce8c000c104d`.
- Bin develop: `f5e1d0200127223981daa71da22cf5ee02fdbc60`.
- Принятые develop: root `68b77ac542cbd21479eab45c474b3603591add97`,
  PulseLib `c1d5b177278f1eb347c1ebc725555837c36642bb`,
  Rdk `ef4f033704d54f11d06e4da2b3518c313f3a9992`.

Текущие feature-ветки ещё не приняты в develop. Публиковать children перед root;
после приёмки использовать --no-ff merge, без rebase/squash/cherry-pick/amend.
Точный root resume HEAD — commit этой записи/следующего финального pause metadata,
его gitlinks остаются указанными выше. Все исходные commits опубликованы.

## Остановленные проверки

Оба `s05-pooled-full-a1` остановлены SIGINT строго по фактическому executable
`/home/user/timelearner-refactor/runtime-s05-pooled-full-a1/Test_PulseLib_StorageComponents`.
На .11 остановлен PID 2122497, на .17 PID 3533854. CTest штатно сохранил logs,
LastTest и terminal exit=8 с PulseLib INTERRUPT; три быстрые suites прошли.
Это **interrupted_by_user**, не PASS и не новая регрессия алгоритма.

Run source: root `f3b45cb9300e4dd43f9d4c4d212e366b75195af1`, Rdk `1223bcc1…`.
Каталог обоих workers: `/home/user/timelearner-refactor/readbacks/s05-pooled-full-a1`.
Сохранены user-stop.json, runtime/binary manifests, partial primary data и логи.
Их Git-пакеты: `Reports/StructTrain/TimeLearner/pause-20261027-elder1` и `-m40`.
Незавершённый parent gtest XML может отсутствовать: его нельзя достраивать как PASS.

Предыдущие full A9 (.11) и A15 (.17) закончились до исправления Rdk с одинаковыми
15 learned-state failures. Они опубликованы в s04-property-bindings packages.
На исправлении уже проверены 18/18 unit .11, 18/18 ASan .17,
30/30 builder→learned-state integration .11, 9/9 Python и первичные данные.
Подробности: PooledPropertyBindings.ru.md. Full acceptance всё ещё открыта.

## Новый test-only reproducer: ещё не запускался

Root `2063e41e…` добавил TimeLearnerNativeLifecycle.ClassicAuditFlagDefaultAndReuse
и BranchAuditFlagDefaultAndReuse в Test_PulseLib_LifecycleContracts.cpp.
Они проверяют actual UProperty, native Build/Reset, explicit Default и Return→Take.
Повод — code finding: EnableTrainingAudit не устанавливается в learner ADefault.
**Baseline не запускался; production fix этого default ещё не сделан.**
Не считать тесты прошедшими и не считать code finding подтверждённым runtime.
Следующий шаг: получить baseline в отдельном свободном checkout; затем при
подтверждении исправить ADefault обоих learner, проверить сохранение explicit
audit при обычном Reset/Build и cold default при reuse. Не менять общий Rdk
контракт property assignment ради локального setter.

## Приоритет продолжения

1. Проверить чистоту деревьев и опубликованные refs; перечитать CurrentStatus.
2. Закрыть новый audit-default reproducer адресными проверками.
3. Повторить post-fix full suite в **новых** out/runtime каталогах (A1 сохранить).
   Никакого автоматического продолжения частично записанных научных наблюдений.
4. После общей приёмки: Rdk feature → develop; PulseLib → develop; root с exact
   gitlinks → develop. Не объявлять полный этап 5 закрытым этим подэтапом.
5. Продолжать недостающие diagnostic/budget/external-stop state transport,
   configured retarget, алгоритмы, conversion/PostTune/calibration, production
   CLI/runner/publisher, миграцию scripts и научную матрицу полного плана.

Code catalog теперь покрывает все 211 исходных и шесть новых configured
properties; PropertyReview.coverage.json сверяет их с 217 текущими declarations.
Это не runtime/property acceptance. Полный ledger истории и 324 script candidates
ещё не разобраны до завершения. Августовские 4/8–6/8 сохранены, 8/8 не является
условием приёмки, серия D автоматически не возобновляется.

## Серверы и каталоги

Workers user@10.245.1.11 и user@10.245.1.17 через user@10.245.1.12.
Credentials не записывать в repo. Синхронизация источников/результатов только Git.

- .11 full source/cache: source-order-fixed-a1 / build-order-fixed-normal-a1.
- .17 full source/cache: source / build-s02.
- .17 отдельный ASan source/cache: source-order-baseline-a1 / build-order-baseline-a1.
- Общая база: /home/user/timelearner-refactor.

Перед любым обновлением checkout/cache проверить actual live processes; не
трогать /home/user/Nmsdk и /home/user/tl-agent/Nmsdk. Существующие runtimes
и результаты сохранить. Все численные/интеграционные проверки выполнять на workers.
