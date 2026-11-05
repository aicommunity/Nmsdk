# Отдельный процесс: сравнение старого и общего recognition-кода

Восемь реальных обученных owner packages2cb воспроизведены в16 новых процессах на Elder: каждый пакет импортирован в старый и новый runtime. Все16 JUnit1/1 прошли без failures/errors/skips. Actual input/soma CSV в каждой из8 пар совпали побайтно; production audit также сопоставил каждую новую кривую с проекцией исходного paired waveform. У каждого процесса отдельный PID/start binding. Исходные файлы до/после неизменны; родительская группа закрыта, lease released.

| Runtime | Фактический compiled root | PulseLib |
|---|---|---|
|baseline|`1eab24decb6432947afc928e7f049f3a07de2709`|`8644c50984c45a2211de13a75fe05cffc5bb3154`|
|candidate|`2cb855677f3e7160cd01837f62c649b18803ebf0`|`f6a917d395b21610f6bf6cbb0ed945e6cdee31dd`|

Python package `f3af229da421c27f0c8e2756dc858d6af90c6092` выполняет replay и аудит; он не объявляется compiled SDK этих двух runtime. [Primary375 members](../../../Reports/StructTrain/TimeLearner/s06-recognition-shared-saved-ab-a2/bundle.json):304968 bytes, SHA256 `ec79bcc991e6c0d15fd8571ad3c0f041ab84db05ae886462f41aa26c9f13e92e`. Evidence `87ea825ae4d2a1e91414b8e30cd00827d4f7ea25`. Независимо сверены321 Python source blobs,30 published checksums, все archive members и actual XML/CSV/process bindings. Первоначальный preflight A1 не запустил ни модели, ни lease: harness неверно ожидал абсолютный path внутри source_closure.root; A2 использует явный native_source_root, проверенный по фактическому Git HEAD. Отказ сохранён в primary.

Этот gate проверяет saved-state transport через прежний и выделенный общий recognition-код. Он не является cold retrain старого алгоритма, самостоятельной классификацией или доказательством эквивалентности любого режима/модели. Исходные packages получены ранее завершённым cold Train2cb с explicit ISI[.01,.03]; здесь переобучения не было.

## Временные графики

[Галерея16 проверенных оригиналов](../../../Reports/StructTrain/TimeLearner/s11-shared-saved-ab-visual-a1/REVIEWED.html) содержит overview всех12 сом новой версии и4 ранних zoom. Все16 PNG1920×960 просмотрены в исходном размере: формы ответов и входные импульсы различимы, заголовки/оси/легенды помещаются. [Привязка ручного просмотра к каждому SHA](../../../Reports/StructTrain/TimeLearner/s11-shared-saved-ab-visual-a1/manual-review.json).

Полные два отчёта обеих версий: `/media/user/Data/TimeLearnerRefactor/ReportsCache/shared-saved-ab16-a1/reports-baseline` и `reports-candidate`. Всего120 views, по183 файла/12040423 bytes на отчёт. Все native samples сохранены; zoom имеет не менее8 pixels/tick. Два actual production renderer checks по1/1 прошли без skips. Reader/renderer source `0bebed450eb2f9bfc69e6c428ac2b2331dc6fd7d`/323 Python files; это renderer package, не новый C++ build. Evidence `ec150765e645e917c665d598004c22d47611d318`:metadata56780 bytes/15 members; выбранные16 PNG2629527 bytes. Полные PNG/SVG/PDF в Git не дублируются. Ручной просмотр всех120 не заявляется; побитовая идентичность будущих PDF с другими timestamps/fonts не обещается.

Синий сигнал — native Soma.SumPotential, оранжевый — фактически записанный общий вход. На свежем процессе выполнен штатный Init/Reset; внутри заявленного окна генератор непрерывно повторяет одну пачку. Между повторениями отдельного Reset нет, поэтому видимое накопление ответа относится к continuous transport protocol. Это не независимые reset-per-pattern trials. Перемещение baseline вверх не является само по себе ошибкой или доказательством классификации. Все окна полны по объявленному ProbeSpec; ими не подтверждается длительность любого возможного позднего ответа за границей окна. LT spike events и потенциал отдельной LTMembrane здесь не записаны; SI единицы сомы не подтверждены. Имена spiking в fixture не заменяют запись событий спайка.

[Проверка metadata, source и primary integrity](SharedRecognitionSavedABVerification.json). Исторические августовские4/8–6/8, критерии classification и robustness этим gate не пересматриваются.

## Новая комбинация и дальнейшая приёмка

Integrated branch объединяет historical adapters, strict native cohort readers и production owner replay/render modules настоящими merges; App/Tests/CMake остаются равны2cb, native childf6 сохранён. Runtime всей новой комбинации ещё требует собственной SDK/coordinator corpus. На M40 full ASan304 продолжает работу; [следующая очередь Owner8/readers128](../../../Reports/StructTrain/TimeLearner/s07-asan-owner-followup-a2-pending/job.json) не запускает модели до304 PASS, реального kernel closure/release и публикации данных с точным evidence commit. Queue A1 с provisional origin отменена до любых native launches; A2 требует опубликованный source archive, а не подстановку source-code SHA вместо evidence SHA.

Полностью принят только этап0;1–12 частичны. Для завершения остаются совместная SDK, обязательная mode/storage/physics matrix, ConditionSpec/очереди/publisher и научные контроли.8/8 не является условием завершения.
