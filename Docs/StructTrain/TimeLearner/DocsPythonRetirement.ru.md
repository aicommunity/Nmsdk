# Исторические Python-инструменты SoftCold/W1/W2

Подэтап этапа9. Четыре разовых инструмента удаляются из Docs без wrappers
или копий на прежних местах. Их исходники доступны в Git по снимку
`ce285d7eee907d7d453ae00e1840246df09d5086`. Это commit для извлечения
скрипта, а не утверждение о версии конкретного научного эксперимента.

| Прежний файл | Назначение и причина удаления | Исторический исходник |
|---|---|---|
| `metrics/monitor_softcold_autosave.py` | SoftCold monitor читает старые autosave/Parameters_00 и campaign workdirs; современный runner использует owned-process/runtime manifests. | [commit/blob](https://github.com/aicommunity/Nmsdk/blob/ce285d7eee907d7d453ae00e1840246df09d5086/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/monitor_softcold_autosave.py) |
| `metrics/refresh_fail_taxonomy_after_fix.py` | Разовый генератор FAIL_TAXONOMY исполняет работу при import; старый softcold_full_49 plan прямо помечает snapshot устаревшим. Старую taxonomy не пересчитываем. | [commit/blob](https://github.com/aicommunity/Nmsdk/blob/ce285d7eee907d7d453ae00e1840246df09d5086/Docs/Audit/TimeLearner-2026-09-26-review/evidence/metrics/refresh_fail_taxonomy_after_fix.py) |
| `tools/w1_order_ctrl_run.py` | W1 launcher содержит фиксированные каталоги результатов24 октября, старую Console и параллельный запуск jobs при import. | [commit/blob](https://github.com/aicommunity/Nmsdk/blob/ce285d7eee907d7d453ae00e1840246df09d5086/Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools/w1_order_ctrl_run.py) |
| `tools/w1w2_sim_template.py` | W1/W2 генератор временного масштабирования зависит от старых profiles/неполного масштабирования; научное расширение физики отдельно от исправления текущего алгоритма. | [commit/blob](https://github.com/aicommunity/Nmsdk/blob/ce285d7eee907d7d453ae00e1840246df09d5086/Docs/Audit/TimeLearner-2026-09-26-review/evidence/tools/w1w2_sim_template.py) |

`script_migration.json` содержит для каждого файла полный commit SHA, blob SHA-1,
SHA256, размер, последний изменявший commit и команду `git show`. Историческая
Markdown-ссылка на удалённый taxonomy generator заменена ссылкой на точный
Git snapshot. Упоминания в старых отчётах остаются историческими свидетельствами.
Ни один исходный отчёт, модель или trial data этим изменением не пересчитаны.

В текущих tracked Python/shell/PowerShell/batch trees корня, Bin и PulseLib
ссылок на четыре модуля не обнаружено. Это проверка текстовых зависимостей,
не доказательство отсутствия произвольного внешнего/dynamic consumer.
Старый e05 runner, c1 tools, cable/fast models и остальные активные/исторические
скрипты требуют отдельных решений; весь этап9 не закрыт.

Проверка должна использовать production `history verify-migration`/
`migration.verify_migration` на обоих workers: все48 записей, включая прежние
44, проверяются по Git trees, точным blob/content hash и отсутствию old paths.
Отдельный Git fixture возвращает один удалённый файл в новое дерево;
положительная квитанция для него запрещена. Проверки завершены на обоих workers; это metadata-only проверка, не ASan/numerical acceptance.

Elder proof `3c631ed1ab1616aa12e004a83151e83c933f9357`, M40 proof
`841790f474d1cc22c2acadcf51cf5f3b6255b09a`: по48 verified records и
одному отклонённому restored-path fixture. Все9 members каждого metadata
archive и bundle hashes проверены локально; архивы7572/7580 bytes. Точные
исходники численных заданий остались прежними: source-context before/after
совпали. Скрипты истории не исполнялись; current root tree не хранит wrappers.
Архивные snapshots не являются closure экспериментальных результатов.
