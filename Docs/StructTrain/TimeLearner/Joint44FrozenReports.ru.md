# Временные отчёты совместного normal44

Рецепт native-joint44-frozen-report-v1.json в Scripts/StructTrain/TimeLearner/specs
объявляет10 моделей: Classic/Branch × N0/N1 × C Off/On high100 boundaries
и два существующих low0.0001 positive controls. До чтения observations заданы
40 проб и60 trial/soma pairs из FrozenTrialChecks/LearnedBoundary source8021301e.
Target ISI[0.01,0.08], reverse foil[0.08,0.01], reset-per-trial и preserve-dynamics,
окно0.12s при2000Hz. Это штатные burst probes, не single-pulse characterization.

Метки/ID, ожидаемые паттерны и полные окна проверяются production scorer;
revision берётся из проверяемого export, pattern hash — из объявленных ISI.
JUnit должен содержать весь declared inventory44 и все10 выбранных test IDs.
Production renderer строит каждую сому с реальными входными samples/events,
полными samples, общим/локальным масштабом и увеличениями>=8px/native tick.
SI единицы не выдумываются. Positive guard требует spikes где-либо в четырёх
пробах; классификация оценивается отдельно. High100 silence — отрицательный
результат. Это LT engineering fixtures, не августовская stock-модель.

Full render cache хранится на отдельном диске M40. Git содержит рецепт,
метрики/manifests и выбранные изображения; primary proof82910cad не дублируется.
Пока render/reader checks и визуальный просмотр не завершены, рецепт является
подготовкой отчёта и не означает приёмку или scientific PASS.
