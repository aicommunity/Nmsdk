# Ход реализации

**План целиком не выполнен.** Проверка по полному принятому плану:
[PlanCompletionAudit-2026-10-25](PlanCompletionAudit-2026-10-25.ru.md).
Последующее устранение TL-014 и его серверная проверка описаны в
[StorageCleanup](StorageCleanup.ru.md). Это не закрывает общую транзакцию импорта.
Формулировки «принято в develop» ниже означают принятие конкретных изменений,
а не автоматическое выполнение всех требований исходного этапа.

Последний проверенный подэтап: внутренний native executor подключён к обоим
learner через штатный scheduler, включая transient Branch solo routing,
контроль lifecycle, schema 2 typed source profile и native FinalVerification.
На обоих серверах прошли четыре maintained CTest suites (PulseLib 247: 238 pass,
9 skip), 34 native execution controls и восемь отдельных строгих legacy A/B.
M40 ASan: 51 адресный тест и 4 lifecycle checks, detect_leaks=0. Primary data,
negative baselines и runtime manifests опубликованы через Git в
s07-native-executor-elder1/m40; проверены 867 artifact hashes.
См. [NativeExecution](NativeExecution.ru.md). Основной bounded search, глобальное
burst-wave assignment Classic и production ControllerVersion=2 остаются
открытыми; этот подэтап не завершает исходные этапы 6/7.

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
