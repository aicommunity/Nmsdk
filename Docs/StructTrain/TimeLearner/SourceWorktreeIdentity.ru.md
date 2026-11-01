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
