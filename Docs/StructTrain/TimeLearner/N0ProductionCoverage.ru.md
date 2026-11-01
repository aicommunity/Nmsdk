# Производственный контроль N0

Статус: подготовка, runtime-приёмка ещё не выполнена. Это продолжение
[адресного исправления поиска](N0CandidateOrdering.ru.md), а не закрытие этапа7.

## Условия и ограничения

`tests/live_pipeline_corpus.py` сохраняет прежний N1-запуск без дополнительных
аргументов. Для N0 явно задаются `normalization="N0"`,
`n0_maximum_synapses=4`, `n0_candidate_repeats=1` либо `2`.
Это два отдельных корпуса, каждый из14 операций: Classic/Branch ×
fixed/grid Train и frozen same-matrix evaluation, а также budget/stopped/
legacy-budget controls. CalculateMode0/1 проверяются в исходном порядке.

Число4 — объявленная граница этого инженерного контроля, не новая граница
алгоритма и не оценка физической достижимости. Сохраняются исходные длительность,
частота2000Hz, CapturedPerInput, допуски и бюджеты. Индивидуальное сопротивление
каждого входа фиксируется на его исходном значении. Опорный последний вход
сохраняет исходные границы числа синапсов и длины. Неопорным входам разрешены
числа синапсов до объявленной границы. Физические storage-образы используются
из fixture без переименования или изменения prototype; N1 в историческом имени
образа не является действующим параметром нормализации.

Повторы2 используют configuration schema2, повторы1 — schema1; версия
training job2 означает live finalization и не смешивается с версией configuration.
Legacy-budget обозначает job1 без live finalization, а не ControllerVersion1.
Допускается только явно объявленное identity conversion. Исходные fixtures
дают профиль и проект обучения; сохранённый обученный граф не импортируется
в cold Train. Незавершённое обучение не получает шаблонный Test.

## Проверки

`test_live_pipeline_n0_worker.N0LivePipelineWorkerTest` наследует четыре
проверки полного корпуса: реальные completed/partial оси, переподписанные
повреждения, preflight persisted plan и closure всех14 запусков. Ещё две
проверки подтверждают N0/schema/repeat/domain в фактических Train packages
и summaries, frozen recognition handoff и отклонение ошибочных факторов.
Положительный контроль требует реально измеренного кандидата с Ns>1;
проверяются фиксированные индивидуальные Rs, неизменность опорного входа
во всех кандидатах и отсутствие N1 resistance-domain действий.
Корпус задаётся `TIMELEARNER_N0_LIVE_PIPELINE_CORPUS`; оба протокола проверяются
отдельно. Production audit каждого запуска независимо проверяет реальные
наблюдения, сертификаты, графы и повторные измерения.

Перед численным запуском необходим новый Console из согласованного source
closure в отдельном runtime. Ранее проверенный Test executable не доказывает
пересборку Console. Build log, compiler/cache flags, исходные SHA, executable
hash и runtime manifest сохраняются вместе с результатом. Сборки выполняются
на указанных серверах; исходники и результаты передаются через Git.

После выполнения нужны первичные архивы, reader results, временные графики
всех сом/паттернов с реальными входными импульсами без downsampling и выбранные
проверенные изображения. Полный производный cache хранится на M40 Data.
SearchUnresolved и NonSeparable допустимы как измеренные отрицательные исходы;
наличие recognition-модели не означает успешной классификации. Этот контроль
не заменяет августовский replay, независимый Test или всю physical matrix.

## Серверная подготовка 01.11.2026

Console собран на M40 из root021692a3fa0de4577e0770fd0af867a582a0ef03 /
PulseLib38edfcad7983478a7e2ca736c32ae2703861c1fd. Configure, target build и
runtime snapshot завершились успешно за36.65s. Новый runtime расположен в
`/media/user/Data/TimeLearnerRefactor/runtime-s07-n0-production-asan-a1`.
Executable SHA256: `be915df13bdf13884beb5ec5eac82d8e41901a2571b32f8e84997b8136833e3e`.
Компактный [build proof](../../../Reports/StructTrain/TimeLearner/s07-n0-production-build-asan-a1/README.md)
содержит девять файлов, включая cache/flags, logs, manifest и20 job preflight
checks; архив18508B. Это отдельное доказательство сборки, не результат обучения.

Запущен supervisor228908/start_ticks257797838 с последовательным выполнением
двух корпусов на неизменяемом runtime. При первой проверке фактически работал
Console228928 в Classic-fixed первого корпуса. Итоговая приёмка ещё открыта;
проверки первичных данных, temporal reports и сервер normal предстоят.
На Elder при ресурсной проверке осталось72MiB, поэтому новую сборку там
пока не запускали и дополнительные исторические данные не удаляли.
