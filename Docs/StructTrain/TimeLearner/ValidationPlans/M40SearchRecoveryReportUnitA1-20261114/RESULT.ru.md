# Одиннадцать проверок search-report приняты

M40:11/11, без failures/errors/skips, source6734dec146063f5f2553fd44871e4256470f0a4b. Unit runtime 0.038s; outer completed/closed20.425687498878688s, heartbeat errors0. Это wire/projection и CLI boundary checks; реальный Branch primary проверяется отдельным заданием, поэтому эти11 PASS не заменяют full-DATA replay и не являются сходимостью обучения.

Новые4 controls проверяют absent=null, empty!=complete, сохранение всех5 различающихся event/runtime deliveries и budget stop без добавления measured candidates; malformed/rehashed invalid counters/dimensions/NaN/duplicates отвергаются. Старые7 controls также пройдены.

[Исходный test log](completed/worker/validation/unittest.log), [result с exact IDs](completed/worker/validation/result.json), [whole group closure](completed/process/whole-group-closure.json), [raw byte integrity](integrity.json). Producer9083e2ec1f2f3331cd7e070fc9e951a5948632a1, pack75717B SHA25699a42f9930571f484693e30ed8dfca31e3d0854b2376450cc2b7a08351a56c46;17 исходных файлов скопированы побайтово без JSON rewrite. Полный этап3/7/9 остаётся частичным.
