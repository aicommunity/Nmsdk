# Fresh validated export SDK36 — M40, canonical A2

Исходный [план36](../M40ValidatedExport36A1-20261112/README.ru.md), root08b898b1ad89d002cccde534e08e0925e080e45d/Pulsee9b80746103750d3b5a100d74549462d6d2c46c6. [Причина отказа A1 до сборки](../M40ValidatedExport36A1-20261112/PREPARATION-FAILURE.ru.md). Восстановлены восемь кириллических tracked paths через UTF-8 stdin Git sparse checkout; все4145 file bytes/hashes совпадают. Source commits, cohort36, artifact rules170, targets/flags/limits/protected runtime не меняются.

A2 создаёт отдельную canonical preparation; Native build/controller ещё не запускался, поэтому его свежие build/runtime/output пути A1 сохранены. Подготовка и native приёмка — разные gates. Любая ошибка сохраняется, ожидаемый source namespace не уменьшается. До фактической свежей сборки36/36 и независимой приёмки кандидат не принят; большой N4 export и Elder остаются обязательными последующими gates.
