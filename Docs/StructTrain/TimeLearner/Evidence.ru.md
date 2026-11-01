# История и уровень доказательности

## Август

Визуально подтверждённые 4/8, 5/8 и 6/8 сохраняются как валидные наблюдения
исходного протокола. Saved-state replay, cold retrain и перенос на другой порядок
или ITI проверяются раздельно. Новый strict gate не отменяет старую точность.

| Контроль | Root commit с согласованными gitlinks | Источник |
|---|---|---|
| Phase A 4/8–6/8 | de02a3809395dd0bbd11e2ba792bfc04a51c89f3 | Bin/Configs/SpikeSamples/StructTrain/SelectivityPhaseA/REPORT.md |
| PSI k-sweep | bf2a68955c83b2540e1bc68d00aaa63eefa6541b | Bin/Configs/SpikeSamples/StructTrain/SelectivityPresynapticInhib |
| Branch amp-eq/NextSeg | 50b0cac1ade4f468be82a3d35e4ac6f5514ceb56 | flat Train/Test models + CSV; report added in root d8a1e711fc6edb0432ac09ad579860172e516db9, before later /Train layout |

Уточнённые [Git-источники шести августовских условий](HistoricalEvidenceAnchors.ru.md)
разделяют snapshot данных и commit отчёта. Проверены 65 адресованных файлов;
это metadata review, не новый runtime replay. В частности, Branch report ещё
не существовал в root 50b0cac1, а EXP02 Test_avg1 доступен в августовской истории,
несмотря на отсутствие текущего каталога.

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
| TL-003 | Branch PostTune rebuild | parent C/fallback 1e-9, потеря child physics и N0 bank consistency | runtime baseline по 8 failures; native reconstruction d862127: по 10 C++ / 7 Python на workers, ASan M40; PostTuneNativeRebuild.ru.md; full candidate transaction ещё открыта |
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

TL-027: native executor ранее проверял численное соответствие Dataset заявленному
expectedInputIsi, но не соответствие patternHash фактической матрице. Новая
проверка вычисляет canonical hash самой Dataset. В root
75e7fedb6c9ae6f040143393683f4bb4c8dee13b поддельный hash уже блокировался, однако
отказ ошибочно назывался native_base_revision_changed: до подготовки revision
не был доступен. Это runtime-подтверждённый дефект диагностики нового контура,
не свидетельство фактического изменения модели. Root
2fd45d4424360d7834ba094f875ddeda678c1625 сохраняет исходную причину первой и
различает unavailable/changed. На каждом сервере прошли 65 addressed cases;
M40 ASan 8/8, detect_leaks=0. В A1 был 41 pass + один failure, он сохранён.
Root 90d11d1990221753e6b494dbf40d83964b7d0fa3 (state diagnostics) прошёл 39/39
на каждом сервере. Root auditor 99cacf35326548a9f2d4f3ed2cad143497dc7a2b:
12/12, 56 реальных CSV/observations и четыре отрицательных сертификата на каждом
сервере. Code finding об исходном отсутствии hash gate и воспроизведённый
diagnostic failure не смешиваются. См. NativeTrainingService.ru.md и пакеты
s06-native-service-elder1/m40. Полный V2 и научная матрица остаются открытыми.

TL-028: auditor v1 проверял global assignment и совпадение записанного пика с
CSV, но не требовал isolated-window maximum rule C++ recorder. Подмена узкого
окна широким с двумя реальными максимумами ошибочно оставалась valid в Python.
Root 036b3a072023801f0562ba306dfc8743776991f1 воспроизводит expected failure
на каждом сервере. Root 7c65d7c6ffa3991c2fa77e775a5fe9aec07dedd1, auditor v2,
проверяет локальный maximum/plateau, clipping и число кандидатов в самом окне:
13/13 tests на каждом сервере. Ранее сохранённые 56 narrow-window traces и
четыре отрицательных сертификата на каждом сервере согласованны также с v2.
Это дефект нового Python-аудитора, не native C++ measurement и не опровержение
исторических результатов. Расширенный assigned-wave policy должен иметь явную
новую версию; пока он не реализован. Пакеты s06-native-service-elder1/m40.

