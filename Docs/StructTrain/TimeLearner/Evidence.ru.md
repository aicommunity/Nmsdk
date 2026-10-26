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
| TL-001 | Branch AllSynapsesNormalized | проверяет ActivePulseIndex; -1 оставляет пустой gate | открыто в legacy; отдельный FinalVerificationSession реализует fresh all-input sweep, но production wiring и native N>1 committed-input corruption ещё требуются; FinalVerification.ru.md |
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
| TL-019 | generator emission history | пустая OutputPulseTimes=[0] давала synthetic stimulus t=0; Dataset на четыре импульса читался как пять событий | PulseLib f974a152917a38a5542edc0ed1dc45cd672837bc очищает Single/Multi history вместо нулевого sentinel и исправляет unsafe SimpleLTZone consumer; failing baseline, 6 passing native controls и 4/4 полных CTest suites на обоих серверах, M40 ASan 6/6; ProbeMeasurement.ru.md |
| TL-020 | Multi event publication and dimensions | реальный импульс записывался во внутренний список, но публикация OutputPulseTimes была закомментирована; default PulseCount=0 против Delays=1; dimension setters не обеспечивали перестройку | PulseLib d9b6d1529aa2a1b8d900978ac0d4127103909435: история публикуется, default count=1, Delays согласует count, setters запрашивают штатный Build; native 1→2→1 emission controls входят в 6/6 и M40 ASan; случайный режим Multi остаётся не реализован |
| TL-021 | native probe lifecycle validation | root 2298736b2a801323ffc101f93ef9dfe55161c85d на M40: Neuron.Reset во время Classic/Branch пробы не менял semantic hash, но наблюдение ошибочно оставалось valid; a8 root d5e122b4d32e2fc5214c74ae4e28f1b40edb0081 дополнительно выявил обход BeforeUnInit в UContainer | исправлено process-local lifecycle observations и live graph membership; 34 native cases, четыре full CTest suites и восемь legacy A/B на каждом сервере, M40 ASan 51+4. Evidence в s07-native-executor-elder1/m40. Прямые Init/UnInit сохраняют штатный обход hooks. Дефект нового адаптера, не ошибочность Reset модели; NativeExecution.ru.md |
| TL-022 | peak labels, whole-burst assignment and physical ownership | WindowOnly принимает задержанную раннюю волну под ID следующего стимула; native ISI=1 мс сливает два стимула в один максимум; одной подписи недостаточно также для physical channel/Branch selector | schema 3 и физические guards проверены: root 2b97f4fbb74776a8f44f254a5910fe59ba1e51f4, 46 адресных checks и 4 full CTest suites на обоих серверах, M40 ASan 48. После переноса model API root 4bd02ff03a6169a92a579b0fa27b40d05aaf0354: 61 addressed cases, 60 pass + helper skip. Git-пакеты s07-burst-final/combined-elder1/m40. Broad physics applicability и configured dispatch ещё открыты; BurstAssignment.ru.md. Исторические criteria не переписываются |

TL-023: в native Branch совпадающие точки подключения являются одним физическим
банком. В readback root 067a4dba91b0e1a2bca83d8c73850baa9c0aa9b7 на обоих серверах
N0 requested Ns=[1,2] реализован как общий Ns=2, N1 requested Rs=[86e6,43e6]
не реализуется как два независимых сопротивления. Поэтому новый controller
принимает эффективные значения банка и запрещает несовместимую локальную
поправку, скрыто меняющую другой вход или anchor. При разрешённом росте позиции
могут разделиться; при фиксированных позициях остаётся честный unresolved.
Legacy поведение не переписано. Один тест A3 предполагал последний writer до
Reset, но реальный Reset/mute выбирает другую запись: исходный failure сохранён,
fixture A4 проверяет сам shared bank и фактические значения. Это не опровержение
исторических результатов. Пакеты s07-bounded-elder1/m40, 27 targeted M40 ASan
checks с detect_leaks=0 и документ BoundedTraining.ru.md.

TL-024: новый NativeModelEditor первоначально проверял только property reverse
cache при удалении сегмента. Root 409ad59c0c727553b8c4e2d58cda4cf93e1cbb13
на обоих серверах прошёл 34/35 cases: shrink удалял источник external observer,
подключённого UItem.Connect. Исправление PulseLib
15deaed88148bf0325a5638b288d622861007630 проверяет
также native connectors и реальные inbound GetDataSources owner tree. Root
b0cd47e4acc335416bff8c3a516d446cfafbed83 прошёл 35/35 с native Connect и прямым
SetPointer. Root bbc81c3d857ceedc188275087354a31f74c71bdb прошёл 36/36 на обоих
серверах и M40 ASan 36/36, detect_leaks=0. Это ошибка нового адаптера, не дефект
Rdk или опровержение исторических результатов. NativeModelEdits.ru.md.

TL-025: исходный bounded kernel предлагал только одну новую позицию Branch.
При cold N>2 и всех L=1 reverse-order рост активного входа блокировался ещё
не посещёнными предшествующими точками. PulseLib
24006f7892aa3fc909ebd2f68ad3b50222a41606 предлагает явный coupled candidate,
сохраняя anchor, последующие входы, bounds и физическую совместимость банков.
Root bbc81c3d857ceedc188275087354a31f74c71bdb проверяет controlled four-input
search; root 4a27a579b5fff61e025ed200f627aa0482f06e1a дополнительно проверяет
native [1,1,1,1] → [2,2,2,1] и свежую пробу на обоих серверах. Полный native cold
Train и scientific matrix ещё не проверены. BoundedTraining.ru.md.

TL-026: native InputParameters представляет одно Rs на банк, но исходный readback
читал только ExcSynapse1. Неоднородный банк нельзя представлять этим значением.
Дополнительно Transform применял learned Rs только первому синапсу: новые члены
N0 банка могли сохранять сопротивление storage вместо объявленного Rs входа.
Это code findings нового edit API, а не runtime-объяснение старых экспериментов.
PulseLib 8f8620836ae0453dfc6140f1a6e7e1369f107f51 запрещает lossy readback;
a87fdd56f677b421d498dbe4cffcb257c19a0159 применяет Rs ко всему owned-банку
и проверяет complete readback preview. Root
1044112a3f26c9cc37fb36ce0e0af402ebb627de: 41 addressed pass на каждом сервере,
2 M40 ASan. Root 1e980f9103920c6012afe810d1e4be23929c80dc: 43 addressed pass
на каждом сервере, 4 M40 ASan (detect_leaks=0). Проверены сохранность rejected
heterogeneous bank и declared bank Rs после growth/shrink при 2000/20000.
Исходный runtime failure именно этого Rs-дефекта не воспроизводился отдельным
старым бинарником; evidence подтверждает исправленный путь и отрицательный guard.
NativeModelEdits.ru.md и Git-пакеты s07-native-edits-elder1/m40.

Эти findings являются результатом проверки кода. Runtime-causality и исправление
не считаются доказанными до соответствующих серверных тестов.
