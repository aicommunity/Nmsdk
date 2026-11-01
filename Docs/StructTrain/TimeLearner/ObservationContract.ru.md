# Контракт наблюдений

Analyzer schema 3 остаётся совместимым форматом старых конфигураций. Новая schema
4 выбирается свойством ObservationSchemaVersion=4, с RunId и ModelRevision из
manifest. Полный список полей и ограничения описаны в PulseLib component docs.

Scorer metrics_version=4 отделяет историческую точность от нового audit verdict.
По умолчанию ожидаются trial IDs 0..7; другой протокол обязан передать точное
expected_trial_ids. Target определяется target_class=1. Дубли sample IDs
запрещены для этого протокола одного прохода по уникальным сэмплам.

Неизвестная/смешанная схема, complete!=1, censored!=0, пропуски IDs, NaN/Inf,
повреждённый список timestamps, несогласованный count либо неполное schema4
окно дают schema_ok=0 и ok_audit=0 с validation_errors. Отсутствующие исторические
поля не достраиваются. Ранний ответ при валидных данных — scientific failure,
а не ошибка схемы. ok_audit_v2 равен ok_audit и включает last-pulse.

Проверки написаны против production scorer и C++ collector. Они не заменяют
native scheduler/end-to-end trial boundary тесты и не доказывают обучение модели.
