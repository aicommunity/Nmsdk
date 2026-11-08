# Cold6: исходный снимок для baseline A4

Статус: только локальная подготовка исходников. Сборка SDK, численные проверки, изменение серверных источников/кэшей и запуск A4 здесь не выполнялись. Приёмка 248/250 cases и научный результат отсутствуют. Машиночитаемый список всех ID, Git blob/SHA256 и предложенный порядок находятся в `Cold6A4NativePreparedSource-20261109.json`; это документ постановки, а не созданный production CanonicalSpec.

## Зафиксированный код

Code Root `478cc35c0f1a314c34ad93aa0095b61836c658ec` — обычный merge `--no-ff` родителей `d2ee4691cbe04fbc8c82f585d27fb3a4da80ed61` и `db2e01a84fe51dd31dd20ef63b8703cacfd77f6c`. PulseLib остаётся `4a5c2ec9df9a9f704dcd8260714323494bfa4415`. Ветка: `codex/timelearner-cold-schema-native-preparation`.

Первый родитель содержит узкое исправление owning `QJsonValue` при записи cold6 `base_schema_version`, два новых model-backed codec cases и усиленные исходные Classic/Branch roundtrip cases. Второй родитель добавляет ранее проверенный exact-cache worker. При этом merge не меняет `App`, `Tests`, `CMakeLists.txt`, `cmake`, PulseLib, Bin или Rdk относительно d2ee. Его delta: документация worker, `native_acceptance_worker.py`, тест worker. Scripts tree точно равен db2: `2d49bcd6b0608f60ff57a53acb80310e56ebd9d0`. Будущие Train5/owner-token исходники в baseline не переносились.

Модели, физика, критерии, числовые tolerances, порядок кандидатов и строгий decoder не изменены. Восстановления типа через coercion нет. Числовая версия должна исходить из исправленного producer.

## Объём и порядок будущего запуска

Source inventory этой постановки — 252 scoped ID, из них выбрано 250: bounded 74, final 23, composite 149, preparation cancellation 4. Ещё два унаследованных `NativeCompositeDeadlineDiagnostic/*UnchangedLastFinalReachability` явно не выбраны. Число 252 не является полным инвентарём всех тестов SDK binary. Фактический compiled inventory обязан быть захвачен и сопоставлен production preparation перед запуском.

Первыми идут четыре cases:

1. `NativeCompositeDeclarations/ClassicCold6AndProtocol4StrictRoundtrip`;
2. `NativeCompositeDeclarations/BranchCold6AndProtocol4StrictRoundtrip`;
3. `NativeCompositeDeclarations/ClassicCold6AllBaseSchemasKeepNumericTypeThroughSerializedBytes`;
4. `NativeCompositeDeclarations/BranchCold6AllBaseSchemasKeepNumericTypeThroughSerializedBytes`.

Затем — прежние 17 NOT RUN после Classic declaration в историческом порядке с удалением уже выбранного Branch declaration, то есть 16 ID: autostart, N4/N6, cancellation/subset restore, growth-window limitation и source guards. Потом — остальные 230 regression ID, включая долгие 20k/C0 группы. Все 250 уникальны, группы не пересекаются. JSON содержит 137 предложенных leaves с прежними инженерными wall declarations; это не доказательство актуальной доступности ресурсов или фактического соблюдения budget.

Исторические 17 получены из Git-сохранённой постановки и совпадают с сообщением родителя об A3 (230 PASS /1 FAIL /17 NOT RUN). Перед запуском необходимо сверить их с actual A3 JUnit/runplan из отрицательного evidence, не заменяя им первичные данные. Полный прежний regression scope сохранён; failfast перестановка не сокращает его.

## Отрицательные данные и обязательные prerequisites

Отрицательная публикация A3: `a7dae002295800d520b1fd35975283f0daa2362d`. Родитель сообщил по неизменённым actual PRIMARY, что все шесть `archive-native23/*/initial-configuration.json` содержат `schema_version: 6` и строковый `base_schema_version: "sample0"`. Это прямой наблюдаемый результат опасного self-object proxy assignment. Первичные JSON не исправляются на месте. Из этого не следует недействительность физических waveform или ошибочность прежней визуальной интерпретации. Group-only archive23 assertion не подтверждал strict cold6 decode этих configuration sidecars.

A4 должен заново произвести все шесть archive bundles исправленным producer и сохранить actual initial configuration, полный group/native/CSV набор и исходный/конечный model readback. Старые bundles остаются отрицательными данными для configuration portability. Продолжение package/reader pipeline требует новой строгой проверки этих фактически выданных source configurations.

До любых SDK source/build reuse нужны независимая проверка отрицательной публикации, закрытие сбора A3, отсутствие held overlap/живых worker descendants и разрешение ответственного root. В этом документе ни одно из этих условий не объявлено исполненным. Active A3 source/cache/runtime не менялись.

Повторять 43 mock metadata cases для каждой byte-identical копии SDK по привычке не требуется. Прежняя code-scoped приёмка worker13/preparer30 переносится только в прежних пределах проверенных assertions и доказанного равенства dependencies. Здесь worker/preparer и Scripts tree равны db2. Заново обязательны actual eight-repository/source materialization, clean Git closure, actual same-SDK module import, fingerprint текущего источника и production canonical capture. Новый runtime/import, изменение dependency или конкретное неразрешённое сомнение могут потребовать нового metadata gate. Такой gate не заменяет actual source/canonical integration.

Подготовленный Root пригоден для дальнейшей production preparation после выполнения этих prerequisites. Ни запуск A4, ни его результат из наличия ветки не выводятся.
