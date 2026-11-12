# Явные DATA inputs native gate

Кандидат: native gate schema5 сохраняет contained Linux execution schema3 и
добавляет обязательный непустой `data_inputs`. Schema4 остаётся контрактом
Windows, схемы1–4 и их result schema1 не изменяются. Runtime-приёмка кандидата
ещё не выполнена.

Каждый вход задаёт `name`, абсолютный `path`, точные `bytes` и `sha256`.
Имя — один ASCII filename; повторы/aliases, traversal, reserved descriptor,
bool вместо размера и неизвестные поля запрещены. Не более8 файлов,64MiB
на файл и128MiB всего. Внешний owned controller должен держать read reservation
на source fixture и фиксировать его before/after snapshot.

До запуска весь набор захватывается существующим production
`capture_required_file_roles`: canonical regular files, bounded read и
проверенные bytes/SHA. Frozen bytes размещаются ровно в
`<gate output>/native-inputs/<name>` штатным staging-механизмом с отдельным
descriptor. `TIMELEARNER_EXECUTION_OUTPUT` по-прежнему задаётся runner и
указывает `<gate output>/native`; native consumer читает соседний
`../native-inputs/`. Новых скрытых environment overrides нет.

После native execution заново проверяются источники, staged bytes, descriptor
и полное множество staged entries. Изменение делает итог невалидным даже
при прошедших GTest assertions. Result schema2 добавляет отдельный DATA audit;
он не является native execution или scientific certificate. Kernel closure,
actual mappings/JUnit и source/runtime guards остаются обязательными.

Приёмка:8 адресных IO/schema/mutation controls, прежние8 native-gate reader
controls на реальном11-case JUnit; далее actual native consumer двух больших
N4 моделей. Сжатые derived модели остаются кэшем M40, исходные self-contained
primary уже сохранены в Git. Этот документ не закрывает весь этап10.
