# Этап 2: проверка runtime

Изолированные сборки выполнены через jump host на Elder-1 (.11, Qt5) и M40
(.17, Qt6). Старые NSR/NSC деревья и binaries не обновлялись, процессы не
останавливались. Новые исходники находятся в /home/user/timelearner-refactor/source.

Console и Test_PulseLib_StorageComponents собираются в выбранный deploy root,
отдельно от source Bin. CTest проходит на обоих серверах. Проверены --help и
отказ при явно несуществующем --app-ini. Qt6 configure потребовал убрать
принудительную зависимость LLM tests от Qt5; используется общий Qt alias проекта.

Elder-1 evidence: Reports/StructTrain/TimeLearner/s02-elder1, commit
8b54226 (полный SHA хранится в Git). M40 evidence: branch
evidence/timelearner-s02-m40, commit 800fb96. Последний пакет также содержит
проверки следующего этапа наблюдений и войдёт с соответствующим merge.

M40 manifest фиксирует 28 фактически отображённых executable files процесса
после инициализации без Calculate. Процесс был создан только для диагностики
runtime и завершён владельцем после capture. Manifest без --pid содержит
resolved ldd dependencies и не объявляет их полным набором будущих plugins.

Результаты относятся к реализации и сборке. Они не являются повторным обучением,
не сертифицируют научный PASS и не отменяют предыдущие исторические результаты.
Перед научным run нужен новый manifest его неизменяемого runtime; источники и
данные передаются через Git.
