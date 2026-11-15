# Адресные проверки idle readback: 13/13

Задание s07-idle-probe-readback-tests-elder-a1 на Elder проверило Root49689590cbdc0bbe5abccfb91374ad716f0ff977: восемь декларативных контрактов полного burst readback и пять DATA проверок idle summary. Все 13 прошли, без skipped/errors/failures. Группа закрыта и lease released; исходные записи находятся в completed-readback, замороженные условия — в controls.

Проверены отказы при изменении истории, source binding, конфигурации, протокола, delivery log, references, counters, epoch, search и certificate. Неполный capture не может породить отсутствующие references. Это проверки формата и сверки данных: реальные Console probes, обучение, принадлежность пиков и распознавание ими не подтверждаются.

Producer Git: 9419d252838efc334229747eca82a19d72e0fad0; integrity.json содержит размеры и SHA256 исходных файлов. JSON с наносекундными величинами переносится как исходные Git blobs без повторной сериализации.
