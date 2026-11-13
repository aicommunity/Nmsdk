# Реальный расчёт выполнен, baseline отвергнут старым reader

Попытка s07-burst-readback-console-six-m40-a3 завершена с ошибкой consumer-аудита. Реально завершены два Console процесса: Classic replay и Classic matched; это три записанных наблюдения — replay, source baseline и main matched. Изменение Rs и Branch probes до ошибки не запускались. Все группы закрыты, внешний и внутренний lease released.

Сборка Root49689590c / PulseLibdfb9a9824 устранила отказ finished summary: native idle controller readback прошёл проверку. Новый отказ unsupported_observation_schema возник в Python-аудите baseline_trial_1.json. Полная пачка schema7 использует native observation schema6 без назначения пика, а consumer направлял её в legacy audit_probe, принимающий schema3. Та же несовместимость находилась в общем _trace.

Rootda64c4c7e3988289d6fc2fc314645ed3634ff8f1 выделяет строгий audit_subset_observation и lossless Console CSV header adapter. Graph/restoration checks остались в полном wrapper audit_subset; waveform-only результат прямо указывает restoration=not_checked и не выдаёт измерения обучаемого пика. Legacy reader по-прежнему отвергает schema6. Новый baseline consumer и общий trace reader используют правильную схему, не меняя ни одного отсчёта.

[Проверка на этих фактических файлах прошла5/5](../M40BurstReadbackRecordedDataA1-20261113/RESULT.ru.md). Это подтверждает исправление потребителя в объявленной области; исходная A3 попытка остаётся failed. Полная серия шести probes повторяется отдельной A4 на прежнем бинарнике без пересборки.
