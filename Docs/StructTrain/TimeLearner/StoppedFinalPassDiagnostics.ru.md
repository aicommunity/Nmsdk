Принято06.11: четыре actual native случая на Elder прошли4/4, записаны32 полные JSON/CSV-пробы. Исправленный reader297bcbb прошёл13/13 и production CLI4 на каждом сервере; все четыре JSON-результата побайтно одинаковы, все116 первичных файлов повторно rehashed без изменений. C++/модели при исправлении reader не перезапускались. [Независимая сверка](StoppedFinalPassDiagnosticsVerification.json). Оригинальная попытка reader A1 с ошибкой чтения CLI envelope сохранена. Это адресная приёмка анализа; полные временные графики этого нового корпуса ещё не приняты, этапы1–12 остаются частичными.

# Диагностика полного отрицательного финального прохода

Принято: новый reader не меняет обучение,
математическую цель, физику, допуски или Rdk lifecycle.

Native service намеренно оставляет `certificate=null` у `BudgetExhausted`:
это диагностическое состояние, не завершённый Train. Внутренний bounded search
может иметь полный отрицательный финальный сертификат, а portable stopped package
сохраняет первичные `final_packets`, references, модель и причину остановки.
Отсутствие публичного сертификата — защитный контракт, не основание разрешать Test.

Команда `analyze INPUTS --format stopped-final-pass --output RESULT` вычисляет
остатки из исходных JSON/CSV, не создавая сертификата. INPUTS — JSON
`kind=timelearner_stopped_final_pass_inputs`, `schema_version=1`, относительные
`package`, `summary` и явный массив `trials` с `packet`/`trace`. Пути задаются
относительно INPUTS; выход за каталог, дубли и неизвестная схема запрещены.
Нет поиска первой строки, glob-эвристики или зависимости от текущего каталога.

Поддерживается только полная reference capture и `maximum_sweeps_exhausted`.
Сначала production stopped auditor проверяет все фактически сохранённые пробы,
численные CSV и fingerprint модели. Затем проверяются полное множество ID,
один финальный проход последнего объявленного sweep, свежие revision/epoch,
protocol/pattern/physical input, исходные tolerances и назначенные измеренные пики.
Измеренное время берётся относительно реального origin stimulus каждой пробы.
Опорный вход — последний физический вход, его временной остаток равен нулю;
амплитудная цель каждого входа — собственный захваченный raw potential.

Результат содержит все временные/амплитудные остатки и исходные ID. Он явно
оставляет `training_completed=false`, `certificate_present=false`,
`diagnostic_only=true`, `evaluation_verdict=null`. Перестановка final packets
не меняет остатки. Если при заявленном исчерпании sweeps все остатки внезапно
попали в допуск, reader отвергает противоречие вместо выдачи PASS.

Это адресная диагностика, не замена признанным отрицательным stock-пробам:
там причина `invalid_observation`, отсутствует полный валидный финальный проход.
Повторение того же невалидного кандидата при большем invalid budget не устраняет
детерминированное слияние волн. Автоматическое расширение SyncTolerance, замена
пачки одиночным импульсом и подтверждение отсутствующего пика прогнозом не вводятся.

Приёмка требует реальных Classic/Branch×N0/N1 native fixtures, production CLI и
негативных проверок на обоих серверах. Ни инженерный fixture с LTMembrane,
ни полный отрицательный проход не являются научной классификацией восьми паттернов.

Native declaration: `specs/native-stopped-final-pass-v1.json`. Оркестратор копирует
её вне исходников и явно привязывает source_root/runtime_manifest к проверяемой
неизменяемой SDK. Reader source и compiled native source фиксируются отдельно.
Первый адресный корпус — четыре двухвходовых случая без повторных финальных
проб: reader требует ровно одну записанную финальную пробу на вход и не выбирает
молча «последнюю подходящую» из retries. Расширение на retries, остальные размеры
и физические профили остаётся открытой частью матрицы; этот gate её не закрывает.

## Фактический корпус и измеренный отрицательный результат

Compiled native source2e0618110a9abb48b94f6edc6b63c51f829ec810/Pulse12d; analysis source297bcbb42105396d83c3eecf52ad98613afaef0f. Native4 выполнены только на Elder. На M40 выполнялся анализ сохранённых данных, не новое обучение. Два входа, fixed L/Ns/Rs, один sweep, SyncTolerance=0 — явный инженерный отрицательный контроль, не stock4-input/8-pattern и не научный default0.02. Fixture имеет LTMembrane; научная эквивалентность stock-профилю не заявляется.

Во всех четырёх Classic/Branch×N0/N1 случаях амплитудные остатки обоих входов равны0 при absolute tolerance1e-5/relative0. Временной остаток input0 около−0.0705s, опорного input1 —0. При объявленном sync0 это полный измеренный отрицательный проход. Причина остановки остаётся maximum_sweeps_exhausted; он не превращается в Exact, PhysicalInfeasible или успешное распознавание. Полные исходные doubles сохранены в diagnostics JSON, без округления для критерия.

Полные источники в Git:

- [Native4 и первоначальная ошибка reader](../../../Reports/StructTrain/TimeLearner/s07-stopped-final-native-elder-a1/bundle.json), data d080310f241c994bca1231cbb38a3cb290ca2f36:116 members/124656B xz. Девять checks readerA1 прошли, один CLI test получил KeyError: он прочитал поле вне штатного analysis envelope. Исправлен тест; первичные данные сохранены.
- [Elder reader13/CLI4](../../../Reports/StructTrain/TimeLearner/s07-stopped-final-reader-elder-a2/bundle.json), data5a1f158ca3628835fb444f10d02dc58ae8e1624d:15 members/19504B xz.
- [M40 reader13/CLI4](../../../Reports/StructTrain/TimeLearner/s07-stopped-final-reader-m40-a2/bundle.json), data3b157a6e67ef7f8a83fef06d0f9b22c7c06b1d2c:15 members/19516B xz.

Все281 Python source hashes каждого reader сверены с Git297bcbb. Native executable/AppIni/source closure/build flags и compiler record совпали с исходной SDK2e normal141; свежая runtime snapshot сохранена отдельно, прежняя не переписывалась. Full worker groups закрыты, leases released. Следующий отчётный шаг — временные графики всех записанных сом/пачек с actual input overlay и visual QA на M40. CPP4 на M40/ASan, retries и расширенная размерность этим gate не закрыты.
