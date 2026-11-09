# Native48 A4: V3 плана и изолированный donor V2

Code root956 не меняется; этот обычный metadata-потомок сохраняет393/V2 и первоначальный1b8 pack.1b8 содержал все1014project code blobs, но не пятый Git control blob Docs/Audit/.../.gitignore. Старый Root receipt проверял SHA/размер packet, а не checkout/projection closure. Он не переписывается.

Новый6704171B pack870f добавляет ровно этот Git object. В изолированном локальном Git без checkout/alternates проверены4846objects, root/tree chains,1014codepaths, все5controlblobs, финальныеCMake/App/Tests/Scripts. Это Git/hash-метаданные, без сборки/тестов.

Свежий donor предназначен исключительно для standalone Git объектов: sparse /*,!Docs,!Reports;1014physicalcodefiles. Docs-control доступен черезGit и намеренно не materialized. Ledger row имеет точные git_mode/git_blob/bytes/sha256. Ожидаемая будущаяSDK4030 составлена из1014новыхroot и3016неизменныхchildfiles изA3negative; actual4030namespace/imports/cache readiness ещё не проверялись.

V3 JSON и input path-bindings хранятся в компактном primary archive. Exact helperV2 request/pack SHA и ожидаемые ledgers закреплены; агент не выполнял серверных записей. Donor delivery выполняет Root отдельно; изменение существующей SDK/build/runtime/output этим действием не разрешено. Sourceupdate и native48 ждут собственного review/актуальной8repo проверки/контроллер40публикации.
