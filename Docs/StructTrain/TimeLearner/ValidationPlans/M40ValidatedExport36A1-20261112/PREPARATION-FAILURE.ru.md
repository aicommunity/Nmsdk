# Canonical A1 отказала до сборки

Source projection gate обнаружил восемь отсутствующих файлов с кириллическими именами в HardwareLib Catalog:physical4137, expected4145. Требование полноты не ослаблялось. Дочерняя диагностика:canonical_source_projection_changed. Весь owned job закрыт, lease released; C++ сборка/tests/models не запускались.

После закрытия A1 выполнено Git sparse-checkout set --no-cone --stdin с UTF-8 списком literal patterns, без изменения Git commits или code bytes. Все4145 файлов после восстановления проверены по размеру/SHA256. [Точный repair receipt](source-projection-repair.json). Ранее JSON-экранирование в диагностике было ошибочно прочитано как часть имени; фактические имена кириллические. Низкоуровневая причина первоначального аргументного пути доставки отдельно не доказана.

Следующая подготовка [A2](../M40ValidatedExport36A2-20261112/README.ru.md) использует то же проверенное дерево. Старые model sources/runtime не затрагиваются.
