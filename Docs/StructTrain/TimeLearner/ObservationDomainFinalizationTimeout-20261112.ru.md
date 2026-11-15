# N4 Branch: поиск и финализация должны иметь разные бюджеты — 12.11.2026

В первой попытке полного домена Branch получил **execution=timeout, validity=unverified_execution**, reason=wall_budget_exhausted. Native PID2306881 закрыт; Classic PID2496264 того же cohort продолжает отдельное холодное обучение. Весь cohort пока не завершён. [Точные промежуточные доказательства](ValidationPlans/M40ObservationDomainTrainA1-20261112/interim-Branch-timeout/readback-integrity.json).

Поиск был ограничен1800s, процесс1920s, включая120s на запуск/остановку/экспорт. До остановки записаны652 `train_stopped_trial_*.csv` и соответствующие packet JSON; в native namespace1306 файлов/100085372 bytes. Итоговые state/summary/execution отсутствуют. Поэтому нельзя установить training outcome, финальную модель, число подтверждённых search observations или сходимость. Имена trial-файлов не заменяют итоговый пакет, а незавершённый экспорт нельзя выдавать за обученную модель или оценивать обычным Test.

SIGTERM stack указывает именно на экспорт: ExportNativeLearnedState → NativeCandidateWindowStateFactory::ExportRecovery/ExportImpl → EncodeNativeCandidateWindowServiceArchive → DecodeNativeCompositeTrainingArchive → DecodeMatchedOmissionEvidence → DecodeNativeProbeEvidence/EncodeNativeProbeEvidence. Сохранён [исходный stderr](ValidationPlans/M40ObservationDomainTrainA1-20261112/interim-Branch-timeout/runs/train/process/stderr.log). Это не доказательство отсутствующего assigned peak или физической невозможности обучения.

Проверенные точки повторной обработки архива:

- PulseLib `Core/TimeLearner/NativeCompositeTrainingEvidence.cpp`: encoder формирует все records/primary blobs и затем полностью вызывает decoder перед возвратом.
- `NativeCompositeLearnedState.cpp`: factory снова декодирует документ для portable proof; summary8 отдельно заново кодирует/декодирует архив для recovery ledger.
- Корневой `App/NeuroModelerConsole/TimeLearnerCompositeArtifacts.h`: publisher ещё раз декодирует пакет перед публикацией зеркал.

Повторные проходы подтверждены исходниками; их отдельная длительность и асимптотическая сложность пока не измерены. Проверки целостности, replay геометрии и service ledger нельзя просто удалить ради скорости.

Следующее действие — отдельная Branch-only попытка с теми же native source/runtime, подготовленным plan3/config8, полной областью наблюдения и **тем же native search budget1800s**. Для процесса явно объявляется900s финализации, всего2700s. Это изменение execution policy; настройки физики, алгоритма, целей и численных допусков не меняются. Старый timeout сохраняется. Classic текущего cohort не перезапускается, файлы работающего задания не изменяются.

После получения полного пакета следует измерить стоимость экспорта и убрать повторную обработку через один привязанный к завершённой границе проверенный archive/proof context. Сохраняются независимая проверка импорта, проверки внешних CSV и отказы при повреждении; кэш нельзя переносить на другую revision или незавершённую пробу. Отдельно нужен небольшой atomic diagnostic receipt о входе в финализацию, чтобы при аварии не терять различие между завершением поиска и завершением экспорта. Эти изменения ещё не реализованы и не приняты.

Предыдущий [preflight5/5](ValidationPlans/M40ObservationDomainPreflightA1-20261112/RESULT.ru.md) остаётся действующим в своём scope. Само исправление полного домена пока не прошло завершённый actual Train gate; новый timeout не создаёт ни сертификата, ни scientific verdict. Весь исходный план остаётся открытым.
