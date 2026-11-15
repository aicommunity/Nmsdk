# Exact export и повторный анализ реального N4 diagnostic

Job `s11-declared-diagnostic-primary-m40-a1`. Source и actor `e20feccea50d814d9659c044d90611db704f6392`, control Git `9442648782bd89b062d98b093c287254a7997cfd`. Источник — completed `s11-budget16-frozen-diagnostic8-m40-a1` и его immutable controller/runtime.

10 объявленных production checks: 7 archive bounds, 2 report bounds и actual large-model export/restore/rescore. Explicit member384MiB, archive128MiB/expanded768MiB/64members без изменений. Сохраняются оригинальные model.json282794133B и trial bytes, schema2 исключает повтор одинакового content. Проверяются SHA модели/всех8 trials и совпадение метрик с исходным run-manifest.

Лимиты:6GiB memory/64tasks/21600s, output2GiB/free floor2GiB. Main PID2613259/start361092471, unit `timelearner-bf5dd7e5-5cab-4ce6-b9d2-fc65045fbfbd.service`, supervisor2609996. Работа начата; результат ещё не принят. Это I/O и независимый повторный анализ; новый Console/Train не запускается и scientific PASS не присваивается.
