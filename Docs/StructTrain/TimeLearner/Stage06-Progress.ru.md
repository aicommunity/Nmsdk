# Этап 6: общий контроллер — работа продолжается

Полный общий контроллер и ControllerVersion=2 ещё не реализованы/не приняты.
Подготовка native A/B controls выявила TL-015 — неинициализированный live Neuron
в Classic. Сначала исправляется этот дефект владельца: LiveRebuildInit.ru.md.
Отдельно выявлен TL-016 — mixed effective rates после создания/growth legacy
элементов. Это ограничивает пригодность baseline для проверки нового контура.

В root добавлен opt-in native compatibility control. Каждый case запускает
отдельный процесс, считает actual stimulus edges и полный hash soma samples,
сохраняет последовательность состояний, параметры и отдельный effective graph.
Трёхсекундный budget не считается завершённым Train или научным PASS. Короткие
обязательные regressions проверяют Init и физический импульсный ответ после
cold Reset, без дополнительных Build/Calculate в проверяющем коде.

Механическое выделение ChooseDelay, ComputePeakTimes, DetectPulses и демпфированного
R proposal сохранено в отдельной PulseLib-ветке refactor/timelearner-s06-controller-core,
commit ad955ba15409db32920f06867f4d5acdcd3caefd. Оно пока не входит в root gitlink
и не принято в develop. Новый production baseline должен включать TL-015 fix;
затем нужны A/B observations/decisions и адресные проверки границ/overshoot.
Fallback от measured delay к model delay останется явно Legacy policy, а не
доказательством измеренной синхронности будущего контроллера.

Остаются общие ProbeSpec/Observation, revision invalidation, независимая final
проверка всех входов, bounded search и topology adapters с native scheduler.
Различия Classic round-robin и Branch reverse/mute не заменяются общим
single-pulse протоколом. Совместимость старого кода и исправление алгоритмов
должны иметь разные commits и разные критерии проверки.
