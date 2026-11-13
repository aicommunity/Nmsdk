# A1: сохранён отказ неполного metadata-fixture

Production CLI вернул mapped_revision_not_available; тест FAILED (0.306s), outer process_error/closed19.242820738s. Исходные356 packets были incremental относительно прежнего metadata namespace, в новом namespace не содержали всех archive commits. Ни verification PASS, ни запуск старых scripts/моделей не получены.

[Original test log](failed/worker/validation/unittest.log), [controller result](failed/controller-result.json). Source5761e16c92fc35580820dce49ad6eafa0c4ab1fc, control3d9f26f2e67817a44ebfae97268ba8795cf0c2b6. Producer e87e47644588db5d45fed37fcb08a440e0c91738; pack188637B SHA25628f6bb869590b2abdd38e6df5882d01e6bfbf4bff3b882dde2685bd4d6cc8b63.

[A2](../M40Migration357A2-20261114/RESULT.ru.md) исправляет только состав fixture, сохраняя этот отказ.
