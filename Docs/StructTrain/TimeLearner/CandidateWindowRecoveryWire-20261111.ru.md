# Форматы объявлений recovery: cold8 и runtime3

Статус: новый код, проверка на серверах ещё требуется. Это отдельное изменение
после frozen C1 root8fac40bb/Pulse1c0fa37; работающий C1 его не проверяет.

Cold8 сохраняет все поля cold7, включая base_schema_version1..4, и добавляет
обязательное invalid_measurement_recovery=advance_rejected_candidate_window.
Нужны candidate-window contract и положительный общий invalid budget.
Flat/scalar конфигурация с этой policy запрещена. Cold7 не принимает новое поле;
декодирование cold8 через cold7 без него запрещено. Старые cold1..7 сохраняют
прежний смысл и формат вывода. Повторная сериализация cold8 сохраняет policy.

Runtime3 сохраняет полный active search и protocol binding runtime2, но явно
содержит новую policy. Runtime2 допускает только retry_same_candidate;
runtime3 допускает только advance_rejected_candidate_window. Перестановка
номера версии или строки policy не превращает один формат в другой.

Python audit_candidate_window_runtime_plan остаётся reader только runtime2.
Новый audit_candidate_window_runtime_recovery_plan проверяет runtime3.
Оба используют общие проверки bounds, budgets, tolerances, C-policy и protocol.
Общая временная validation view cold8 не изменяет оригинальный документ,
который должен сохраняться для запуска, provenance и fingerprints.

Добавлены два real-Environment C++ wire roundtrip/mutation cases, Classic и
Branch, с сохранением пяти producer JSON в recovery-wire. Добавлены восемь
Python DATA tests: версии/policy, неизвестные поля, budgets, protocol binding,
сохранение оригинала и прежнего retry-only reader. Синтетические DATA tests
не доказывают native delivery или физическую сходимость; нужен отдельный
cross-language audit JSON от actual native producer на workers.

Service пока явно запрещает новую policy. Package6, archive/history, ordered
recovery events, независимый replay и Save/Load ещё не подключены. Успешный
codec roundtrip не разрешает дорогой Train и не завершает этап7.
