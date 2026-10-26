# История и уровень доказательности

## Август

Визуально подтверждённые 4/8, 5/8 и 6/8 сохраняются как валидные наблюдения
исходного протокола. Saved-state replay, cold retrain и перенос на другой порядок
или ITI проверяются раздельно. Новый strict gate не отменяет старую точность.

| Контроль | Root commit с согласованными gitlinks | Источник |
|---|---|---|
| Phase A 4/8–6/8 | de02a3809395dd0bbd11e2ba792bfc04a51c89f3 | Bin/Configs/SpikeSamples/StructTrain/SelectivityPhaseA/REPORT.md |
| PSI k-sweep | bf2a68955c83b2540e1bc68d00aaa63eefa6541b | Bin/Configs/SpikeSamples/StructTrain/SelectivityPresynapticInhib |
| Branch amp-eq/NextSeg | 50b0cac1ade4f468be82a3d35e4ac6f5514ceb56 | Bin/Configs/SpikeSamples/StructTrain/TimeNeuronTimeLearnerBranch/Train/REPORT_ampeq_nextseginh.md |

Phase A прямо отмечает зависимость LTZ peak от порога: offline threshold sweep
по spiking trace не предсказывает корректно повторный запуск с новым порогом.

## Волны аудитов

Август: Phase A, PSI, Branch, FastResponse/FastSpan, LTZ calibration, AsymRm.
Сентябрь: PHASE5–12, изменение gate, PostTune и cold/load/reset проверки.
Октябрь: AmpNorm EOL, resistance bounds, SoftCold 49, расширенная матрица,
диагностика Classic N1, измерения кабеля, E05, NSR/NSC и D.
Для каждой волны необходимо отдельно восстановить версии кода, критериев и
Train/Test artifacts. Число PASS из разных gate не суммируется.

## Root 895dea071600eafe489c97dffc8147383587e51c

Коммит меняет три отчётных файла, 23 добавления и 7 удалений; raw results не
добавлены. Численные сводки требуют привязки к опубликованным артефактам.

- NSR_E1_b_N1_f1_r2 имел resync_count=0 в прежней записи: это не испытание
  выполненного resync. Позднее описание «no effect» не усиливает этот вывод.
- NSR f2 хуже f0 в конкретном случае; общая невозможность не доказана.
- NSC_E1_b_N0_t1 не завершил обучение, Test оставался шаблонным. Причинный вывод
  о вреде C-trim требует валидной парной проверки.
- NSR Branch frz invalid: параметр Classic отсутствует в Branch.
- Classic E5 N0/N1 имеют одинаковые L, но разные Rs; сравнение полного результата
  не состоялось из-за незавершённого Train.
- WIP e05_job 552ce27 применялся к заданиям .17, стартовавшим после 11:20; ранний
  f1_r2 нельзя автоматически приписывать этой версии.
- D остановлена 25.10 в 11:22. Невалидная постановка не является отрицательным
  научным результатом.

## Подтверждённые code findings

| ID | Компонент | Свидетельство | Требуемая проверка |
|---|---|---|---|
| TL-001 | Branch AllSynapsesNormalized | проверяет ActivePulseIndex; -1 оставляет пустой gate | испортить ранее committed input, fresh verify |
| TL-002 | Branch parallel conversion | mutable bool, повторное включение training сбрасывает его | save/load, повторный conversion, clipping |
| TL-003 | Branch PostTune rebuild | parent C или fallback 1e-9 | heterogeneous storage roundtrip |
| TL-004 | C trim | baseline читается из parent C | эквивалентная child physics |
| TL-005 | StructuralAmp tracker | знак вместо амплитуды, неполный revision | drift, C/dt invalidation, несколько brackets |
| TL-006 | scorer | исходный дефект target row0, incomplete/duplicates/bad tokens | исправленный scorer/collector проверен на этапе 3; сквозная интеграция runner открыта |
| TL-007 | queue fingerprint | stall_autosave_n отсутствует при восстановлении | production serialization roundtrip |
| TL-008 | process limiter | только точное имя executable | suffix binaries, owned PID |
| TL-009 | publisher | push check=False и rsync | child push failure, Git closure |
| TL-010 | Rdk UNet XML property order | scalar L=3 восстанавливалась как 0 после setter StructureBuildMode | code fix + native scalar growth/XML и общий setter regression; подэтап 4.6 |
| TL-011 | Rdk UStorage cleanup | native события Parent, Child, Child при одном ClearObjectsStorage | code fix: корни ownership forest; failing/passing baseline в s04-profiles-elder1 |
| TL-012 | Rdk channel destruction | ASan: NPulseGenerator::AReset читает Environment после его delete в ChannelDestroy | code fix + runtime ASan 122 cases, pooled probe и failing baseline опубликованы в s04-profiles-m40 |
| TL-013 | PulseLib membrane index | fresh/Load одинакового графа давали разные порядки Membranes | native Build формирует индекс по таблице детей; полное identity source/restored, seven cases и raw baseline в s05-identity-* |
| TL-014 | Rdk UStorage::DelClass | два ASan heap-use-after-free: чтение удалённой фабрики и списка возвращённых экземпляров в b15f4384c4516c865afc59a83b487acd477744d0 | исправление 2317f3147c1193dbe2097ea2a242c8d0ab7b049b; 7 native controls и 4 CTest на обоих серверах, M40 под ASan; s05-cleanup-*; общая transaction импорта ещё не реализована |
| TL-015 | Classic live BuildStructure | новый Neuron Ready=true/Init=false; реальные Dataset edges, но нулевые soma/references до extraction | PulseLib ccb399c6bdcdace2814833155416ca82ab736ec2: native Init нового поддерева; восемь bounded native controls и четыре CTest suites на обоих серверах; LiveRebuildInit.ru.md |
| TL-016 | effective frequency legacy creation/growth | model/controller=20000 после двух пачек не означает uniform tree: Classic N1 на M40 15 nodes×20000 + 64×2000 | Rdk 9cb00e640f857b4533518669c8ada01c80efc44e: global-rate attachment и Environment policy; 5 native integration + 3 Rdk controls, 4 CTest и два N1 growth controls на обоих серверах; s04-frequency-final-*. OpenProject/CloneChannel multirate и полная матрица ещё требуют проверки; FrequencyContract.ru.md |
| TL-017 | pooled Environment assignment | native profile copy expected TimeStep type=769, actual=513; isolated checks проходили, full suite падал | Rdk 33e8b3a1114cafd065d4088477e55900297af90a обновляет только метаданные при SetEnvironment; исходные failures и passing full CTest на обоих серверах; ProbeMeasurement.ru.md |
| TL-018 | class-image identity and mode switches | одинаковая физика вызывала image_name_collision после individual→global | Rdk e7690e4a1c0b769951409176c1c2c7bae819181f: process-local descriptor v2 нормализует только visibility TimeStep; native transitions и запрет другой численной частоты; failing baseline и M40 ASan сохранены |

Эти findings являются результатом проверки кода. Runtime-causality и исправление
не считаются доказанными до соответствующих серверных тестов.
