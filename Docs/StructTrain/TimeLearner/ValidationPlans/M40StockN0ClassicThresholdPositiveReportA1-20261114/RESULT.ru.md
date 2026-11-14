# Positive-response Y detail A1: часть визуальной приёмки открыта

Production1/1 PASS, outer completed50.62922348501161с/whole group closed.40 каналов (8×4 сомы +8 LT) построены без нового model execution, изменения samples либо scorer. Сохраняется один общий положительный диапазон Y на каждый канал для всех паттернов; отрицательный reset ниже оси явно помечен как clipped. [Обязательный исходный full-range report](../M40StockN0ClassicThresholdReportA2-20261114/RESULT.ru.md) сохраняет полный отрицательный отклик и native time tiles.

19 original overview PNG сохранены, но при ручной проверке обнаружена ошибка подписи вертикальной оси LT: данные и заголовок относятся к LTZone.Potential, подпись оси осталась Soma SumPotential. Эти8 LT companion PNG **не приняты визуально** и не используются в основном научном отчёте.11 выбранных Soma PNG (все8 Soma1 и target Soma2–4) просмотрены, читаемы и имеют правильную подпись. Unit PASS не отменяет этого визуального отказа; исходные receipts/изображения сохранены.

Исправление только подписи оси зафиксировано в root6410bfb76cb6cf189c41863fc2511c125045b250. Передача новой source на M40 оборвалась; A2 job ещё не запущен. Потребуется повторный read-only rendering, не Train/Test. Научные TP/FP и underlying observations этим дефектом не затронуты.

[Manifest](completed/worker/tmp/fixed-threshold-positive-response-gallery/manifest.json), [unit](completed/worker/validation/result.json), [integrity](integrity.json). Producer9da6345d9905a5d0cb578400ee0c6dce1b452733, pack SHA256737e782e55f103edee74b5c6cbed40bd594d619aaefb04f5bc066e6d2ffefdf0. Нельзя считать всю gallery или весь новый plot interface принятой матрицей.

Уточнение после восстановления связи: [A2 фактически завершён и принят1/1](../M40StockN0ClassicThresholdPositiveReportA2-20261114/RESULT.ru.md),8 исправленных LT originals просмотрены.11 Soma PNG побайтно совпадают с принятой A1. Исторический отказ8 LT изображений A1 остаётся в силе для их неверной подписи.
