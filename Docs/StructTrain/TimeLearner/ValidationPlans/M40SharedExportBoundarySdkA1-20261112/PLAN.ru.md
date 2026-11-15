# SDK shared export boundary: адресная серверная приёмка

Проверяется [исправление summary8](../../RecoverySummaryExportTimeout-20261112.ru.md): SourceRootc73575fe545b00cc7c9bf170c81c185c30b7026a, Pulsedfb9a98244f91b4f4029d8470465fd40116436ca. Изменены export/summary и его Console/finalization callers, не поиск или физика. Исходники доставлены Git-проекциями;6 неизменённых дочерних репозиториев перенесены с принятыми sparse scopes через собственные Git packs, без alternates и без изменения старого SDK. Namespace4160 files/8 repos фиксируется отдельно и должен быть проверен canonical producer.

Используется штатный native acceptance pipeline с новой source/build/runtime/output областью. Старая runtime-recorded-n4-roundtrip-sdk-a3 защищена; resources/framework остаются прежними. До canonical prepare и реальной сборки ничего не считается принятым.

Cohort102 существующих C++ cases: прежние36 native/Console/export guards, плюс recovery package7 и finalization suites. Каждый case запускается отдельной leaf согласно текущей production схеме; source-derived case inventory и фактический JUnit должны совпасть без skips. Recovery fixtures теперь непосредственно вызывают объединённый API, сравнивают summary с standalone, проверяют явную/owned C0 и сохранность live graph/динамики. Finalization fixtures удерживают source summary после import/reset.

Canonical actor/source7bd3684732e1d3f7a0aa038d659fd52bc95892bf подготавливает только DATA; SDK child использует собственные Scripts из SourceRoot. Native build и cases запускаются отдельно по полученному verified controller command. Build Release/O3, parallel2, без изменения научных tolerances/budgets.

Эта проверка не закрывает большой временной gate: после функционального допуска нужна выгрузка реального67-group случая в прежние300s и один конечный повтор scientific job, без автоматического роста времени или recovery budget. Elder-проверка остаётся обязательной; Windows и весь исходный план не объявляются выполненными.
