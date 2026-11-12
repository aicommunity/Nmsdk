# Независимый N4 readback A1: отказ provenance, 3/4

Исходный job `s08-recorded-n4-independent4-m40-a1` завершён за 284.89 s, whole group closed, lease released, diagnostics clear. Четыре адресных теста выполнены без skips/errors; три прошли. Оба полных экспортированных пакета, summary8, embedded primary и все boundary-response samples приняты DATA-аудитором. Проверка qCompress corruption также прошла.

Closure-проверка отказала: в `RecordedN4RoundtripPrimary-M40-20261112/primary.tar.xz` под `controller/` ошибочно включён `s08-recorded-n4-sdk36-m40-a3-controller` с36 дочерними процессами вместо `s07-recorded-n4-native-roundtrip-m40-a3-controller` с2. Это ошибка подготовки manifest сборщика, а не дефект моделей или новая ошибка C++ roundtrip. Сам generic collector проверил byte inventory и закрытие перечисленных групп, но не смысловую принадлежность controller к native root. Следовательно, его технический PASS не доказывает согласованность provenance.

Исходные 189 members и архив не переписываются. Его native primary остаётся доступным, но controller-subtree объявляется посторонним. Правильные исходные native2 proofs уже сохранены отдельно в Git: `../M40RecordedN4NativeRoundtrip2A3-20261112/completed/controller`. Для исправления нужна явная проверяемая композиция native primary и этих proofs с проверкой job ID, обоих JUnit ID и точных child bindings. Нельзя просто изменить ожидаемое число children на36.

Raw отказ, исходные результаты и before/after snapshots сохранены в `failed/` с отдельными SHA. Отказ остаётся отказом. A2 добавляет исходные модели и рисунки, но до исправления привязки controller также не может получить полный PASS.

Новая classification, cold Train и научный PASS не заявляются.
