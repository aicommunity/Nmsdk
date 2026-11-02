Адресный inventory опубликованных references теперь доступен в
[SourceReferenceAudit](SourceReferenceAudit.ru.md): два byte-identical server
повтора,25 report folders, из них22 требуют dependency review. Этот inventory
не является retroactive source attestation или переоценкой научных результатов.

# Проверка принадлежности исходников рабочей копии Git

01.11.2026 при серверной проверке migration manifest обнаружен Bin alias:
`source-n1-measured-refinement-normal-a1/Bin` на Elder использует gitdir
`source/.git/modules/Bin/worktrees/Bin1`, в котором core.worktree указывает
на `source-order-fixed-a1/Bin`. HEAD и status первого пути выглядели корректными,
но Git проверял содержимое другой рабочей копии. Проверка migration.py
корректно завершилась `migration_repository_alias_mismatch:Bin`.

Это дефект проверки provenance, а не доказательство повреждения численного
результата. Прежние receipts не переписываются и не объявляются автоматически
проверкой фактического Bin дерева. Для затронутых запусков требуется отдельная
сверка использованных ресурсов с точными Git blobs. Изменять metadata старых
рабочих копий и запускать заново живые задания этим исправлением не требуется.

`runtime.source_closure` теперь перед чтением HEAD/status проверяет равенство
resolved requested directory и `git rev-parse --show-toplevel` для корня и
каждого gitlink. Несоответствие запрещает создание runtime manifest.
Формат успешного manifest и content fingerprint не меняются. Проверка не
обеспечивает lifetime immutability, а untracked files по-прежнему не являются
частью проверяемого Git closure.

Три теста используют настоящие временные Git repositories: корректный child;
child с совпадающими HEAD/status, но другим core.worktree и другим локальным
физическим файлом; аналогичный alias корня. Они вызывают production
`source_closure`, без копирования реализации. На обоих workers все три теста
пройдены; исходная реализация 76afaeb пропускает оба alias и проваливает два
отрицательных теста. Первоначальный root fixture не имел дочернего alias и
вызывал incidental Git error; исходные логи сохранены, fixture дополнен.
Доказательства: root commits 43f427f1d8c032e85f45ba1daf86368c39f98054 (Elder)
и e8edd5ca73275bf9fbfe44244cc1748e2938d7e7 (M40). Это Python/Git проверки,
а не численные ASan испытания модели. Этапы 2/10 целиком не закрыты.

## Адресное исправление Elder Bin после диагностики

Полная сверка запрошенного Bin с tracked blobs6304b4a обнаружила отсутствие
всех tracked files; в каталоге находились `.git` и untracked RTlibs.
Это подтверждает недостаточность прежнего чистого HEAD/status. Отчёт
`s02-elder-bin-worktree-repair-a1` сохранён commit
de0f1ad60f7dd0c0637d931af8f7842c87d2d437, включая полный список missing paths.
Резервные копии Git metadata остаются в одноимённом readbacks каталоге Elder.

После проверки отсутствия процессов, использующих source, использовано уже
включённое `extensions.worktreeConfig=true`: только в config.worktree Bin1
записан правильный `core.worktree`. Общий config не менялся; HEAD/status/
toplevel соседней `source-order-fixed-a1/Bin` до и после совпали. Через штатный
`git restore --source=6304b4a --worktree -- .` восстановлены отсутствовавшие
tracked files; untracked RTlibs не удалялись. Новый `source_closure` успешно
проверил корень и все дочерние рабочие копии. На M40 соответствующая сверка
toplevel всех gitlinks прошла без исправлений.

Это проверка текущего состояния. Она не делает прежние Bin manifests
ретроспективно достоверными. Для предыдущих запусков через этот Elder source
нужны явная маркировка ограничения и адресная сверка зависимостей; отсутствие
Bin само по себе не опровергает вычисления с compiled storage profiles и
inline jobs, но недоступные ресурсы нельзя считать проверенными. В частности,
старый measured-length gate39+28 сохранён с invalid Bin provenance; повторный
gate67 на том же frozen runtime после исправления выполняется отдельно.
