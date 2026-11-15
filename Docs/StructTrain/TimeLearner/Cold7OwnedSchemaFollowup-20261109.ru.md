# Cold7: отдельный owning-value follow-up

Статус: исходники и test inventory, проверки не исполнены. Baseline A4 (`478cc35c0f1a314c34ad93aa0095b61836c658ec` / Pulse `4a5c2ec9df9a9f704dcd8260714323494bfa4415`) остаётся отдельным неизменным снимком.

Будущий источник сохранён обычными merge `--no-ff`: Pulse `ff787837d1835497a9b022fb64ebf9f34c676b95` переносит baseline cold6 fix в `b2878e565febe20a4ba7c9c64536d6e66f672626`; Root `32a5022f1360894a149a84a937895bf7ae7666f3` переносит baseline ROOT controls в `e11bbd403a5f93790a7ad6c5a245c1964797d63d`. Исторические исходники не переписаны.

Pulse `4b70b0bfb41510691971de86ce5c4993bb382b8b` исправляет отдельную cold7 ветку producer: owning `QJsonValue` числового schema сохраняется до вставки нового ключа в тот же `QJsonObject`. Decoder, строгие типы и все старые ветви остаются прежними. Это устраняет источник proxy/index alias; нет bool/string→number coercion.

Два новых actual model-backed Classic/Branch tests перебирают плоские base schemas1–4, проверяют числовой тип base, равенство всех flat полей после снятия оболочки, production object decode и production parse из Compact JSON bytes. Bool, строковый номер и null по-прежнему обязаны отвергаться обоими путями. Исходные initial actual readback cases дополнительно проверяют numeric base и bytes roundtrip. Actual producer declarations сохраняются под `classic-cold7-envelope/base-{1..4}/producer-wire.json` и `branch-cold7-envelope/base-{1..4}/producer-wire.json` при заданном `TIMELEARNER_COMPOSITE_OUTPUT`.

Schema3/4 здесь означают объявление C0/C-search политики. Тесты не создают фиктивного измеренного C0, waveform, references, live admission или Train5 certificate. Native groups не запускаются для codec controls. Source inventory с точными ID и SHA256 Git bytes — `Cold7OwnedSchemaFollowup-20261109.json`. Полный SDK/native/service/portable gate по будущему источнику остаётся обязательным отдельным непрошедшим условием; этот follow-up не заменяет full248 или candidate-window acceptance.
