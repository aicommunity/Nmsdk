# Component GUI — native dock smoke protocol (TD-010)

## RU

Ручной протокол после lifecycle-тестов `Test_ComponentGuiLifecycle` / `Test_ComponentGuiRegistry`.

1. Открыть 2 component forms → Detach (floating dock) → reattach to MDI.
2. Move one form to Tab Host → reorder tabs → close/reopen project → order restored.
3. Move form to Secondary Host → close secondary → reopen from menu.
4. Float dock, close via X, reopen from diagram — single instance.
5. No style loss on float/reattach (title bar, tab strip).

Автоматика: `NativeDockHostCreateAndClose`, `TabHostSaveStatePersistsTabOrderV2` в `Rdk/Tests/Unit/Test_ComponentGuiLifecycle.cpp`.

---

## EN

Manual protocol after lifecycle unit tests.

1. Open 2 component forms → Detach (floating) → reattach to MDI.
2. Move one to Tab Host → reorder tabs → close/reopen project → order restored.
3. Move to Secondary Host → close secondary → reopen.
4. Float dock, close via X, reopen from diagram — single instance.
5. No style loss on float/reattach.

Automation: `NativeDockHostCreateAndClose`, `TabHostSaveStatePersistsTabOrderV2` in `Rdk/Tests/Unit/Test_ComponentGuiLifecycle.cpp`.
