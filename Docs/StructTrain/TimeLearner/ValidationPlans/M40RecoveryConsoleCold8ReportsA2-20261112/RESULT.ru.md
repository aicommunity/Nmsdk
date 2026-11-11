# Временные отчёты настоящего Console cold8 — M40 A2, 12.11.2026

Production renderer: **1/1 PASS**, без skips/errors/failures. Проверены четыре предъявления Classic и четыре Branch: **12 пар «предъявление × сома»** (Classic:две сомы, Branch:одна). Все native samples сохранены. Обзоры и увеличения:PNG1920×960, SVG и PDF. Увеличения дают не менее8pixels/native tick; используются общие Y и явно отмеченные local-detail Y. Фактические входные импульсы и LT events наложены на Soma.SumPotential. Порог LT не переносится на другую физическую величину сомы.

## Приёмка и воспроизводимость

Python source:45ebf7e5dc2a612a94139ccc0ba28f5834f1a321; package fingerprint75338b29bd779dba84185608777446c849d447b4255a8ce02c679e26d43da538. Проверенный plotting runtime:Python3.12.3/matplotlib3.9.4/Pillow13. Исходная попыткаA1 без matplotlib сохранена отдельно.

[Точный результат](completed/process/stdout.log), [closure](completed/closure-and-reservation.json), [controller result](completed/controller-result.json), [terminal](completed/worker/terminal.json). Процессы закрыты, lease released, diagnostics clear; heartbeat errors отсутствуют. Source/tool/fixtures до и после побайтно совпадают. Fixtures:628JSON исходного Console результата и одна декларация. Модель заново не рассчитывалась. [SHA256 readbacks](completed/readback-integrity.json).

Полный кэш:/media/user/Data/TimeLearnerRefactor/readbacks/s11-recovery-console-cold8-reports-m40-a2/worker/visual-reports. Он воспроизводится из [полного primary в Git](../M40RecoveryConsoleCold8ClosedCorpusA1-20261112/RESULT.ru.md). В корневой Git перенесены только24PNG, два figure manifest и selection.json. [Git transport](git-transport.json):standalone commit e86def6e85a27b965722ee965e84d7acd163f058, pack2885178bytes. Git objects проверены fsck; каждый извлечённый файл проверен по SHA256/размеру. Полный кэш в Git не добавлен.

## Визуальная проверка и ограничения

Просмотрены **10PNG**:обзоры обоих уникальных паттернов для всех трёх сом и local-detail Soma1 обеих моделей. [Точный список](visual-inspection.json). Все24 выбранных PNG и весь кэш вручную не проверены; manifests сохраняют visual_acceptance_complete=false.

На target видны actual LT event и сильная отрицательная фаза после него; на foil в обзоре LT event отсутствует. Общий Y сохраняет эту фазу, но сжимает малые положительные вершины, поэтому необходимы detail-графики. Zoom-002 показывает0.05–0.10s относительно onset; более поздний LT event и второй импульс foil требуют соседних увеличений полного кэша. Метрики по картинкам не пересчитываются. Единицы:model_units_SI_unverified; универсальная нулевая rest-state не предполагается.

Это инженерный **N2/N0/SyncTolerance0.2**, historical same-matrix:один target и один foil с последним ISI×1.5, каждый повторён дважды, reset-per-trial. Реальный Console ранее подтвердил TP2/FP0/FN0/TN2 каждой модели, frozen state и calibration candidate. Это не независимая N4/8pattern классификация, default SyncTolerance0.02 или реальный recovery intervention (delivery_count=0). Этапы1–12 общего плана остаются частичными.
