# Managed native preflight: адресная приёмка04.11

Это приёмка данных отдельных checks, не promotion implementation branch
и не завершение этапа10. Child gitlinks/C++ physics не меняются.

Elder source43d32cf211f0366d1237726c5be423db72565d41 прошёл62/62
kernel/resource tests без errors/failures/skips, включая отказ при смене
symlink alias после reserve и до direct native submission. Source34361/61
сохраняется отдельным предыдущим срезом. Новая suite62 на M40 ещё pending.
Evidence8ae97bde52ee4b2b11f8144d10d33f83fe7cf3ae:292 members verified
на worker и после Git transfer локально.

M40 source713c811c4654152759aeb02f19d5b7bb0071515c прошёл19/19:
17 policy/portable consistency checks и два реальных public CLI preflight
ClassicN0/BranchN1 с policy2/schema3 owner/controller/managed-unit context.
Immutable Console SDK sourcef679d0410dd00a36995f9d32cc03812438819bb7;
model_ticks0 и training_started=false подтверждены actual execution.json.
Native4GiB/controller256MiB/aggregate4.25GiB, capacity6GiB; оба процесса
и supervisor закрыты, global operational lease освобождён после readback.
Переподписанная подмена lease token остаётся invalid.

Предыдущая source43d32cf211 попытка17/19 сохранена полностью:
два process_error/-9, Result=oom-kill, MemoryMax536870912. Это ошибка
ASan fixture budget, а не нехватка диска и не отрицательный научный результат.
После свежей проверки родительской группы и двух отдельных signed native
bindings освобождён только operational global lease; failed verdict не изменён.
Следующая попытка сохраняет исходные JobSpec/runtime/assertions, изменяя
только выделенную память тестовой Console.

Evidence9ea7ecff7dfb319dfd3073bb1ba01bb80edf0d8b включает failed65 и
passed142 архивных файла. Все member bytes/SHA256 проверены на worker
и локально; оба code commits доступны в origin feature branch.

[Артефакты Elder62](../../../Reports/StructTrain/TimeLearner/s10-managed-unit-reservations-elder-a2/README.ru.md)
и [M40 failed/passed](../../../Reports/StructTrain/TimeLearner/s10-native-managed-preflight-a3/README.ru.md).

Открыто: реальная связка Train→export→calibration→frozen evaluation,
PostTune, delegated coordinator/self-allocation, cancel/recovery/interruption
и полная production resource matrix на двух workers. Новый backend ещё не
рекомендован по этим preflight controls. Научный PASS классификации отсутствует;
joint normal304 требует отдельных readers/ASan и не заменяется этими19 checks.
