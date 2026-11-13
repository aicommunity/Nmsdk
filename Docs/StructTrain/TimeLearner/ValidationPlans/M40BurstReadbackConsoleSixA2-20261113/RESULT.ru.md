# Отказ внешнего запуска до расчёта модели

Попытка s07-burst-readback-console-six-m40-a2 не создала рабочую contained-группу и не выполняла Console probes. Причина в исходном launch log: loader_environment_changed:QT_QPA_PLATFORM. При подготовке Console runtime manifest значение offscreen было ошибочно унаследовано внешним Python controller; его собственный runtime требует пустого loader environment.

Это ошибка настройки запуска, не результат модели и не отказ нового C++ readback. Сохранены замороженные controls и исходные preflight/launch-context/request/log. Нет worker terminal, run manifests или научного verdict. Для новой попытки A3 окружение внешнего контроллера очищено от трёх loader keys; Console получает своё offscreen штатным applied_loader_environment из неизменного runtime manifest. Ограничения контроллера не ослабляются, SDK не пересобирается.

Producer Git83edf7dfa75ab5e2ce73bde957688de5c5a75626; исходные12 blobs перенесены побайтно.
