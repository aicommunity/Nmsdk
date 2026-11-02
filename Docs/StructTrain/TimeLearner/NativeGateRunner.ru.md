# Декларативный запуск native CI checks

Команда native-gate SPEC.json --output NEW_DIRECTORY использует production
owned process_runner и неизменяемый заранее собранный runtime. Она не выполняет
checkout, сборку, изменение конфигурации либо восстановление модели. SPECschema1
kind timelearner_native_test_gate содержит runtime_manifest, source_root,
expected_test_ids (Suite/Case), maximum_wall_seconds и asan_options.
Input paths разрешаются относительно SPEC; output не может пересекать source
или runtime. Loader environment берётся из runtime manifest и восстанавливается
после операции. Фильтр строится из exactIDs, без shell и glob-инференции.

Проверяются реальные loaded-file capture, exitcode/JUnit agreement, точное
множество всех случаев, totals и отсутствие skipped/uncompleted cases. Полный
failed JUnit является валидным наблюдением неуспешного тестирования; timeout,
обрыв или missing case не становятся PASS. Assertion status, execution и
validity разделены. Scientific verdict всегда null. Источники сверяются с
runtime source_closure до и после процесса. Нельзя менять их пока job работает.

Spec search-termination-configured-native-v1.json объявляет34 source-reviewed
IDs; пути-заполнители нужно заменить на действительные runtime/source. Это
native service, configured/XML/Copy, repeatedN0 и четыре completed-boundary
transfer controls. Набор нужен для обнаружения регрессий, а не для заявления
сходимости всех моделей. Первичная server-приёмка нового runner ожидается.
Параметризованные/slash-containing GTest IDs пока явно не поддерживаются;
unknown/дублирующие IDs отвергаются. Generated Python launchers не нужны.
