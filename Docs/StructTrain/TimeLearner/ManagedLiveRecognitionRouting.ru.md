# Pending: передача конечной live recognition модели в managed Test

Для Train job schema2 управляющий pipeline принимает отдельный маршрут Train→evaluate. Native learner уже выполняет conversion/PostTune/калибровку внутри штатного scheduler. Повторный export из solo после этого этапа запрещён самой схемой маршрута: он потерял бы конечное распознающее состояние.

Граница Train готова только при completed execution, valid evidence, completed_boundary и recognition_available. Фактический native recognition-model.json подставляется в следующий unsigned evaluation job. Полный production auditor сверяет finalization report, окончательный пакет и native execution, после чего frozen worker заново импортирует именно этот пакет. Исходный solo архив нужен для проверки provenance, а не для восстановления шаблонного Test.

Незавершённая finalization/Train не запускает Test даже при наличии промежуточного solo certificate. Cold schema1 маршрут Train→export→[PostTune]→[calibrate]→evaluate сохраняется. Continue/reconcile используют ту же привязку к конечному пакету; повтор завершённого continue не создаёт процессов.

Подготовлены6 actual CLI tests: Classic/Branch×fixed/grid и два остановленных live Train. Во всех положительных случаях — новый cold Train из проверенной ModelSpec2 постановки, отдельный frozen native процесс, полное равенство переданного final recognition package и неизменность его bytes; export/calibrate каталоги вне Train отсутствуют. Планируемый объём10 отдельных native units. Fixed policy не требует successful detection; counts остаются результатом измерения, а не условием корректной передачи.

Параметры grid и trial design берутся из сохранённых measured declarations; готовые learned graphs не устанавливаются вместо обучения. Общая физика и profile_archives берутся из исходного cold job. KeepDone/Auto, weight_probe_threshold2 и ModelSpec2 initial threshold не заменяются на произвольный новый профиль. Это engineering same-matrix проверка, не independent scientific Test и не causal LT/no-LT исследование.

Пока проверен только AST. Новые runtime tests не выполнялись, код не объединён в develop. Нужны полный cold coordinator regression, declaration11, scorer reader regression, фактический live6 и оставшиеся PostTune/cancel/recovery/multirate/physics cases. Только этап0 полностью принят;1–12 остаются частичными.
