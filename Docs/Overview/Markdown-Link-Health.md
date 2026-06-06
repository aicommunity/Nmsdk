# Markdown Link Health Report

Отчёт по валидации ссылок во всех Markdown-файлах репозитория `Nmsdk`.

## Методика
- Собраны все `.md` файлы (157 шт., исключены только внешние зависимости `build/_deps/**`).
- Для каждой ссылки формата `[text] (target)` и `![alt] (target)` (пробел разрывает парсинг ссылок в этом описании):
  - Пропущены внешние URL (`http(s)://`, `mailto:`) и чистые якоря `#anchor`.
  - Цель интерпретирована как путь, **относительный к каталогу текущего файла**; проверено существование файла.
  - Для сабрепозиториев оставлены только ссылки внутри их каталога; внешние пути заменены ранее на текстовые указания (в рамках предыдущих работ).

## Результат проверки
- Автоматическая проверка: `Scripts/doc-audit/check-links.py` → [Docs/Audit/Link-Health-Report.md](../Audit/Link-Health-Report.md)
- Последний прогон: см. дату в Link-Health-Report (полное дерево ~650+ `.md`)

## Исправленные проблемы (кратко)
- Обновлены ссылки в `Reports/00-Project-Overview.md`, `Reports/09-Component-System.md`, `Reports/10-Build-System.md` на актуальный `Docs/Libraries/Overview.md`.
- Исправлены пути из `Bin/Docs/README.md` к корневой документации (`Configuration-Files-Overview.md`, `Style-System.md`).
- Нормализованы относительные ссылки в `Rdk/Docs/**` на разделы `Docs/Rdk-Core/**` и `Docs/GUI/**`.
- Уточнены ссылки в `Docs/Development-Guides/Component-Development.md`, `Docs/Troubleshooting/Troubleshooting-Guide.md`, `Rdk/Docs/Diagrams/README.md`.

## Примечания
- Внешние каталоги зависимостей `build/_deps/googletest-src/**` не исправлялись; они исключены из финальной проверки.
- Для поддержки GitHub-навигации в сабрепозиториях активные ссылки оставлены только на локальные файлы; кросс-репозиторные указания даны текстом в обратных кавычках.