TL-029: shared PulseLib test harness разрешал executable/ini относительно CWD
и предполагал QCoreApplication. S05 A4/A5 сохраняют fresh-process failures;
root a222ac7c4b386451137ef17e4a5a0af6996c8d9b разрешает actual executable и
соседний runtime ini; 7186788be098a58091a14025d664647e5d9eb2cd инициализирует
корневой NModel нового helper штатно. A6/A7 проходят адресные переносы на обоих
серверах. Прежние ad-hoc numerical controls не отменены, но утверждение об их
соответствии заявленному ini ограничено. Позднейшие full maintained groups пройдены на обоих workers;
PooledFullAcceptance.ru.md и FullClockAcceptance.ru.md. NativeLearnedState.ru.md.

TL-033: sampling-gap comparison терял absolute timestamp scale при вычитании.
Full root 157a5301 / PulseLib e875ca5 дал на каждом worker по 22 failures из
430 PulseLib cases; три Rdk groups pass. Начало поздних probes >128 s делает
roundoff delta больше прежнего допуска. Baseline f712e865 на двух workers,
M40 ASan: девять ожидаемых failures из десяти; восемь реальных Classic/Branch
probes при 131/1000000 s и 2000/20000 Hz, dropped-frame control pass.
Рабочая PulseLib d4c0cf0 использует absolute endpoints в sampling/coverage и
resolution guard; 52-case seeded regression и corrected data audit пройдены.
Full native aeff4a9d: четыре maintained groups pass на обоих workers, PulseLib
442 cases, 432 pass / 10 helper skips, 58 independent Python tests. Принято
в develop root b6212753 / PulseLib 32cb44bb; FullClockAcceptance.ru.md.
Причинная связь с августом не установлена.
См. AbsoluteClockSampling.ru.md; все failure bundles опубликованы через Git.

TL-032: explicit Default обоих learner сохранял EnableTrainingAudit=true.
M40 ASan baseline root bde7032a2af0fe2c670453809f0baa50d25f7cd6 воспроизводит
два failure, только на direct Default; ordinary Build/Reset и stock Return/Take
assertions проходят. PulseLib 4919bac2bd359118b13310862e54bcd24492967d явно
задаёт false в ADefault. Root 7fb92a4a57b9773ff56996cf2c7b8c75b2746cd8:
8/8 lifecycle и 18/18 UContainer passed на обоих workers, также ASan M40,
detect_leaks=0. Git packages s04-audit-default-elder1/m40 опубликованы.
Full A2 shell preparation failure сохранён; Full A3 завершён на обоих workers:
четыре maintained suites pass, PulseLib 387 pass / 10 skip. Принято в develop,
см. PooledFullAcceptance.ru.md. Физика,
tolerances и общий lifecycle Rdk не изменялись. См. AuditFlagDefault.ru.md.

TL-031: full maintained CTest Elder-1 A9 и M40 A15 воспроизводят по 15
learned-state export/import failures среди 395 PulseLib tests. Native reproducer
подтверждает старые direct property sources при Return/Take и replacement Copy.
Rdk 1223bcc18cf1ba106e8f8a17f20cce8c000c104d очищает внешние источники на этих
границах, сохраняя internal wiring и обычные Build/Reset/Default. На Elder-1
18/18 unit, 30/30 последовательных builder/learned-state integration, 9/9 Python;
на M40 18/18 unit под ASan, detect_leaks=0. Два исправления matrix-accessor fixture
сохранены отдельно от production defect. В failed full runs независимо проверены
по 16 source trainings и 208 trial CSV/JSON; успешный Train не отменяет failed
transport. Git evidence packages s04-property-bindings-elder1/m40 опубликованы.
Post-fix full CTest A3 завершён на обоих workers: четыре maintained suites pass,
PulseLib 387 pass / 10 skip, 16 packages / 208 primary trials на каждом.
Rdk develop merge 1812624ff75c60f03ad57c10b379d3e3848590bc принят, его tree
совпадает с tested 1223bcc; root develop 2ad95250fb91c32826399702081c636852a0d56a.
См. PooledFullAcceptance.ru.md. Эти проверки не включают более поздние
stopped-state и dynamic-domain extensions.
См. PooledPropertyBindings.ru.md. Исторические научные результаты этим не опровергаются.

