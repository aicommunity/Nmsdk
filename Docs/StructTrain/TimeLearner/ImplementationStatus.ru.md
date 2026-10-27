# Ход реализации

**Актуальная систематизированная сводка всех этапов:**
[PlanCompletionAudit-2026-10-27](PlanCompletionAudit-2026-10-27.ru.md).
Полностью принят этап 0; этапы 1–7, 9, 10, 12 частичны; новые сквозные
контуры этапов 8 и 11 не выполнены. Ниже сохранён журнал конкретных подэтапов
и исторических snapshots; его ранние формулировки не заменяют новую сводку.

Подэтап `stage06/native-model-builder` добавляет cold construction,
read-only adoption и сохраняющий модель forced Build. На root `c1f90650`
на каждом сервере прошли 29/29 новых и 68/68 регрессионных проверок;
M40 ASan — 21/21, независимый Python-аудит — по 18/18 без skips.
Cold Ns/inhibition controls завершены; A1/A2/A3 primary artifacts сохранены в Git.
См. [NativeModelBuilder](NativeModelBuilder.ru.md). Configured V2 ещё отсутствует.

Проверка ревизии actual model ускорена через typed observer с полными boundary
captures: [ModelRevisionObserver](ModelRevisionObserver.ru.md). На каждом
сервере прошли 85/85 основных cases, 12/12 replacement/lifetime, 20/20 old
provider regressions и 18/18 Python. Это уменьшает overhead будущей матрицы,
не закрывая configured V2 или физические/научные требования исходного плана.

Последующее измерительное изменение:
[AssignedWaveSelection](AssignedWaveSelection.ru.md). Явный assigned выбор
поддерживает широкое окно при полной measured burst assignment; isolated
семантика сохранена. На .11/.17: 56/56 addressed C++ и 18/18 Python без skips.
Это уточняет прежний pending assigned-wave policy ниже: автоматическая
длительность окон, большие исторические длины и configured V2 ещё открыты.

**План целиком не выполнен.** Проверка по полному принятому плану:
[PlanCompletionAudit-2026-10-25](PlanCompletionAudit-2026-10-25.ru.md).
Последующее устранение TL-014 и его серверная проверка описаны в
[StorageCleanup](StorageCleanup.ru.md). Это не закрывает общую транзакцию импорта.
Формулировки «принято в develop» ниже означают принятие конкретных изменений,
а не автоматическое выполнение всех требований исходного этапа.

Проверенный измерительный подэтап: внутренний native executor подключён к обоим
learner через штатный scheduler, включая transient Branch solo routing,
контроль lifecycle, schema 2 typed source profile и native FinalVerification.
На обоих серверах прошли четыре maintained CTest suites (PulseLib 247: 238 pass,
9 skip), 34 native execution controls и восемь отдельных строгих legacy A/B.
M40 ASan: 51 адресный тест и 4 lifecycle checks, detect_leaks=0. Primary data,
negative baselines и runtime manifests опубликованы через Git в
s07-native-executor-elder1/m40; проверены 867 artifact hashes.
См. [NativeExecution](NativeExecution.ru.md). Основной bounded search и
production ControllerVersion=2 остаются
открытыми; этот подэтап не завершает исходные этапы 6/7.

Общие native graph API перенесены из Console в PulseLib.core. Console и tests
используют одну реализацию identity/readback/archive; тела семи файлов сохранены
после механической нормализации includes/export. На обоих серверах: 18 pass и
один helper skip, отдельно четыре fresh-process parent controls, шесть sole Core
symbols и два сравнения native waveform/identity. Пакеты опубликованы в Git.
См. [ModelGraphOwnership](ModelGraphOwnership.ru.md). Это подготовка producer
модели для контроллера, а не завершение обученного state export или main search.

