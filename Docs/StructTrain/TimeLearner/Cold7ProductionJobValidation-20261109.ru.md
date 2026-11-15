# Cold7: исправление ранней проверки production job

В source e91 функция native_pipeline_worker.validate_job распознаёт cold7 в конце проверки, но раньше безусловно вызывает project_training_configuration. Последняя принимала только cold6 и legacy1–5; cold7 с composite_measurement отклонялся ещё до новой ветви. Поэтому успешные metadata readers и C++ export tests не подтверждали готовность Python production Train/preflight.

Добавлена явная ветвь7 в общем private validation projector: strict candidate_window configuration view, затем существующая проверка общего base1–4. Оригинальная декларация, её SHA, policy2 и отправляемые в Console байты не заменяются projection. Legacy1–6 сохраняют прежний dispatch. Физика, target, CapturedPerInput и исходные tolerances не меняются.

Новые worker regressions проходят production validate_job для train/preflight, Classic/Branch и N2/N4/N6 declarations; отдельно проверяют base1–4, отсутствие mutation/доказательства обучения, пропущенную/повреждённую policy, неизвестные поля и mixed versions. Это metadata validation, не native preflight или научная серия. Обязательны серверный regression gate и последующий реальный Console cold7 Train→export→Test. Исправление подготовлено в отдельной ветке; активная SDK native119 не меняется.