TL-030: штатное перемещение компонента вперёд в конец читало за границей
вектора; вычисление int destination могло переполняться. Native test-only Rdk
e2bcd8da5bab016bd3fd703c42e519e56b633081 воспроизводит failing order check и
ASan heap-buffer-overflow на M40. Исправление Rdk
2cfda44d738f6291914217dba9cd223acae35bfd проходит 13/13 native tests под ASan,
detect_leaks=0, и 13/13 в обычной сборке Elder-1. A14 дополнительно проверяет
native import/rollback/frozen response на обоих серверах; Git-пакеты доступны.
Rdk develop merge ef4f033704d54f11d06e4da2b3518c313f3a9992 опубликован,
его tree совпадает с tested feature tree. Позднейший полный контроль
пройден: PooledFullAcceptance.ru.md и FullClockAcceptance.ru.md.
См. ComponentOrderBounds.ru.md. Причинная связь с историческими
экспериментами не установлена; их результаты этим finding не отменяются.

Эти findings являются результатом проверки кода. Runtime-causality и исправление
не считаются доказанными до соответствующих серверных тестов.

TL-034: оба legacy PushPostTunePattern подменяли InputPattern временным stimulus.
Correct pre-fix f9a30cb7 / PulseLib 6e28d203: 4/4 expected failures normal на
обоих workers. Fixed a5ada26f / PulseLib 0e1b01ae: 4/4 native; independent bb4a3511
8/8 Python, Elder normal / M40 ASan; 8 complete presentations, 19368 samples.
8 общих waveform projections byte-exact. Полный поиск/retarget/calibration этим
не подтверждены. См. PostTuneTransientStimulus.ru.md; ранняя неправильная фаза
Classic является fixture error, не доказательством lifecycle defect.

TL-035: native USerStorageXML::Load не принимал UTF-8 BOM вместе с declaration.
Baseline root7db4d9737 / Rdk1812624f: три real patched Project.ini читаются,
synthetic BOM+declaration отклонён; удаление любого элемента устраняет отказ
на том же binary. Rdk8ebf64dd нормализует только начальный BOM: M40 ASan
четыре Rdk CTest groups и native readback 4 файлов / 11 values успешны.
Python lossless adapter: по 7 tests на workers, 1599 tracked StructTrain Project.ini
byte-exact. Evidence 6210f023 / 13c43281, hashes сверены. A2 launcher syntax и
A3 disk exhaustion сохранены отдельно; native Elder/wide и production preflight
не заявлены. См. ConfigDocument.ru.md. Историческая научная причинность не установлена.

TL-036: native construction/import/editor принимали изменение physical graph,
когда связанные owner поля не могли принять required mirror values. Это не
перезапись SetPointer sources: Rdk оставлял их значения неизменными.
Construction/import cbbf56ce: M40 ASan 16 controls pass, evidence 1c55f903;
Elder normal повторил 16 controls в editor-baseline A1. Editor A2 root03fd6e47
на обоих workers: 6 conflict failures / 6 matching passes, actual Applied
при несовпадающей metadata. Первый A1 пропускал consumed probe boundary —
fixture error, не algorithm evidence. Editor fix 0ca75b3 прошёл на обоих workers 46/46 native,
по 2/2 independent Python tests, 12 boundary probes / 4332 samples.
Fixed пакеты 073b2906 / 37e6326c: по 530 stored / 528 raw hashes проверены. См. NativeOwnerBindings.ru.md. Причинность для исторических кампаний
не установлена; полный lifecycle/control-flag audit этим не закрыт.

TL-037: новый legacy inference saved-matrix attempt переиспользовал публичный
Result и SampleMetricState предыдущей попытки при равной размерности.
Baseline root d8e2ad16 / PulseLib ded4b558: по шесть воспроизведённых failures
из восьми cases normal/ASan; две NaN controls прошли. Непосещённый foil давал
Success и mid=0.25. PulseLib 39810a7 сбрасывает attempt-scoped evidence/status;
runtime-приёмка исправления пока не завершена. См. LegacyPostTuneObservation.ru.md.
Историческая причинность для августа и остальных кампаний не установлена.
