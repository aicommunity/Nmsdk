# Передача пути для composite primary в native child

Native gate назначает каждому запуску собственный путь
`<gate-output>/native-composite` через `TIMELEARNER_COMPOSITE_OUTPUT`.
Linux contained runner передаёт именно этот дополнительный ключ в записанный
request дочернего процесса. Windows использует ту же scoped environment
native gate через штатный Windows backend. Путь legacy execution output
`<gate-output>/native` и его назначение не меняются.

Причина: объявление переменной в наружном worker не передавало её systemd
child, поскольку contained runner имел явный whitelist. C++ assertions могли
выполняться без сохранения новых primary. Теперь путь принадлежит конкретному
gate, внешний caller не выбирает его через наследуемую переменную. Остальные
переменные окружения этим изменением не разрешаются.

Схемы gate 1–4 и математические критерии не меняются. Наличие пути и успешный
JUnit сами по себе не доказывают наличие или достоверность экспортов: worker
обязан проверить фактические файлы, схемы, hashes, completeness и closed
process state, а независимый reader — пересчитать записи по primary.

Для текущего archive206 набора 23 `NativeCompositeArchive` cases запускаются
одним leaf/process: production fixture cache создаёт шесть канонических
экспортов один раз. Разделение этих cases на процессы с общим каталогом
не является эквивалентным запуском и приводит к повторной записи NewOnly.
Остальные leaf имеют отдельные output paths. Проверка шести реальных
экспортов и их независимый replay остаются обязательной адресной приёмкой.
