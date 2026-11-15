# Совместная ветка controller / managed pipeline: приёмка ожидается

Это интеграционный candidate, а не новый принятый develop. Исходная принятая точка — root `ba47396bc3e99c5012aa4eb8ce6de6b597a7cd42`, PulseLib `9ec4566d71bf56d4eeb5c8a920bbc683fcd85299`, Bin `11ad066eac74d26c3e71e471c8a5998323e79176`, Rdk `10e9d05aa658dd2203c89bc84ba9166595b50014`. Все исходные этапы 1–12 остаются частичными.

Через два настоящих merge commits в отдельной ветке соединены root `2cb855677f3e7160cd01837f62c649b18803ebf0` (PulseLib `f6a917d395b21610f6bf6cbb0ed945e6cdee31dd`, общий lifecycle/recognition helper и test-only Owner source) и package `8c9ee9f6b319a06224d6ebdcdd537b88e993fc4a` (managed coordinator/live routing/reconciliation/declaration/runtime role guard). История не переписывалась; cherry-pick и squash не использовались. Candidate merge `bcf060f5fffc9d05ddf045346db56729dd8acf9c` предшествует этому документу.

Ручное разрешение потребовалось в двух файлах. В __main__.py сохранены обе независимые группы parser: controller-ab/controller-kernel и pipeline. Статически проверены отсутствие повторяющихся command names и включение всех прежних literal choices обоих родителей: 25 commands, ни одна прежняя опция не потеряна этим разрешением. В ManagedDeclarationPreflight сохранена поправка historical fixture null→{} и ясно отмечены старые pending формулировки. AST всех 317 Python files разобран локально; это не runtime-проверка.

[Сверка Git/AST](IntegratedControllerMergeReview.json): App, Tests и корневой CMakeLists.txt побайтно совпадают с 2cb. Bin отличается от его 99f snapshot только удалением 26 исторических scripts и изменением 7 markdown documents; ресурсы физических моделей не менялись. Отдельная рабочая среда 2cb всё ещё проверяется на Elder и не обновляется этой интеграцией. Нельзя назвать старый executable сборкой нового root, даже при равенстве relevant source trees: runtime manifests должны сохранять фактический compiled root, executable/library hashes и resource origin.

## Обязательные следующие проверки

1. Завершить неизменяемые joint ASan304 и его fresh-process owner8/readers128 на SDK802/Pulsecc; focused ASan44 уже принят отдельно. Leak detection выключен, отсутствие утечек не заявляется.
2. Завершить old-condition A/B восьми Owner cases и независимый133 на old candidate4f/Pulsef6. Предварительно failures и112 CSV совпали; Owner positive contract этим не проверен.
3. Отдельный SDK2cb должен реально пройти new-source Owner8 и полный133. ISI [.01,.03] является явным условием теста, а не изменением допусков/алгоритма; никакой certificate не подставляется.
4. Проверить именно интегрированный Python package: CLI inventory/role refusal, recovery/declaration на настоящем completed corpus, reservations/worker dependency/contained-runner controls, public coordinator8/live6 и measured calibration/frozen paths. Старые package8c receipts относятся к 8c, а не автоматически к этому merge.
5. Выполнить свежую согласованную серверную сборку интеграционного root и необходимые регрессии с точными child gitlinks. Повторное использование внешнего immutable resource root допустимо только с явно сохранённым origin и сверкой применяемых ресурсов; обновление активного runtime запрещено.
6. Сохранить полные необходимые primaries/модели/метрики и выбранные временные графики всех предъявленных паттернов. Полный воспроизводимый plot cache — на M40 Data. Отсутствующие/pending данные не повышаются до completed, Exact или scientific PASS.

Только после адресной приёмки — merge PulseLib в develop, проверка доступности его commits, затем root merge с точными gitlinks. Это не отменяет оставшиеся property/mode/storage/physics, ConditionSpec/fault/publish, legacy и научные пункты полного плана. Августовские 4/8–6/8 остаются результатами исходного протокола; 8/8 не является условием завершения рефакторинга. Series D не возобновляется.
