# comp_gui Dock-Native Smoke Checklist

Цель: быстро проверить, что migration на нативный `QDockWidget` работает стабильно в интерактивной Linux-сессии.

Ожидаемое время: 3-5 минут.

## Preconditions

- Собран актуальный `NeuroModeler`.
- Открыт реальный проект с компонентами, у которых есть GUI-формы.
- Запуск в обычной desktop-сессии (не offscreen/headless).

## Scenario 1: Open -> Docked

1. Открой GUI компонента из DrawEngine (или другой entrypoint).
2. Убедись, что форма открылась как dock-панель в главном окне.
3. Повтори открытие того же компонента.

Ожидание:
- создаётся/активируется один и тот же экземпляр (single-instance),
- нет дубликатов панели.

## Scenario 2: Dock -> Floating -> Dock

1. Отцепи панель за нативный заголовок dock (float).
2. Перемести floating panel и пристыкуй обратно в main window.
3. Повтори float/dock ещё раз.

Ожидание:
- float/reattach выполняется штатно мышью,
- оформление формы не деградирует (без "чёрного" окна, без потери QSS).

## Scenario 3: Dock -> Tab Host -> Dock

1. Для открытой component GUI выбери `Move to Tab Host...`.
2. Помести форму в существующий tab-host.
3. Верни форму обратно в dock-host (через host menu / attach action).

Ожидание:
- форма появляется в tab-host как вкладка,
- после возврата в dock source-tab очищается,
- нет дублирования одного context в двух host-ах одновременно.

## Scenario 4: Dock -> Secondary Host -> Dock

1. Открой `Window -> Component GUI Secondary Host...`.
2. Для открытой component GUI выбери `Move to Secondary Host`.
3. Верни форму обратно в main dock-host.

Ожидание:
- secondary host открывается как single-instance окно,
- GUI пристыковывается в secondary host,
- возврат в main host работает без потери состояния.

## Scenario 5: Save/Load restore

1. Открой 2-3 component GUI, часть оставь docked, одну сделай floating.
2. Одну размести в tab-host и одну в secondary host.
2. Сохрани проект, закрой и открой снова.

Ожидание:
- панели восстанавливаются с корректным host mode,
- floating-состояние/позиция восстанавливается ожидаемо,
- состояние tab-host и secondary host восстанавливается корректно.

## Scenario 6: Negative checks

1. Попробуй выполнить attach/detach повторно для уже attached/detached панели.
2. Открой GUI для незарегистрированного класса (если доступно в текущем проекте).

Ожидание:
- повторные операции идемпотентны (без падений/порчи layout),
- для незарегистрированного класса — корректный fallback без crash.

## Log capture (если есть проблемы)

При сбое приложи:
- шаг сценария,
- ожидаемое поведение,
- фактическое поведение,
- последние строки с `[ComponentGuiDnD]` из вывода приложения.

