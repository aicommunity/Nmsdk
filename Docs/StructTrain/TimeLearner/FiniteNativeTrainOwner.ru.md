# Длительный Train с полным учётом native-памяти

Schema3 существующего `native_data_checks` добавляет конечный набор production
Train jobs. Схемы1 (GTest DATA) и2 (recorded diagnostic matrix) сохраняют свою
семантику. Новый режим не меняет контроллер обучения, физику и native scheduler.
Он вызывает тот же `native_pipeline_worker.run_job('train', ...)`, что и
остальные production-запуски.

У request обязательны `operation: train` и от1 до8 cases вида
`{name, job_name}`. Все `job_name` однозначно соответствуют объявленным inputs;
каждый input — подписанный training job с точными bytes/SHA. Весь job проходит
штатный `validate_job('train')` **до** создания controller/output и повторно
после staging. Шаблон, ошибочный фактор и другой тип операции не допускаются.
Произвольные shell-команды, Python-модули и env не добавляются.

Общий host registry резервирует `reservation_memory_bytes`, причём
`reservation_memory_bytes ≥ memory_bytes + leaf_memory_bytes`.
Параллельно с Python owner работает максимум один объявленный native leaf;
следующий case начинается после штатного закрытия предыдущего. Physical
MemAvailable проверяется по общей сумме до запуска. Эта сумма не меняет
собственные kernel caps: они задаются отдельно для owner и native.
Integer overflow и bool вместо лимита запрещены до дорогого выполнения.

Конечные пути `case/process/contained` известны внешнему владельцу заранее.
Существующий `_run_owned` записывает intents/bindings, наблюдает kernel units,
закрывает только принадлежащие попытке процессы и удерживает host lease до
закрытия owner и всех объявленных children. При потере SSH нужно проверять
тот же controller через `native_data_checks status`; повторный запуск с новым
ID не является восстановлением. Recovery использует исходные request,
supervisor identity и конечный граф. Активные sources/runtime не обновляются.

Успешная обработка валидного остановленного Train **не означает сходимость**.
Исходный run-manifest сохраняет execution, training_outcome, certificate и
наличие действительной модели. Structured budget stop может быть валидным
наблюдением. Timeout/OOM, отсутствующая модель и непроверенное выполнение не
превращаются в valid. Из одного `operation_passed` нельзя выводить Exact, PASS
классификации либо разрешение выдавать шаблонный Test за результат обучения.

Приёмка этой схемы требует реальных native Train и закрытых host/kernel
leases, помимо проверок деклараций. Не объявлять прежний759-probe OOM
исправленным на основании малых resource controls. Внешний archive остаётся
единственным местом primary; в Git — код, условия и компактные квитанции.

Этот путь закрывает конкретный разрыв суммирования памяти owner+sibling.
Полный общий scheduler, host task accounting, конкуренция разных клиентов,
отказоустойчивость всех режимов и полная матрица этапа10 остаются отдельными
требованиями исходного плана; одна конечная серия их не доказывает.
