# Elder A1: canonical принят, native launch не выполнен

Canonical completed/exit0/70.09837876958773s, whole group closed, diagnostics clear; независимо проверены4160 files,30 imported SDK modules,102 selected cases. [Исходные подтверждения](canonical-readback/readback-integrity.json).

Native launcher завершился отказом owned_native_capacity_preflight: disk reservation12GiB+physical floor2GiB превышали свободное место. До создания native controller и lease; launcher PID отсутствует при readback, native job не стартовал. [Исходный traceback и состояние](failed-launch-readback/readback-integrity.json). Это не ошибка C++ или обучения. Следующий [A2](../ElderSharedExportBoundarySdkA2-20261112/PLAN.ru.md) имеет отдельную identity и уточнённый по измеренному SDK disk reserve; исходный отказ сохранён.
