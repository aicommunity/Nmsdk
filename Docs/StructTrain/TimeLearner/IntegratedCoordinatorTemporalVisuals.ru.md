# Временные графики integrated coordinator: принятые примеры

[Открыть галерею 42 оригиналов](../../../Reports/StructTrain/TimeLearner/s11-integrated-coordinator-visual-a2/index.html). PNG1920×960, без прореживания, реальные входные импульсы поверх потенциала каждой записанной сомы. Для подробного анализа открыть оригинал: zoom даёт не менее8 пикселей на native timestep. Рассмотрены все42 выбранных изображения: подписи, оси, легенды и кривые читаемы, обрезанных заголовков не обнаружено.

## Что подтверждено

На M40 точный reader root2e выполнил16 phase reports и4/4 проверки на опубликованном primary26a602e8. Все2233 исходных файла сохранены; нового Train/Test не было. Сформировано5752 вида:368 training,120 calibration и24 frozen trial–soma pairs. Автоматические проверки охватывают весь корпус; ручная визуальная проверка — только42 выбранных оригинала, не5752.

В Git сохранены24 overview для всех frozen предъявлений и сом,12 подробных target/foil zoom и6 first/last training examples. Всего5784905 байт PNG и972280 байт metadata.tar.xz; полный HTML/PNG/SVG/PDF остаётся кэшем M40: `/media/user/Data/TimeLearnerRefactor/ReportsCache/integrated-coordinator-visual-a2/reports`. Полный отчёт воспроизводится из primary и сохранённого reader/recipe. Сверены644 archive members,42 PNG с исходными manifests и hashes reader против Git blobs. [Независимая проверка и перечень просмотренного](IntegratedCoordinatorTemporalVisualsVerification.json).

Первичный data commit `85e85c90e400b7c165f3011c4a8bae004535f43e` содержит состояние producer до ручной проверки: manual_review=false и selected_images_published=false в raw coverage не переписаны. Последующая приёмка записана отдельно. В derived index добавлены ограничения трактовки; top-level SHA256SUMS обновлён только для этого изменённого HTML. Изображения и первичные архивы не менялись.

## Научная область применимости

Четыре завершённых инженерных случая — Classic/Branch × ModelSpec1/2. Для каждого после historical same-matrix calibration:TP2/FP0/FN0/TN2 в четырёх предъявлениях target/foil/foil/target. Это не исходная4-input/8-pattern матрица, не independent evaluation и не статистически независимые повторы. v1/v2 означает сериализацию ModelSpec, а не ControllerVersion. Четыре отрицательных stopped Train проверены в training reports; Test для незавершённого обучения не создавался.

Профиль — двухвходовый EditingRig-derived, с отдельной LTMembrane0.3nF. Stock NSPNeuronGen/августовский граф отдельной LTMembrane не имеет. Кроме этого отличаются DissociationTC1ms против5ms и InhChannel RestingResistance100MΩ против10MΩ. [Полная постановка различий](ScientificProfileDrift.ru.md). Эти рисунки подтверждают инженерную цепочку; научный результат stock-модели ими не установлен, эффект LT отдельно не выделен.

Синяя линия — SumPotential конкретной сомы, фиолетовая отметка — реальное событие downstream LTZone. Она не является отдельной кривой LTMembrane или потенциалом действия сомы; непосредственно сопоставлять LT threshold с Y сомы нельзя. SI units не подтверждены: показаны model units. Shared Y означает общую шкалу одного канала между пробами, а не обязательную общую шкалу разных сом. Сравнивать амплитуды разных сом следует по числам оси. В training record_spikes=false; отсутствие отметок спайков не доказывает молчание. Отсутствие стимула или события внутри отдельного tail zoom допустимо: начало ответа находится на соседнем zoom/overview.

Normal coordinator8/8 и20 native phases приняты отдельно. ASan304 и последующие shared SDK gates ещё не приняты; исходные этапы1–12 остаются частичными. Для итоговой науки нужны завершённый stock Train, полный frozen8-pattern Test, legacy/V2, order/ITI/reset и остальные физические профили.
