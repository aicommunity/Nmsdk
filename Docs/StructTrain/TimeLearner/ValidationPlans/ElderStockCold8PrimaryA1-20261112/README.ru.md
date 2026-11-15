# Независимое восстановление полного N4 cold8 primary — Elder, 12.11.2026

Четыре файла корпуса StockCold8N4StoppedPrimary-20261112 доставлены с точной версией Git. Сначала production portable_primary проверяет SHA/размер и каждый member архива; единственный разрешённый compatibility adapter удаляет только доказанные дубли glog из новой производной копии. Проверяются обе исходные Classic/Branch модели: native preflight graph, неизменность stock physics, полные исходные full/omission данные и recovery ledger, исход invalid_observation/отсутствие certificate. Изменение реального извлечённого primary обязано отвергаться. Архив и исходные результаты не изменяются.

Это DATA-проверка на втором сервере, без нового расчёта модели, восстановления execution authority или научного verdict. CPU test использует production readers/resolver; ожидается один integration test с обоими случаями. Исходный Train engineering2/2 не становится успешным обучением.

Лимиты:1GiB RAM/tasks32/1800s wall,512MiB output и минимум2GiB свободного места. До запуска подтверждено3019632640 bytes free; архив расширяется примерно до473MB и временное восстановление удаляется после теста штатным TemporaryDirectory. Результат до проверки terminal/closure/lease/source fingerprints не принят.
