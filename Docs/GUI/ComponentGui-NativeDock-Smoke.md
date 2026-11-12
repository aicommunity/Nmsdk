# Component GUI — native dock smoke protocol (TD-010)

## RU

Ручной протокол после unit-теста `Test_ComponentGuiDockChrome`.

1. Открыть 2 component forms → Detach (floating dock) → reattach to MDI.
2. Move one form to Tab Host → reorder tabs → close/reopen project → order restored.
3. Move form to Secondary Host → close secondary → reopen from menu.
4. Float dock, close via X, reopen from diagram — single instance.
5. No style loss on float/reattach (title bar, tab strip).
6. Float dock → **рамка ресайза**, кнопки свернуть / **развернуть (активна)** / закрыть. Двойной клик по заголовку **максимизирует**, а не возвращает в док. Re-dock — перетаскиванием к главному окну.

Автоматика: `Tests/Unit/HardwareLib/Test_ComponentGuiDockChrome.cpp` (`installComponentGuiFloatingChrome`).

---

## EN

Manual protocol after the `Test_ComponentGuiDockChrome` unit test.

1. Open 2 component forms → Detach (floating) → reattach to MDI.
2. Move one to Tab Host → reorder tabs → close/reopen project → order restored.
3. Move to Secondary Host → close secondary → reopen.
4. Float dock, close via X, reopen from diagram — single instance.
5. No style loss on float/reattach.
6. Float dock → **resize frame**, minimize / **maximize (enabled)** / close. Title-bar double-click **maximizes** instead of re-docking. Re-dock by dragging to the main window.

Automation: `Tests/Unit/HardwareLib/Test_ComponentGuiDockChrome.cpp` (`installComponentGuiFloatingChrome`).
