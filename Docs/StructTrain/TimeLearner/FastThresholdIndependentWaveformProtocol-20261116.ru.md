# Fast threshold primary: независимая проверка исходной waveform — 16 ноября2026

Новое полное Fast threshold primary включает два закрытых дерева: исходный frozen8 и реальный baseline100/candidate study. Это позволяет на Elder проверить не только метрики, но и записанное в result.json утверждение baseline_waveforms_equal без доступа к исходным каталогам M40.

Production restore_native_bundle проверяет все logical members и подтверждённые duplicate aliases. Production audit_run_manifest и native diagnostic scorer проверяют обе реальные серии; дополнительный audit исходного frozen run проверяет его полные источники. Восстановленный исходный manifest дополнительно связан по size/SHA256 с proposal.source_manifest: неверный prefix или сравнение baseline с самим собой не подтверждает replay. Затем сравниваются все8 observations по trial_id: полные массивы samples, model-before/after, labels/pattern_hash, reset policy, реальные stimulus timestamps, частота, complete/valid/censored. Изменённый run_id не является частью равенства waveform. Новая simulation и independent scientific evaluation не выполняются.

Дополнительный original_baseline_prefix объявляется в controls заранее и должен оставаться внутри restored root. Старые пакеты без этого поля продолжают проверяться в прежней области, а readback явно пишет original_baseline_waveforms_checked=false. Их историческая доказательность не повышается задним числом.

Новый test_restored_threshold_primary использует штатные production readers и реальные сохранённые данные, без копии тела learner и без требуемого положительного научного результата. Приёмка этой feature требует отдельного завершённого серверного job; один успешно прочитанный manifest её не заменяет.
