# Ранжирование измеренных кандидатов при нулевых и малых допусках

Source review общего BoundedTraining::Rank выявил потерю различий: ненулевая
ошибка при tolerance=0 превращается в infinity. Для положительного очень
малого tolerance деление также может переполниться. В обоих случаях лучший
измеренный остаток может проиграть исходной геометрии по parameterChangeCost.
Это дефект порядка поиска/выбора, не основание расширять допуски.

Отдельная ветка от develop включает незавершённые search/diagnostic prerequisites
через merge commits. На M40 прежний ASan163 не меняется. Перед correction
нужен реальный серверный failing baseline через production BoundedTrainingSession
и ProbeRecorder. Первые8 tests содержат20 измеренных сценариев:
Classic/Branch×N0/N1, sync=0, amplitude=0, оба=0 и положительные subnormal
tolerances с переполнением обычного деления. Проверяются все3 законные
геометрии, fixed anchor/Rs/Ns и fresh negative final certificate.

Требуемый порядок сохраняет readiness timing/amplitude. Для точного нулевого
допуска сравнивать модуль действительного остатка, без epsilon, процента,
timestep или подстановки скрытого численного допуска. Для положительных
допусков конечное нормированное сравнение сохранить; при переполнении
сравнивать тот же положительный нормированный остаток в log-domain.
Стоимость изменения — последний критерий. Exact требует прежних сравнений
с исходными допусками и свежего all-input прохода; лучший отрицательный
кандидат остаётся BudgetExhausted/SearchUnresolved по причине остановки.

Этот документ задаёт ещё не проверенное исправление. Не объявлять все
алгоритмы или этап7 принятыми; нужны baseline, correction, прежние decision
regressions и native controls на обоих workers, с исходными artifacts.

## Первая попытка и уточнение fixture

Baseline ba34e4aa8/Pulse427 дал8/8 failed, compact proof
6ecdff6ab10a9e123173270a845f0e95927a8f28:24 verified members/7894 bytes.
После Pulse225642bd9 первая regression81 дала73/81:8 новых tests ещё failed.
Амплитудные сценарии прошли, временные — нет. Временной fixture ошибочно
ранжировал собственную задержку вместо arrival относительно origin всей пачки.
При исходных delays0.09/0.05/0.04 и anchor arrival0.13 длина2 действительно
была лучшей; это не подтверждение timing-дефекта. Предыдущее утверждение о
меньшем timing residual длины4 пересмотрено; исходные данные сохраняются.

Исправленный fixture использует delays0.19/0.15/0.14 при том же anchor0.13
и явно проверяет измеренные остатки0.06/0.02/0.01 через Evidence контроллера.
Амплитуды и цель не меняются. Нужен повтор baseline с прежним Core427 и затем
того же fixture с Core225; ошибочную попытку нельзя объявлять PASS.

Corrected baseline daefecf61cabff82d8d6983321d17df5abd8d310/Core427
на Elder действительно дал8 expected failures. Все дополнительные проверки
измеренных timing/amplitude residuals прошли; только best length2 вместо4
остаётся неверным. Proof244399829e94bae3d619c858f48431e89ce59505:
26 verified members/8305 bytes. Предыдущая negative regression81 сохранена
в47be80c10851c0f2755f60b3be9a5d049c3bfdc1:380 members/2799815 bytes.

Correction numeric rootfbe7b667faaeb5eb17319d9d3a4a5b8d92c86754/Pulse
225642bd9b3a5651fce2808bd0bef79944d4f1b8 проверяется объявленным gate81:
все50 BoundedTraining tests,5 measured-R,6 measured-L и20 native/archive
controls. Это включает старые positive/negative cases и fresh all-input gate.
Приёмка не выводится из запуска процесса: нужно дождаться полного JUnit.

Этот Elder normal gate завершён:81/81,15/15 JUnit/diagnostic readers и4
production stopped-boundary audits. Proof f9e823ced7d51614a2a1af307405bbdaaac0478f:
384 verified members/2799016 bytes. Все20 чисто контроллерных сценариев теперь
выбирают меньший измеренный остаток. Прежние native20 проверяют интеграцию
и guards, но их законные singleton domains не являются самостоятельной
проверкой нового порядка нескольких физических кандидатов. Такая адресная
native проверка остаётся нужна, как и ASan; подэтап не принят в develop.

Для этого добавлен NativeFiniteRanking:4 настоящих Classic/Branch×N0/N1
случая с L1..3, fixed Ns/Rs/anchor и sync=0. Амплитудный tolerance=1 задан
явно для изоляции timing-rank, а не подтверждения default1e-5. Проверяются
фактический лучший измеренный остаток, чувствительный positive control
«другая геометрия действительно лучше исходной», fresh final verification
и отрицательный certificate. Все training soma/input traces записываются
production recorder. Физический baseline327d8d5d13a42c6e1ebd17eba39af962be69b929
пинует старый Core427; его сборка начата отдельно на Elder. Результат пока
неизвестен; отсутствие улучшения или invalid peak будет явным failure fixture,
а не автоматическим доказательством дефекта ранжирования.

На M40 отдельная новая ASan-сборка использует другое source/build/runtime
дерево; живой07167 ASan163 не меняется. Первая настройка новой сборки
выявила неполную подготовку dependency closure: отсутствовали4 штатных
library submodules. Она остановилась до компиляции tests и сохранена как
s07-finite-ranking-build-asan-a1. Следующая подготовка перебирает все7 paths
из .gitmodules, сверяет точные gitlinks и оставляет HEAD прежнего активного
дерева неизменными. Configure a2 прошёл, сборка и последующий gate81 pending.
