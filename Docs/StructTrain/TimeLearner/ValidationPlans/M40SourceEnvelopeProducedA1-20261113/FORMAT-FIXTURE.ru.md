# Проверенный fixture source-envelope формата

Это повторное представление прежнего A4 контрольного corpus для проверки нового reader, не новое обучение или научный результат. Полный пакет около1.08MB; старое каноническое A4 primary остаётся отдельно опубликованным. Реконструируются те же исходные файлы, их manifests не меняются.

Reader: portable_primary.restore_native_bundle(bundle.json, new_output, compatibility=ALIAS_ADAPTER). Он восстанавливает literals,18 jobs из recipes и проверяет итоговые bytes/namespace;6 glog aliases проверяются и опускаются прежним адаптером. Restore не подтверждает fresh execution.

Весь путь production collector → package → restore → шесть production primary audits принят на M40. Для хранения N4 результатов потребуется отдельная actual large-file проверка; Git dependency reuse общего source этим fixture не реализуется.
