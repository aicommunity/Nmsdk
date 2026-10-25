# Этап 3: наблюдения и оценка

В PulseLib реализована явно выбираемая observation schema 4, сохраняющая schema 3
по умолчанию для старых конфигураций. Коллектор сохраняет произвольное число soma
peaks, обнаруживает nonfinite, изменение размерности и overflow. Scorer использует
метки target/foil, проверяет полноту, IDs, timestamps, schema/context и имеет один
audit verdict с last-pulse. Историческая точность остаётся отдельным значением.

На M40 выполнены 90/90 Python tests и четыре C++ collector tests, затем полный
PulseLib CTest. На Elder-1 дополнительно проверены пять C++ collector cases,
включая запись реального schema4 CSV с quoted RunId и пятью amplitudes, и чтение
этого файла production Python scorer: n=8, metrics_version=4, schema_ok=1.
Это синтетический unit fixture; он не включается в научный реестр PASS.

Артефакты опубликованы через Git в ветках evidence/timelearner-s02-m40 и
evidence/timelearner-s03-s04-elder1. Они будут собраны в develop вместе с
принятыми подэтапами. Исходные manifests сохраняют фактические tested commits,
а не подменяются последующими merge SHA.

Здесь не заявляется завершение нового controller, native export/import или
обучение. Доказательность конечной модели, полный scheduler boundary audit и
pipeline протоколов относятся к следующим этапам. Старые scripts ещё ожидают
миграции по отдельному этапу; новых wrappers на старых местах не добавлено.
