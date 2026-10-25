# Ход реализации

**План целиком не выполнен.** Проверка по полному принятому плану:
[PlanCompletionAudit-2026-10-25](PlanCompletionAudit-2026-10-25.ru.md).
Формулировки «принято в develop» ниже означают принятие конкретных изменений,
а не автоматическое выполнение всех требований исходного этапа.

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
Применение registry к production profiles, росту и versioned export ещё впереди.

Согласованные develop merge: Rdk c80200bf1cd2bc8beec35546d3022da86afd35c9,
PulseLib 735fea58af4b1815dc332c7d38af5bf4f68d0855,
Bin 7136679740c5aa97def6fd3700b7b781d97af8f2. Корень содержит эти gitlinks.
Все изменения вводятся merge commits; tested SHA сохранены в manifests.

## Серверы

После уточнения адреса и аутентификации доступ к обоим серверам через jump host
проверен. При начале реализации на .11/.17 работали старые NSR/NSC jobs. Их
исходные деревья и runtime не обновлялись, процессы не останавливались. Новые
сборки выполнялись в отдельных checkout и deploy roots.

## Остальные этапы

Этап 1 требует завершения semantic/evidence review; этап 4 требует оставшихся
lifecycle/graph проверок; этапы 5–12 ещё не завершены. Pending не обозначается PASS,
version 2 не объявляется production-ready до серверной проверки.
