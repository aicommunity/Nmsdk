# N4 diagnostic16 A2 — исправлен только native loader environment

Предыдущий [A1](../M40RecordedN4Diagnostic16A1-20261112/RESULT.ru.md) закрыт с15 raw proofs:0 native children/0 observations, original main exit1, released lease. Новая попытка использует отдельный job ID/controller/output и допускается после32-case metadata gate.

Tool `251dddc6293bfb4bf620b46d25adf2c633cae8fc` применяет ровно три runtime loader key на execution boundary общего pipeline и восстанавливает parent environment при любом исходе. Строгий guard executor сохранён. Compiler/runtime, Root448b153f2/Pulse7b524b8, исходные модели, thresholds, target matrix и все численные параметры совпадают с A1. CPP не пересобирается, physics/storage profiles не меняются.

Request отличается от A1 только job_id и tool_commit. Цель — получить по8 полных diagnostic observations для Classic/Branch,2 s/reset-per-trial/2000 Hz, source thresholds inherited fixed; никаких Train, калибровки, ретаргетинга и template fallback. Источники/первичный XML/CSV/transport summaries — те же Git inputs, проверенные raw size/SHA.

У Classic фактически прочитан source LT threshold100 (configuration и neuron metadata совпадают). Это высокий фиксированный порог источника, а не результат подбора classifier threshold. Серия даёт baseline временные отклики и измеренные свойства source model; итоговую оценку настроенного классификатора она не заменяет. Выбранный впоследствии порог требует отдельного реального подтверждения с явным протоколом и сохранением stopped provenance.

Root исходного пакета: native primary SHA `f00fd600e1ca5341e4cdd1e8216085a8fea2dc3719f0b624b98ea71fdadb4f25`; правильная provenance композиция описана в `RecordedN4CorpusProvenanceCorrection-20261112.ru.md`. Input cache commit e48a05fdde0a43e441e8718278501cfd16b11510. Runtime manifest SHA `8dcec12353cfff0c198bebc6e9c2c18de557965500b34924b76c0583299ee6ad`.

Приёмка требует реальных обоих Console executions, всех16 полных проб, frozen model/threshold, неизменных input/source/runtime, exact closure всех конечных групп и released lease. Только затем публикуются metrics и temporal reports по всем паттернам и сомам. Исходные stopped training outcomes остаются invalid_observation/budget_exhausted; положительный scientific verdict не выдаётся из технического завершения.
