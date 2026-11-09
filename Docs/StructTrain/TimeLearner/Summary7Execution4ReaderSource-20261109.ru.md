# Readers summary7/execution4: исходная интеграция

Реализована явная пара summary7/package6 и execution4/cold7. Общие проверки
полей предыдущих форматов переиспользованы без изменения исходных документов:
summary6 остаётся отдельным wrapper, execution3 допускает только package5.
Новые версии не проецируются в старые measurement packets или certificates.

Package6 проверяет переданный summary7 как дополнительное утверждение: модель,
epoch, original references, финальные группы, counters, certificate3 и поисковую
историю. Отсутствующий summary не синтезируется. Execution4 проверяет точные
filesystem primary, sidecars, index, package digest и original job/initial model
через существующий production pipeline. До захвата source счётчики остаются
unknown; preflight имеет известные нули. Receipt DATA-проверки не аттестует
процесс или историческое завершение после согласованной подмены всех данных.

В прежние train/preflight/live и source snapshot/recognition paths добавлена
явная поддержка новых версий. Сохраняется привязка original execution к exact
exported package digest и неизменённым артефактам. Нативный runner и проверка
его runtime/закрытия остаются отдельным обязательным слоем.

Добавлены шесть server-only metadata controls execution4 и два reader cases
на обязательном будущем реальном C++ package6/summary7 corpus. Отдельно
требуются прежние package5 regressions, исправленный runtime2 cursor case,
полный Console Train/export/evaluate и frozen model checks. Ни эти тесты,
ни численные CSV replay локально не запускались. Это source preparation,
не приёмка форматов и не научный результат.
