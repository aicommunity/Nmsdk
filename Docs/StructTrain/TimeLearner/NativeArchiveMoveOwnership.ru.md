# Передача владения архивом: проверка кандидата

10.11.2026 подготовлена отдельная SDK-версия
`355c60df066bdc8da09bd6d7872b47f6e71c0494`, PulseLib
`165d49da7e65cd6ac59bca2812ce52884ddd50c2`, Rdk
`de4134235c0dcb8b91fd9a43b267348ad1a163ca`.

В декодированном архиве явно объявленный copy constructor подавлял implicit
move. В результате передача через `std::move` копировала первичные трассы.
Добавлены defaulted move constructor/assignment и copy assignment. Проверки
архива, формат данных и математическая постановка не меняются. Отдельная
копия записей в retained legacy proof сохраняется намеренно: её нельзя
уничтожать без проверки потребителей этого proof.

Новый integration case
`NativeArchiveOwnership/MoveRetainsDecodedPrimaryStorageAndCopyIsIndependent`
декодирует реальный сохранённый package6. Проверяет передачу backing storage
записей и вложенных samples, независимость явной копии и сохранность
document/protocol/reference groups/current attempt. Это проверка production
decoder и типа архива, а не копии их реализации в тесте.

## Объявленная серверная проверка

[Спецификации](ValidationPlans/NativeArchiveMove18-20261110/cohort.json)
зафиксированы в root `601ac11df7e0ccf2122175e0ba5094ee5b093dbc` до запуска.
Включены новый case и все17 случаев предыдущего repair17. Пять package cases
разделены на отдельные процессы/JUnit. Лимиты каждой leaf-группы остаются
4GiB/128 tasks; ASan `detect_leaks=0`, те же build flags и fixtures.

Штатная canonical preparation прошла на M40:4074 source files,29 SDK modules,
18 cases/10 leaf groups; completed/return0, group closed, diagnostics clear.
Она не выполняла C++ tests и не доказывает корректность исправления.

Запущена свежая сборка и последующий gate:
`/media/user/Data/TimeLearnerRefactor/readbacks/s05-native-archive-move18-m40-a1`.
[Наблюдение запуска](ValidationPlans/NativeArchiveMove18-20261110/launch-observation.json)
содержит supervisor identity и привязку к группе процессов. Это промежуточное
наблюдение, не итоговая приёмка. Исходники и runtime предыдущих заданий
не изменялись; контрольный C0 на SDKff42 продолжал работать параллельно.

## Что остаётся доказать

Нужны фактические JUnit18, закрытие групп, сравнение C0 peak memory и результата
при прежнем лимите, публикация полных компактных primary и проверка переноса
на Elder. Если C0 снова завершится OOM, изменение не объявляется достаточным:
следует исследовать другие копии decoder/replay, сохраняя проверки данных.

Даже PASS18 не закрывает полный package regression, Console Train→Test,
матрицу режимов/физики и этапы0–12. Научная классификация этим gate не
оценивается. До соответствующей приёмки ветки не объединяются в develop.
