# Ход реализации

## Исходная точка

До изменений root был 895dea071600eafe489c97dffc8147383587e51c, PulseLib checkout
652e0942f82029af388e432c004fc4a477387cb3, Bin checkout
78bcb00fe0ca1575ba3c9627b7c8c247d7c901de. Root-recorded PulseLib был
02cc0c749a979961586263ac305fbec4b9006c90. Локальных изменений файлов не было.
Rdk остаётся b3b2472dc347899af266cd46e64bca2a6ea16fea.

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

## Серверы

После уточнения адреса и аутентификации доступ к обоим серверам через jump host
проверен. На .11 и .17 продолжают работать старые NSR/NSC jobs. Их исходные деревья
и runtime нельзя обновлять. Новая сборка должна использовать отдельный checkout
и отдельный deploy root. Активные процессы не останавливались.

## Остальные этапы

Этапы 2–12 не считаются выполненными. Pending проверки не обозначаются PASS,
version 2 не объявляется production-ready до серверной проверки.
