# Реальный collector output восстановлен и проверен

s10-source-envelope-produced-data-m40-a1:1/1 passed за4.316s собственно unittest, без failures/errors/skipped. Внешняя группа закрыта, lease released. Code Root434fd67c973548f0b6f787428ca672bc88b233d0, Tool7bd3684732e1d3f7a0aa038d659fd52bc95892bf. Проверялся actual output штатного manifest3 collector, а не тестовая копия writer.

Проверены712 logical members, восстановлены706 regular files и18 исходных job documents. Разница в6 members — документированные glog aliases: их содержимое проверено, сами redundant aliases опущены прежним compatibility adapter. Original manifests не переписаны. После полного восстановления production primary audit прошёл для всех6 Classic/Branch replay/matched/changed outputs.

Полный новый пакет1,082,331 bytes против1,234,243 bytes полного legacy package на том же corpus. Это сравнение всего формата, включая metadata; literal XZ нового формата отдельно занимает680,360 bytes. Экономию большого N4 corpus эти маленькие N=2 данные не доказывают.

Raw proof находится в completed-readback/worker/tmp/source-envelope-produced-proof.json. Форматный fixture и receipts опубликованы producer Git7ac974d81928f10887faba722a915aa6a4c20e44 без повторной сериализации. Native execution attestation/scientific verdict не создаются восстановлением. Большой N4 эксперимент продолжает отдельную исходную попытку.
