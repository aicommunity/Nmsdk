# ISI-template анализатор: проверка нечисловых данных и источника

**Текущее состояние07.11:** исправленный baseline a3 воспроизвёл дефекты,
fixed12/12 прошёл на M40. [Проверенные primary и source bindings](IsiTemplateValidationNormalVerification.json).
ASan, второй сервер и вся матрица analyzer остаются открытыми. Ниже сохранена
история постановки, неверной первой fixture и ошибки доставки.

Source review Pulse2f6b5725 выявил два риска в NPatternResponseAnalyzer:
IsIsiTemplateMatch использует fabs(observed-reference)>1e-5 без проверки finite;
NaN делает это сравнение ложным. Источник Neuron ищется через конкретный
NNeuronTimeLearner, хотя Branch является отдельным UNet. Отсутствующий источник
возвращает тот же false, что и обычное несовпадение; для foil это может стать
положительным match. Это исходные гипотезы по коду; последующее native подтверждение a3 приведено ниже.

Добавлены четыре production C++ regression cases, каждый с Classic и Branch:
реальные storage/Environment/owner lookup; finite match/mismatch и обе
исторические формы reference; NaN/±Inf reference для target и foil; NaN
stimulus; отсутствующий источник. Тела production функций не копируются.
Сохранённый конечный допуск1e-5 не меняется.

Сначала проверяется исходный код на отдельном baseline SDK. После воспроизведения
нужен явный результат invalid/mismatch/match: повреждённые данные и отсутствие
источника должны инвалидировать наблюдение для обеих меток, не превращаться
в correct rejection foil. Исправление должно сохранить finite legacy поведение
и не заменять его V2-метрикой. Пустой/неверный shape reference требует отдельной
проверки без небезопасного индексирования. Начальный scope не объявляет всю
матрицу analyzer принятой.

Эти случаи относятся к MatchMode=1 legacy analyzer. Они не объясняют
InvalidObservation текущего native V2 stock Train и не меняют его критерий.
Активные runtime/source эксперимента не обновляются.
[Baseline SDK собирается на M40](IsiTemplateValidationJobs.json): root56ac50c9,
Pulse2f6b5725 с неизменённым Core46615e8, отдельные source/build/runtime.
Gate содержит4 новых функции (каждая Classic+Branch) и5 существующих controls.
Ожидаемые assertion failures сохраняются как baseline, не положительный PASS.
Процесс сборки подтверждён по PID/start ticks; native tests ещё не завершены.
Ни baseline failure, ни исправление, ни научный результат пока не заявляются.


## Исправление самой новой fixture до приёмки

В a1 обнаружена дополнительная неверная проверка временного флага после
CloseTrial: ResetTrialState уже устанавливает его для следующей пустой пробы.
Она удалена из новой версии теста; invalid проверяется по сохранённым LastMatch
и LastErrorClass, finite mismatch — по отсутствию invalid_measurement.
Запущенный a1 source не меняется. Его исходный результат и эта ошибка сохраняются;
четыре failed IDs сами по себе не докажут корректность baseline. Нужен повтор
исправленных тестов на том же неизменённом C++ после полного closure a1.


## Исправленный baseline a2

Root920d42a7 доставлен отдельным Git snapshot; child Pulse2f/Core466 не меняется.
Очередь a2 подтверждена живой и ожидает full closure/released lease a1.
После этого ей разрешено получить исключительное владение закрытыми source
и build cache, проверить старый runtime и обновить parent checkout через Git.
Единственное изменение кода root56ac→920 — исправленная тестовая функция;
алгоритмический C++ не меняется. Старый source SHA остаётся в Git и receipts.

Новый runtime создаётся отдельно. Старые runtime files проверяются до/после
сборки; symlinks в изменяемые source/build и общие mutable inodes запрещены
до изменения checkout. При несоответствии preflight останавливается. Исходный
архив a1, его JUnit и ограничение ошибочной fixture сохраняются. До результата
исправленного a2 дефект не объявляется runtime-принятым. Эта политика повторно
использует только освобождённый кэш; активные source/runtime не обновляются.


## Воспроизведение и candidate-исправление

Исправленная fixture a3 на root920d42a7/Pulse2f завершилась:9/9 объявленных
functions наблюдены,5 observation controls passed,4 ISI regressions failed,
valid JUnit/process agreement. NaN reference/stimulus, отсутствующий источник
и Branch lookup воспроизведены на реальных объектах. Это отрицательный baseline,
не PASS исправления. A2 до него остановился при обычном fetch частичного
снимка без Reports blobs; checkout остался56ac, расчётов не было. A3 импортировал
точный Git code packet и сохранил прежний runtime без изменений.

Candidate Pulsefe382a0 разделяет Invalid/Mismatch/Match. Неизвестный/пустой
источник, неприменимый ISI-размер, nonfinite reference/stimulus/residual и
нестрого возрастающий clock дают invalid_measurement и Match0 для target/foil.
Конечный mismatch остаётся обычным mismatch, допуск1e-5 сохранён. Источник
Neuron и lazy LTZone разрешаются через общий UContainer, как при ABuild.
Публичные properties, CSV schema, физика и lifecycle bool не меняются.

В fixed gate добавлены три controls: реальный lazy LTZone lookup обоих
learner, empty shape/NaN в дополнительном столбце и неверный порядок stimulus.
Итого7 новых test functions (каждая Classic+Branch) плюс5 прежних observation
controls. Дополнительные три controls пока не runtime-проверены; положительная
приёмка candidate12 ещё ожидается. Проверка на втором сервере и ASan также
не объявляются выполненными.

MatchMode1 сравнивает входные ISI с сохранённым TrainingPattern. Его Match сам
по себе не доказывает ответ нейрона. Научные метрики обязаны использовать
фактические выходные спайки; исторические отчёты с таким режимом требуют
отдельной проверки критерия. Августовские4/8–6/8 подтверждены настоящими LT
responses и не отменяются этим замечанием.


## Адресная normal приёмка на M40

[Точная сверка](IsiTemplateValidationNormalVerification.json): baseline a3
наблюдал9 функций (4 новых failed,5 controls passed), fixed root87e406bd /
Pulsefe382a0 прошёл12/12 без skips. Первые четыре regression bodies совпадают;
три дополнительных fixed-only controls не выдаются за baseline A/B.

В Git опубликованы все три исходные попытки и fixed primary. Проверены
35+9+40 baseline members и41 fixed member;766 source hashes каждой попытки
сверены с её фактическими root/Pulse commits. A2 declared root920, но не дошёл
до checkout: его source hashes относятся к56ac, что указано явно. Старые
13 runtime files сохранились;28 actual loaded files привязаны к процессу.
Все группы закрыты и leases released. ASan, второй сервер, полный analyzer
scope и этап3 остаются открытыми; положительный научный результат не добавлен.
