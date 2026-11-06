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
Активные runtime/source эксперимента не обновляются. Тесты пока не выполнялись;
ни baseline failure, ни исправление, ни научный результат не заявляются.
