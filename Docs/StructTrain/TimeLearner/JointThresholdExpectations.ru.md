# Ожидания frozen-response в joint ModelSpec2/C-search fixtures

Статус: исправление тестового helper подготовлено; повторная native приёмка
ещё не выполнена. Это не изменение алгоритма learner или научного критерия.

Исходный joint normal42 source9f92a40b завершился с34 passed/8 failed.
Все восемь новых Classic/Branch × N0/N1 × C Off/On boundary cases сохранили
construction и effective LTZone threshold100. Их32 frozen trials были valid,
complete, uncensored, с неизменными model-before/model-after и нулём spikes.
Failure был единственным `EXPECT_GT(observedSpikes,0)` в FrozenTrialChecks.
Общий helper ошибочно интерпретировал legacy suffix `_spiking`, добавляемый
при любом initialThreshold!=1, как положительный физический response contract.

В новом helper ожидание `optional<bool> expectedSpikes` передаётся явно:
true требует хотя бы один реальный spike в четырёх пробах, false требует ноль,
nullopt оставляет только прежние validity/completeness/frozen-state проверки.
Имена artifacts больше не задают физическое ожидание. Сами legacy filenames,
включая `_spiking` у high100, сохранены для прямого сравнения первичных данных;
нормативен отдельный `*_frozen_expectation.json` с expected/observed spikes,
effective threshold и model revision, scientific_verdict=null.

Восемь high100 случаев явно требуют отсутствие spikes. Существующие четыре
низкопороговых LearnedBoundary cases сохраняют positive guard через явно
переданный true, с теми же значениями всех прежних default аргументов.
Candidate-threshold loop также передаёт прежний узкий positive contract
явным аргументом, без чтения имени artifact. Критерии сходимости, физика,
CapturedPerInput, tolerances, бюджеты, порядок проб и storage образы не меняются.

Адресный повторный gate расширен42→44 двумя ранее существовавшими positive
controls при threshold0.0001 и explicit sync0.2; оба уже входили в full304,
чьё множество осталось прежним. Положительные случаи не удаляются ради
прохождения silent controls. Сначала требуется реальный normal44, затем
согласованный ASan и full304/readers. Первоначальный failed42 сохраняется.

High100 silence не является успешной классификацией или NonSeparable
доказательством. Эти двухвходовые engineering LT fixtures не подменяют
августовский stock четырёхвходовый граф. Совместные C On / ModelSpec2 с поздним
readout0.005 и калибровкой остаются отдельным незавершённым требованием;
присваивание нового порога не заменяет измеренную calibration transaction.
