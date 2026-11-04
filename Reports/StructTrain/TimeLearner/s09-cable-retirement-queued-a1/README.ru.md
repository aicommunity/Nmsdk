# Ожидает:20 исторических cable/E1 исходников

Feature commit1d5c8276cc9344362ebffccf43a0970d55cc2084 подготовил удаление20 связанных исторических tools с full commit/blob/SHA256 retrieval и оговорками в12 E1 отчётах/двух README. Первичные данные, модели и численные выводы сохранены. Source и metadata доставлены через самостоятельные Git packs без alternates; SDK не создаётся.

На Elder и M40 подтверждены живые worker handles и queue.json, исключений после запуска нет. Они ждут закрытия уже работающих/поставленных ранее native заданий. Перед приёмкой требуется production verify-migration всех141 candidate records на обоих workers и negative tree с восстановленным удалённым файлом. Положительного результата пока нет.

В принятом develop по-прежнему121 migration record; feature удаления не объединён. Pending snapshot уменьшит path-based остаток217 до197 только после приёмки. Общая миграция остаётся неполной. jobs.json и сжатые orchestration сохраняют точную постановку без паролей. Исторические программы не исполняются.
