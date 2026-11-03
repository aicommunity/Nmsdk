# Уточнение канонического lifecycle Rdk, 03.11.2026

Подэтап документации исходных этапов4/12; не новая численная приёмка и не
завершение этих этапов. Rdk feature `da3025b2eaf298e9cf3940731041d9254a88b79b`,
merge develop `33bdf2d19bb915d3fe4c8a917b84bdfe28bf6580`.

Исправлены подтверждённые исходниками неточности: прямые AReset/ACalculate
детей на диаграммах, смешение Ready/InitFlag и линейное представление
Default/Build/Init/Reset. Новый канонический
[NativeLifecycle](../../../Rdk/Docs/Engine/NativeLifecycle.md) описывает guards,
Init → Reset → Build, AfterBuild → Reset, пропуск Calculate без InitFlag,
различие UModule/UContainer и структурное владение после Load.
Обзорные документы и diagram navigator ссылаются на этот контракт.

Проверки: все изменения Rdk находятся в пяти Docs-файлах, локальные ссылки
новых/заменённых документов разрешаются, fenced blocks сбалансированы,
git diff --check проходит. Core tree `b204ef8da698476898394aa1d5b6a2679e5a91ed`
и Deploy tree `acd5bb9c16beceb79b70a5a3330a22b65cc193ac` совпадают с принятым
Rdk `a62393f7791cc4ad10d1c2c11f255b3db3334f89`. Код, scheduler и runtime не
менялись. Поэтому новые численные/ASan прогоны этому docs-only изменению
не приписываются. Работающие серверные jobs сохраняют собственные gitlinks.

Root closure сохраняет Pulse develop5a525657 и Bin develop39d811e5, меняя только
Rdk на указанный docs merge. Automatic C₀ owner и bounded C search остаются
отдельными ещё не принятыми feature-ветками. Полностью завершён только этап0;
полная lifecycle/storage/physics матрица и общая реализация плана остаются открыты.

## Дополнение: связи и присваивания также входят в lifecycle

Rdk merge `acc3de8d1af2480d61ddb723c3288f7e81003049` дополняет тот же канонический
документ. Источниками проверены UItem.Connect/DisconnectAll и
UConnector.ConnectToItem: операции связей вызывают Build. В частности,
LoadComponent(links=true) → SetComponentInternalLinks → BreakLinks →
DisconnectAll может запустить структурный owner до возврата из Load.

Diagnostic proof `38cf86675497e9d7ca441467b51393fc03f1baff` (99 members,
106 654 bytes, все hashes проверены) фиксирует первую потерю custom channel
class и retained C уже в after_load, до явных frequency/Build/Init/adoption.
Его четыре FAIL являются диагностикой setup, а не итогом проверки dormant
export или научного обучения. Исправленный setup ещё принимается в отдельной
ветке; документация не выдаёт ему PASS.

Уточнена также семантика UProperty.h: равное локальное SetData при включённом
CheckEqualsFlag не вызывает setter; connected input не принимает такое
присваивание, ExternalDataSource перенаправляет его источнику. Это объясняет,
почему self-assignment не является штатной командой rebuild. Для факторов
эксперимента и структурной настройки требуется effective readback.

Этот дополнительный diff Rdk затрагивает только NativeLifecycle.md. Core/Deploy
SHA выше неизменны, новые численные/ASan результаты ему не приписываются.
