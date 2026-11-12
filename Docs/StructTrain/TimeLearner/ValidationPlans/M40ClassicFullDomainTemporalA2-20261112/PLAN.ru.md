# Временной разбор завершённого Classic full-domain

Анализируется прежний закрытый s07-observation-domain-train-m40-a1, а не работающий budget16. Production renderer composite_training_temporal.render повторно проверяет полный package/summary и primary CSV, строит full/omission группы12,14,42 со всеми каналами сомы и реальными входами. Выбранные PNG для чтения — soma0 overview этих трёх групп; остальные представления остаются кэшем M40. Downsampling выключен.

Source7bd3684732e1d3f7a0aa038d659fd52bc95892bf. Render A1 остановился до создания фигур: системный Python не содержит matplotlib. A2 использует уже принятый plot-python-owned-copy-a1/bin/python; ни код, ни исходные численные данные не менялись. Анализ ограничен1800s/4GiB/64tasks и выполняется через production contained runner.

[Таблица пяти отклонённых групп](assignment-table.json) и [14 валидных измеренных кандидатов](candidate-table.json) извлечены из исходных package/summary; SHA исходников сохранены. Это производные данные для чтения и не новые измерения.
