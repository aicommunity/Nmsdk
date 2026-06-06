# Markdown Link Health Report

## RU

Отчёт по валидации ссылок во всех Markdown-файлах репозитория `Nmsdk`.

## Методика
- Собраны все `.md` файлы репозитория (~800+, см. [Documentation-Inventory.json](../Audit/Documentation-Inventory.json)); исключены `build/_deps/**`.
- Для каждой ссылки формата `[text] (target)` и `![alt] (target)` (пробел разрывает парсинг ссылок в этом описании):
  - Пропущены внешние URL (`http(s)://`, `mailto:`) и чистые якоря `#anchor`.
  - Цель интерпретирована как путь, **относительный к каталогу текущего файла**; проверено существование файла.
  - Для сабрепозиториев оставлены только ссылки внутри их каталога; внешние пути заменены ранее на текстовые указания (в рамках предыдущих работ).

## Результат проверки
- Автоматическая проверка: `Scripts/doc-audit/run-all.sh` → [Link-Health-Report.md](../Audit/Link-Health-Report.md)
- CI: `Scripts/ci-doc-audit.sh` (критические корневые ссылки + полный прогон отчётов)
- Целевое значение: **0** битых относительных ссылок в Link-Health-Report

## Исправленные проблемы (кратко)
- Обновлены ссылки в `Reports/00-Project-Overview.md`, `Reports/09-Component-System.md`, `Reports/10-Build-System.md` на актуальный `Docs/Libraries/Overview.md`.
- Исправлены пути из `Bin/Docs/README.md` к корневой документации (`Configuration-Files-Overview.md`, `Style-System.md`).
- Нормализованы относительные ссылки в `Rdk/Docs/**` на разделы `Docs/Rdk-Core/**` и `Docs/GUI/**`.
- Уточнены ссылки в `Docs/Development-Guides/Component-Development.md`, `Docs/Troubleshooting/Troubleshooting-Guide.md`, `Rdk/Docs/Diagrams/README.md`.

## Примечания
- Внешние каталоги зависимостей `build/_deps/googletest-src/**` не исправлялись; они исключены из финальной проверки.
- Для поддержки GitHub-навигации в сабрепозиториях активные ссылки оставлены только на локальные файлы; кросс-репозиторные указания даны текстом в обратных кавычках.

---

## EN

Link validation report for all Markdown files in the `Nmsdk` repository.

## Methodology
- Collected all `.md` files in the repository (~800+, see [Documentation-Inventory.json](../Audit/Documentation-Inventory.json)); excluded `build/_deps/**`.
- For each link of the form `[text] (target)` and `![alt] (target)` (space breaks link parsing in this description):
  - Skipped external URLs (`http(s)://`, `mailto:`) and pure anchors `#anchor`.
  - Target interpreted as a path **relative to the current file's directory**; file existence checked.
  - For subrepos, only in-repo links kept; external paths were replaced with text references earlier.

## Check result
- Automated check: `Scripts/doc-audit/run-all.sh` → [Link-Health-Report.md](../Audit/Link-Health-Report.md)
- CI: `Scripts/ci-doc-audit.sh` (critical root links + full report run)
- Target: **0** broken relative links in Link-Health-Report

## Fixed issues (brief)
- Updated links in `Reports/00-Project-Overview.md`, `Reports/09-Component-System.md`, `Reports/10-Build-System.md` to current `Docs/Libraries/Overview.md`.
- Fixed paths from `Bin/Docs/README.md` to root documentation (`Configuration-Files-Overview.md`, `Style-System.md`).
- Normalized relative links in `Rdk/Docs/**` to `Docs/Rdk-Core/**` and `Docs/GUI/**`.
- Clarified links in `Docs/Development-Guides/Component-Development.md`, `Docs/Troubleshooting/Troubleshooting-Guide.md`, `Rdk/Docs/Diagrams/README.md`.

## Notes
- External dependency trees `build/_deps/googletest-src/**` were not fixed; excluded from the final check.
- For GitHub navigation in subrepos, active links are kept only to local files; cross-repo references are given as text in backticks.
