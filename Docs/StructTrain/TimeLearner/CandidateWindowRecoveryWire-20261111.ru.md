# Форматы объявлений recovery: cold8 и runtime3

Статус: Python readers проверены81/81 на M40; C++ C2 принят146/146 на M40,
включая два native wire roundtrip. Elder C2 и independent cross-language
проверка native producer ещё требуются. Это отдельное изменение
после frozen C1 root8fac40bb/Pulse1c0fa37; работающий C1 его не проверяет.

Следующий frozen C2 root5643f8319/Pulse0fb035a содержит146 cases/49leaf gates.
Все4104 source files и восемь Git repositories доставлены на Elder и M40.
Два прежних запуска подготовки M40 остановлены до сборки на cohort file
binding и совпадении external output с owned job directory. Декларации C2C
исправляют эти ошибки. Canonical M40 принята за79.77с с clear diagnostics
и закрытым cgroup; запущена отдельная SDK сборка/native146, supervisor
PID82620/start346617135. C2 завершён146/146 valid PASS, outer и49child groups
закрыты, lease released: [terminal](ValidationPlans/M40CandidateWindowRecoveryWireC2C-20261111/completed-terminal.json),
[closure](ValidationPlans/M40CandidateWindowRecoveryWireC2C-20261111/completed-closure-and-lease.json).
Elder canonical принята за67.53с, но native launch остановлен до создания
задания проверкой диска: около6.03GB свободно при требовании4GiB reservation
+2GiB floor. Смена научных параметров или запуск без проверки места не выполнялись.
После этого удалены только15 generated child directories трёх устаревших
сборок. Все source/runtime trees и CMakeCache.txt сохранены; runtime snapshots
до/после равны. Свободное место выросло с6005776384 до6659514368bytes:
[точный receipt](ValidationPlans/ElderObsoleteGeneratedBuilds-20261111/retirement-completed.json).
Elder native146 запущен, supervisor PID2684254/start396745925;
[launch](ValidationPlans/ElderCandidateWindowRecoveryWireC2C-20261111/native-launch-receipt.json).
Итоговой приёмки Elder C2 пока нет.
Неудачные прежние outcomes
сохранены; их нельзя считать сборкой либо результатом C++ тестов.

Cold8 сохраняет все поля cold7, включая base_schema_version1..4, и добавляет
обязательное invalid_measurement_recovery=advance_rejected_candidate_window.
Нужны candidate-window contract и положительный общий invalid budget.
Flat/scalar конфигурация с этой policy запрещена. Cold7 не принимает новое поле;
смена только номера cold8 на7 при сохранении поля policy запрещена. Старые cold1..7 сохраняют
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

## Проверенная область

На M40 выполнены81/81 объявленных DATA tests, failures/errors/skipped=[];
восемь новых runtime3/cold8 controls, десять прежних runtime2 declarations,
десять synthetic archive2 controls,14 package6 metadata и39 candidate-window
DATA controls. Source root e273a7e715c839e83023aeb246dd2725e45d1001 /
Pulse0fb035a221d6da2b2e883bf767a20a35318d3154,
package fingerprint66a7f46eda7b25bd6d7c204a4984809473b8fb7c04cf8c3a4ae6795b5f430391.
Whole cgroup закрыт, lease released/owner missing, operational diagnostics clear.
[Точные результаты и integrity readback](ValidationPlans/M40CandidateWindowWirePython81A2-20261111/readback-integrity.json).
Первая попытка остановилась до тестов из-за отсутствовавшего Git-объекта
`.gitignore`; её outcome сохранён отдельно. A2 использует новый исходный
каталог с полным набором root metadata. Эти81 не являются новыми научными
прогонами, приёмкой C++ wire или всего этапа7.
