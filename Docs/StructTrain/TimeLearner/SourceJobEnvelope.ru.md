# Побайтное восстановление job вокруг сохранённого source package

Статус: codec source_job_envelope подготовлен, серверная приёмка ещё не выполнена. Работающий N4 эксперимент, его source/runtime и файлы не меняются. Это подготовка компактной публикации, не изменение способа расчёта.

В stopped probe один и тот же большой source_stopped включён в исходный job, input/job.json и native/job.json. Сохранение всех этих копий как независимых XZ members избыточно. Сам source package уже должен быть сохранён в Git как необходимый первичный материал; ссылка на абсолютный путь M40 его не заменяет.

Codec сохраняет оригинальные prefix/suffix bytes и тип известного вложенного представления source_stopped. Поддержаны production Python indent2 и Qt indent4. Python-вариант воспроизводит существующий json.dumps с ensure_ascii=False/indent2/allow_nan=False; Qt-вариант добавляет ровно один уровень отступа к исходному Qt document. Применение разрешено только при полном побайтном совпадении вычисленного payload с оригинальным span. Неизвестный layout остаётся literal, без попытки нормализовать или исправить данные.

Recipe хранит размер/SHA256 reference document и оригинального job, codec version и base64 prefix/suffix. Restore проверяет reference bytes, допустимый schema/codec и бюджеты, затем восстанавливает весь исходный файл и сверяет его размер/SHA256. Вывод в новый файл разрешён только после успеха. Recipe не содержит исполняемых команд или путей.

Исходные jobs, run manifests, native execution records и их hashes не переписываются. Перед production audit восстанавливаются исходные bytes; аудитор не читает recipe вместо настоящего job. Любая экономия размера считается доказанной только после actual-file roundtrip. Сам codec не подтверждает валидность JSON, native execution, обучение, принадлежность пика или классификацию.

Для публикации N4 дополнительно нужны закреплённый Git archive/member с reference source document, recipe index, проверка полного восстановленного namespace и повторный production audit на восстановленном corpus. Эти шаги ещё не реализованы/приняты данным codec и не должны считаться завершёнными по его узким тестам.
