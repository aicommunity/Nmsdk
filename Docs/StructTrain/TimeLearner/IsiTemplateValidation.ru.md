# ISI-template анализатор: проверка нечисловых данных и источника

Source review Pulse2f6b5725 выявил два риска в NPatternResponseAnalyzer:
IsIsiTemplateMatch использует fabs(observed-reference)>1e-5 без проверки finite;
NaN делает это сравнение ложным. Источник Neuron ищется через конкретный
NNeuronTimeLearner, хотя Branch является отдельным UNet. Отсутствующий источник
возвращает тот же false, что и обычное несовпадение; для foil это может стать
положительным match. Это гипотезы по коду, пока не native runtime-подтверждение.

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