Измерительная schema 3 добавляет whole-burst assignment и physical input
ownership. Полная приёмка отдельного снимка: 273 cases (264 pass, 9 skip) в
PulseLib и четыре maintained suites на каждом сервере; M40 ASan 48 checks.
После объединения с model API проверены ещё 61 addressed cases (60 pass, один
helper skip) и 16 совпадающих native waveform/identity/outcome pairs на каждом
сервере. См. [BurstAssignment](BurstAssignment.ru.md). Это внутренний API;
ControllerVersion=2, основной поиск, trained-state export и широкая physics/
inhibition applicability остаются обязательной незавершённой частью плана.

В ветке stage07/bounded-controller реализован общий BoundedTrainingSession:
целые L/Ns и ограниченная сетка Rs, индивидуальные bounds, свежая опорная проба
после каждого изменения, ranking измеренных остатков и независимый финальный
проход. Root 5f3737013ec3c18d3514f1d3292e1367181cb9e0 прошёл 29 адресных tests на
обоих серверах, включая настоящую коррекцию Rs Classic/Branch × 2000/20000 Гц.
Это проверка нормализации с фиксированными длинами и явным sync tolerance 0.2 с,
а не синхронизация при default 0.02 с. Root 067a4dba91b0e1a2bca83d8c73850baa9c0aa9b7
прошёл 27 адресных tests на обоих серверах после добавления deadline и защиты
общего Branch-банка; M40 ASan — ещё 27 cases, detect_leaks=0. Пакеты обоих
серверов опубликованы через Git, проверены 206 artifact hashes и gzip payloads.
Подключение ControllerVersion=2, структурные адаптеры и
полная алгоритмическая матрица всё ещё нужны. См. [BoundedTraining](BoundedTraining.ru.md).

## Исходная точка

До изменений root был 895dea071600eafe489c97dffc8147383587e51c, PulseLib checkout
652e0942f82029af388e432c004fc4a477387cb3, Bin checkout
78bcb00fe0ca1575ba3c9627b7c8c247d7c901de. Root-recorded PulseLib был
02cc0c749a979961586263ac305fbec4b9006c90. Локальных изменений файлов не было.
Исходный Rdk: b3b2472dc347899af266cd46e64bca2a6ea16fea.

## Этап 0 — выполнен

- PulseLib merge: 4feda750b674536fbd680cab416cd6f53930f947.
- Bin merge: 24df8c836e596472f96b3f01ab0397c97c37cd0d.
- Root merge: f92dee818e71d1b04cda4bcf2c572c11008cf180.
- Root coordinated gitlinks/hints: 2450e1a (полный SHA извлекается из Git).

Все три develop опубликованы, child pushes выполнены до root push. Merge имеют
два родителя; rebase/squash не применялись. Branch hints PulseLib/Bin — develop.

## Этап 1 — в работе

Зафиксированы контракты и исходный inventory; семантическая проверка всех
публичных параметров и полный evidence ledger ещё не завершены.

## Этапы 2 и 3 — проверенные компоненты приняты; полная приёмка открыта

Этап 2 проверен на Elder-1/Qt5 и M40/Qt6: отдельные runtime, explicit ini,
нативный CTest, dependency provenance и 28 executable mappings idle Console на
M40. Этап 3: 90 Python tests, пять C++ collector cases, реальный C++ CSV → Python
roundtrip и полный PulseLib CTest. Подробности: Stage02-Validation.ru.md и
Stage03-Validation.ru.md. Это не научные результаты обучения.
Автоматический runtime capture перед настоящим Train, полный published run bundle
и сквозной controller/runner контур ещё не реализованы. Проверка scorer/collector
не означает завершения всех аналитических путей и native trial boundary проверки.

Подэтап 4.1 принят: NPulseSynapse::AReset обновляет step coefficients после
изменения частоты. Сохранён failing baseline на активном/Init-компоненте и passing
regression; native hook order и storage-image reuse также проверены.
Этап 4 целиком не завершён: см. Stage04-Progress.ru.md.

Подэтап 4.2: native effective graph readback проверен на обоих серверах, включая
прямые связи свойств и внутренние ссылки нейрона. 4/4 targeted tests и полный
PulseLib CTest прошли; реальные Classic/Branch Test-проекты дали 499/364 bindings
без неразрешённых источников. Readback не выдаётся за model export/checkpoint.

