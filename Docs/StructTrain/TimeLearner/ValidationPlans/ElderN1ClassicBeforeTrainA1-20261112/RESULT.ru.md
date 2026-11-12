# Исходный Train: timeout при финализации, learning outcome неизвестен

Native process исчерпал общий2100s deadline:1800s поиска и300s финализации. Full model package и summary не получены; technical result `timeout/unverified_execution`, package/physical audit=null. Outer wall2125.737s, единственный CLI test завершился FAIL; skips/errors0. Это не runtime-проверенный результат сходимости или физической недостижимости.

К завершению поиска сохранено613 `train_stopped_trial_*.json` с соответствующими первичными трассами. Число файлов не превращается в число поисковых probes, которые без summary независимо не подтверждены. Финализация занимала CPU, RSS достигал примерно3.2GB; по наблюдениям новые пробы уже не добавлялись, но итоговый export ещё строился. Таймаут не переименовывается в `budget_exhausted`: typed learning outcome не получен.

Исходные terminal/log/limits/native process result/closure/runtime и source/fixture before/after сохранены в `failed-timeout`. Outer и native whole groups закрыты, lease released, operational diagnostics clear, source/fixtures неизменны. Лог `stock_cold7_condition_changed` относится к заранее объявленному отрицательному контролю condition, а не к причине фактического Train-отказа.

Повтор исходного обучения автоматически не запущен. Подготовленная after половина остаётся полезной для анализа решений, но без полного before package нельзя заявлять завершённое сравнение результатов обучения. Проблема производительности экспорта старого SDK уже устранялась в более новых subjects; перенос этой общей правки на обе половины будущей изолированной пары нужно обосновать отдельно, сохранив единственный алгоритмический фактор.

[Все исходные данные неудачной попытки сохранены компактно](../../N1BeforeTimeoutPrimaryPublication-20261112.ru.md):1341 members,13.6MB XZ. Архив не содержит отсутствовавшего итогового model export и не меняет outcome неизвестного обучения. Исходные CSV остаются доступны для анализа записанных реакций.

Для допуска after освобождён только объектный кэш завершённых before/after SDK builds:1012 `.o`,292795440 bytes. [Receipt](object-cache-cleanup/cleanup.json) содержит пути/размеры/SHA, проверку отсутствия работающих сборок и неизменности обоих executable/CMakeCache. Исходники, статические библиотеки и научные данные не удалялись.
