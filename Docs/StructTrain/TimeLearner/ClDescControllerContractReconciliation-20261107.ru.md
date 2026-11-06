# ClDesc: контроллеры и legacy experiment, 07.11.2026

В Bin исправлены описания двух TimeLearner: общий текст класса и пять свойств
ControllerVersion, ControllerConfiguration, ExperimentMode, ExperimentNum,
StructureBuildMode. Изменены только 12 узлов Description; имена, типы, пути,
списки значений и остальные XML-узлы сохранены. Численный код и runtime не менялись.

## Что уточнено

- Отсутствующий ControllerVersion означает legacy1; V2 выбирается явно.
  Проверка 1/2 относится к штатному setter, не доказывает все connected/direct пути.
- JSON schema1 поддерживает N0/N1; schema2 задаёт N0 repeats2..128.
  Расширения3/4/5 описаны как возможности отдельного candidate SDK, а не
  принятого PulseLib develop. Точный SHA сборки определяет доступность схемы;
  номер JSON не является номером контроллера.
- Experiment() пуст в обоих TimeLearner. ExperimentMode и ExperimentNum не
  выбирают действующий научный сценарий, но имеют setter side effects.
  В частности, ExperimentNum включает CalculateMode=1, CountIteration=0,
  IsFirstBeat=true и IsFirstFileStep=true. No-op алгоритм не означает no-op setter.
- Learner StructureBuildMode0/1 не смешивается с neuron0/1/2. Configured V2
  создаёт модель через ModelSpec/native import, а не legacy BuildStructure.
- Окончание управления и качество классификации описаны раздельно.

## Основания и приёмка

[Структурная сверка и полные SHA](ClDescControllerContractReconciliation-20261107.json)
содержат hashes обоих прежних/новых XML и пяти проверенных исходников PulseLib.
Каждый XML разобран; после восстановления шести старых Description его дерево
полностью совпадает с исходным. Существующие серверные normal/ASan gates не
выдаются за новую проверку ClDesc или всего публичного интерфейса.

Bin feature680564e2 объединён в develop merge commit
fc67a3b0958e8becdfbe1cd3f0e4e054d966d54f и опубликован раньше корневого gitlink.
Корневая ветка начинается от develop9b380a3e: pending C++ features этим изменением
в develop не переносятся. Принятый PulseLib остаётся0ec9193e, поддерживающий
cold configuration1/2; расширения просмотрены по candidate2f6b5725.

Это адресная актуализация пяти свойств и двух классов. Полный semantic/runtime
аудит217 свойств, все ClDesc, режимы физики и этап12 остаются незавершёнными.
Научных результатов это изменение не добавляет.
