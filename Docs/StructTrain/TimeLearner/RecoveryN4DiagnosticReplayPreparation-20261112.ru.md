# Диагностика окон настоящего N4 recovery Train — подготовка12.11.2026

Branch native и независимый DATA audit завершились:valid artifacts, invalid_observation/rejected_candidate_window:missing,28logical groups/168native probes. Четыре cursor_advanced и финальный invalid_budget_stop подтверждены ledger; Exact/certificate отсутствуют. Classic ещё рассчитывается. [Точные поля](ValidationPlans/M40StockCold8TrainA1-20261112/INTERIM.ru.md).

Обнаружен пробел инструмента анализа:production candidate_window_diagnostic_replay принимал только package6 и не мог разбирать source7/cold8 recovery. Добавлен явный dispatch6→прежний auditor,7→recovery package auditor; неизвестные версии продолжают отвергаться. Чтение full/omission CSV, проверка их digest/grid и geometry replay не меняются.

Подготовлен реальный worker-only test для Branch N4:найти все пять rejected groups по recovery ledger и предшествующий valid group того же assigned input; повторить geometry на исходном окне и на полном сохранённом наблюдении. Ожидается только совпадение исходного missing, не оптимистичный ответ полного окна. Отсутствие пика, ambiguity, clipping и nonrepeatability остаются явными исходами. Любой post-hoc valid не превращается в новый Train certificate. Старый package6 replay сохраняется отдельной проверкой.

Серверная проверка нового dispatch/replay ещё не выполнена. Она запускается после закрытия всего Train cohort, чтобы не читать locked source незавершённого задания. Исходный Train и его runtime не меняются. Следующий алгоритмический вывод должен опираться на полный primary и реальные waveform, а не на prediction или максимум всей пачки.
