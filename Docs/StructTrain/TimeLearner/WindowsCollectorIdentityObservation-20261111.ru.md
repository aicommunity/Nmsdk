# Windows: открытое наблюдение file identity

Во время подготовки control fixture production validation.fixture_fingerprint отказала collector_file_changed_during_read. Повторное сравнение для declaration.json показало одинаковые dev/ino/size/mtime_ns, но разные lstat.st_ctime_ns и fstat.st_ctime_ns; runtime.json при этом совпал. [Точные metadata](ValidationPlans/M40RecoveryConsoleCold8A1-20261111/windows-file-identity-observation.json) сохранены без округления ns. Это наблюдение на локальной Windows/Python, не тест learner и не доказательство причины внутри ОС.

Не менять сравнение на Linux и не игнорировать ошибку в runtime evidence. Для текущей Linux-job ожидаемый fingerprint формируется production _digest из hashes Git-bound объявленных bytes; реальные файлы проверяются Linux preflight/frozen_digest до и после suite. Это не утверждает Windows collector portability.

До использования такого collector на Windows: воспроизвести на .14 с фактической версией Python и обычным изменением файла после создания; определить единый OS-specific способ сравнения handle/path identity и change time; сохранить проверки подмены inode/размера/mtime, symlink/junction и изменения во время чтения. Исправление требует адресных Windows и Linux проверок и отдельного commit. Текущая scope-приёмка Windows build не закрывает этот пункт.