Подэтап 4.3: исправлена перестановка Soma/LT в режиме явного графа нейрона 0.
На обоих серверах native Copy/XML/повторный Build: 3/3 и полный CTest; сохранены
400-точечные импульсные трассы каждой пары source/target.

Подэтап 4.4: исправлены rest outputs NConstGenerator и NPulseSynapseCommon до
первого Calculate. 9/9 lifecycle/roundtrip tests и полный CTest прошли на обоих
серверах; warm/fresh, Copy и XML traces совпадают. Сохранены failing baseline
с binary provenance и passing traces. Growth/default-profile и расширенная
fresh/reuse матрица остаются в работе; научное A/B не заменяется unit-тестами.

Подэтап 4.5: opt-in registry проверяет отдельную native копию образа, коллизии
имён и сохранность физики. Исправлен общий UContainer::Copy: инициализация
прежнего графа больше не сохраняется после замены детей. На обоих серверах
15 targeted cases и четыре maintained Rdk/PulseLib CTest suites прошли.
Полный versioned export и карта всех production-профилей ещё впереди.

Подэтап 4.6: реализованы явные физические storage-рецепты, отдельные Exc/Inh
образы синапсов и body/LT. Рост сохраняет learned Rs/C; устранены Ns wakeup toggles.
Native проверки выявили и закрыли три общих дефекта: XML setter order,
повторный Free при очистке storage и Environment use-after-free при shutdown.
На обоих серверах прошли 11 адресных проверок и четыре CTest suites, на M40 —
полный ASan run 122 cases через shutdown (leak detection выключен).
Артефакты: s04-profiles-elder1, s04-shutdown-elder1, s04-profiles-m40.
Это не полная миграция всех физических моделей или реализация ModelSpec.

Согласованные merge подэтапа 4.6: Rdk b15f4384c4516c865afc59a83b487acd477744d0,
PulseLib 77cc52d06852cef0ddcd256a528283dd90631f49,
Bin 83ab62fcb40f62affd83f66ae68fcd557de55d53. Подэтап 5.1 далее обновляет PulseLib.
Все изменения вводятся merge commits; tested SHA сохранены в manifests.

## Этап 5 — в работе; подэтап 5.1 принят

Добавлены semantic model identity и production verifier expected → actual
native graph. Исправлено различие membrane index после fresh Build и XML Load.
На обоих серверах прошли семь адресных cases, четыре maintained CTest suites и
реальные Classic/Branch CLI controls. Fingerprints совпали между Qt5/Qt6 для
всех шести сохранённых случаев. PulseLib merge:
4af8184275e182b943bb43df7447f8f7a065d73d.

Подэтап 5.2: native ModelArchive переносит замкнутую физическую модель и
definitions в свежий процесс. На обоих серверах прошли пять parent controls с
двумя child imports и четыре CTest suites. Реальный Git-перенос M40 → Elder-1
дал совпадение identity и 200/2000 waveform samples (max error=0).
Источник 41 узел, 34 class definitions; metadata model_spec/not_trained.

API boundary ports (5.3) проверен: native Connect/BreakLinks, независимый источник,
два сервера, 4/4 CTest suites и M40 ASan, реальный Git replay Elder-1 → M40.
Границы проверки и raw artifacts: [ModelBoundary](ModelBoundary.ru.md).
Подключение API к реальному learner, metadata/certificate adapters, безопасный
registration rollback, controller checkpoint и Train → frozen Test остаются открыты.
Подробности: [Stage05-Progress](Stage05-Progress.ru.md).

## Серверы

После уточнения адреса и аутентификации доступ к обоим серверам через jump host
проверен. При начале реализации на .11/.17 работали старые NSR/NSC jobs. Их
исходные деревья и runtime не обновлялись, процессы не останавливались. Новые
сборки выполнялись в отдельных checkout и deploy roots.

## Остальные этапы

