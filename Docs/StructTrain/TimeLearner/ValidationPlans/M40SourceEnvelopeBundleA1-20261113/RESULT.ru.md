# Пакетное восстановление: пять проверок пройдены

s10-source-envelope-bundle-data-m40-a1:5/5 passed за9.248s собственно unittest, без failures/errors/skipped. Внешняя группа закрыта, lease released. Code Root5fda947e4d3bac6d4cebcc33a6e7a41aa372c5e3; frozen controls и исходные receipts сохранены рядом. Producer Git848aa5253dc865c65b24b2023249a520cc667791.

На фактических файлах шести закрытых A4 прогонов проверены полный source-envelope pack/restore,12 job recipes, весь восстановленный namespace и production primary audit каждого из шести native outputs. Отдельно проверены повреждённый recipe до создания restore output, literal fallback, запрет циклических ссылок, manifest3 roles и сохранение legacy manifest1. Fixture fingerprints охватывают216 JSON и298 CSV; новые native расчёты не выполнялись.

Это проверка библиотечного пути и форматов. Следующая отдельная [production collector/restore проверка](../M40SourceEnvelopeProducedA1-20261113/RESULT.ru.md) подтверждает штатный owned writer. N4 large-file roundtrip и внешнее Git source reuse этим набором не подтверждаются.
