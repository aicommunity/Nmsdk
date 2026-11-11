# Native119: готовность изменённого dataset перед snapshot

Root f2f8e611d51f1b4f23ef0471ddfc7618e68a59ea на Elder/M40 завершил30/119: на каждом29PASS/1FAIL/89not-run,2 leaf gates. Исправленный foreign-reference case прошёл; package29 дал28PASS/1FAIL. [Elder original records](ValidationPlans/Native119DatasetReadiness-20261110/elder-negative-readback.json), [M40 original records](ValidationPlans/Native119DatasetReadiness-20261110/m40-negative-readback.json). Full119 не принят. Полный lossless primary этих запусков ещё не опубликован; metadata не заменяют его.

Единственный FAIL — NativeCandidateWindowPackage/ActualForeignDatasetCannotReplaceRestoredFullSource: ExportDatasetSnapshot выбрасывает invalid_model_identity: DatasetMatrix/model_not_ready_or_initialized до вызова импортера. Setter NDatasetMatrix::SetMatrixData штатно устанавливает Ready=false. Тест менял матрицу и сразу экспортировал физический snapshot, пропуская lifecycle владельца параметра.

Кандидат вызывает dataset->Build(); dataset->Init() после изменения MatrixData, без расчёта модели, Default, learner-specific дополнительных Build либо проверки lifecycle return bool. Затем проверяются Ready/Init, actual readback изменённого ISI и отличие physical snapshot. Подготовка обученного состояния должна отвергнуть корректно построенный чужой dataset с точной причиной composite_package_source_isi_changed. Таким образом форматный/initialization отказ не может подменить проверку исходных данных.

Production алгоритмы/физика/допуски не меняются. Source candidate ещё не скомпилирован/runtime не принят. Следующая приёмка — real complete TU и адресный negative control, затем весь119 без исключений.

Закрытый corpus package29 содержит результаты28 прошедших случаев, включая actual model exports/imports, C0, warm, partial/stopped/zero-group и legacy5. Его можно независимо использовать для diagnostic проверки production reader16 после проверки точного набора файлов и immutable hashes; это не отменяет FAIL119 и не превращает всю серию в принятую. Окончательная приёмка требует повторения readers на принятом итоговом subject.