При подготовке этапа 6 найден и исправлен TL-015: live Classic Build оставлял
новый Neuron неинициализированным. Native controls и raw graph/readbacks:
[LiveRebuildInit](LiveRebuildInit.ru.md). Обнаружен также TL-016: смешанные
эффективные частоты при legacy model clock=20000. Последующее исправление
общего режима Rdk и его ограниченная проверка описаны в
[FrequencyContract](FrequencyContract.ru.md); полная uniform-rate матрица ещё
не доказана. Общие legacy-политики подключены к обеим топологиям и проверены
строгим native A/B на обоих серверах. Перенос полного контроллера и исправление
алгоритмов не объявляются завершёнными: [Stage06-Progress](Stage06-Progress.ru.md).

Также введены ProbeSpec/Observation и bounded recorder с фактическими пиками,
неполнотой, revision mismatch и явными unknown значениями. Native frozen
characterization проверена в обоих learner при 2000/20000; общий controller
ещё не подключён. Полный CTest выявил и помог исправить TL-017/018 в Rdk
storage metadata/identity: [ProbeMeasurement](ProbeMeasurement.ru.md).

Вынесен stateful FinalVerificationSession и immutable references/certificate:
[FinalVerification](FinalVerification.ru.md). Он проверяет весь свежий sweep,
текущий anchor и исходные tolerances; session API ещё не подключён к train/search
циклу обоих learner. TL-001 в legacy и полная матрица остаются открытыми.

Этап 1 требует завершения semantic/evidence review; этап 4 требует оставшихся
lifecycle/graph проверок; этапы 5–12 ещё не завершены. Pending не обозначается PASS,
version 2 не объявляется production-ready до всей обязательной проверки.

Следующие принятые подэтапы описаны отдельно: общий model graph API перенесён
в PulseLib, schema 3 связывает всю пачку с реальными входами, bounded decision
kernel выполняет конечный поиск и независимый final gate. См.
[ModelGraphOwnership](ModelGraphOwnership.ru.md), [BurstAssignment](BurstAssignment.ru.md),
[BoundedTraining](BoundedTraining.ru.md). Это уточняет прежние строки о неподключённом
final gate: kernel уже использует его, но configured ControllerVersion=2 и
полный native structural Train ещё не реализованы.

В подэтапе stage07/native-structural-edits добавлен общий preview/apply
L/Ns/Rs на границе native-проб. Исправлены guard внешнего наблюдателя и
холодный Branch N>2 candidate. Root bbc81c3d857ceedc188275087354a31f74c71bdb:
36 адресных cases на каждом сервере и 36 M40 ASan, detect_leaks=0.
Root 4a27a579b5fff61e025ed200f627aa0482f06e1a: отдельный native four-input
coupled edit и четыре полных поддерживаемых CTest suites прошли на обоих серверах
(PulseLib 293 pass + 9 skip, Rdk 18 pass). Финальные native bank readback/Rs
правки root 1e980f9103920c6012afe810d1e4be23929c80dc прошли 43 addressed cases
на каждом сервере и 4 M40 ASan, detect_leaks=0. Подробности:
[NativeModelEdits](NativeModelEdits.ru.md). Полные этапы 6 и 7 остаются открытыми.

Explicit BeginNativeTraining соединяет capture/search/fresh final gate внутри
Before/After hooks обоих learner: [NativeTrainingService](NativeTrainingService.ru.md).
Root 2fd45d4424360d7834ba094f875ddeda678c1625: 65 addressed pass на каждом
сервере, 8 M40 ASan (detect_leaks=0). Retention A3: 31/31; state-summary A4:
39/39 на каждом сервере. Root analysis module: 12/12, 56 real CSV/observations
и четыре отрицательных сертификата на каждом сервере. Это actual structural
search API, а не только ручное выполнение действий тестом. Однако configured
ControllerVersion=2, новые builders, длинные окна/assigned-wave policy,
динамические Rs domains и полный Train→Test остаются открытыми. Поэтому прежняя
строка «полный native structural Train не реализован» не означает отсутствие
этого ограниченного рабочего API; весь этап и production-ready V2 ещё не приняты.
