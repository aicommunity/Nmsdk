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
