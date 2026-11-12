# Native DATA A1: registry admission отказ до native

Tool3314a3a782be960ec46b858ad04918301872f100; bound worker PID3880737 завершился с reservation_requires_directory_tree. Outer closed, children=[], reservation-final=[] (lease не был получен), preservation errors=[]; оба native model cases не запускались. Raw10 files сохранены в failed-directory-admission с SHA256.

Я неверно передал file paths в directory-tree registry. Metadata17 проверяли схему и scope, но не вызывали фактический reservation admission. Исправление552222359 резервирует canonical parent dirs для control/manifest/DATA, отдельно проверяя file identity/bytes; тот же production _resources валидирует scopes до запуска worker. Новый тест18 использует штатный API и воспроизводит отказ file lease. A1 сохраняет failure; SDK36 остаётся принятым, его runtime не изменялся. Новый DATA A2 требует отдельного source/Tool/job ID и повторной проверки18.
