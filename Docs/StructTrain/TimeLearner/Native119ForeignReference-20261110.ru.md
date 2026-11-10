# Native119: корректная постановка проверки принадлежности эталона

Исходный SDK8ec на M40 завершил65/119:64 PASS,1 FAIL,54 not-run;38 leaf gates. Full119 не принят. [Исходный terminal/progress](ValidationPlans/Native119ForeignReference-20261110/m40-terminal-readback.json), [JUnit17](ValidationPlans/Native119ForeignReference-20261110/m40-portable-proof6-native.xml), [наблюдение kernel closure](ValidationPlans/Native119ForeignReference-20261110/m40-owner-closure.json). Полный compact primary этого задания ещё не опубликован; указанные metadata не заменяют его.

Отказ: NativeCandidateWindowPortableMath/RehashedForeignReferenceProofCannotJoinActualFinal. Полный17-case leaf отработал663.205s,16PASS/1FAIL. Проверка устанавливает referenceProofId=foreign-original-reference и ожидает, что standalone decode пройдёт; действующий wire-контракт требует64 lowercase hexadecimal chars, поэтому возникает candidate_window_hash_id_format до проверки принадлежности. Это воспроизведённая ошибка постановки теста; production не менялся.

Кандидат исправления использует semanticProofId реального reference другого входа того же наблюдаемого архива. ASSERT_NE подтверждает отличие от исходного эталона. Standalone decode обязан пройти; после пересчёта recipe/instance/semantic hashes и при неизменных primary blobs archive replay обязан отвергнуть чужой reference с точной причиной candidate_window_proposal_replay_mismatch. Форматный отказ больше не может дать положительный итог теста.

Изменён только Tests/Integration/Libraries/Test_PulseLib_CompositeTraining.cpp. Lifecycle, scheduler, физика, цель CapturedPerInput, допуски, данные и критерии сходимости не менялись. Кандидат пока не скомпилирован и не проверен runtime. Следующий шаг — серверная проверка полной TU и адресный production native gate, затем полный119/reader16/Console.

Elder на последнем наблюдении продолжал тот же portable-proof6-17; он не остановлен по результату M40. Windows .14 отдельно собирает неизменный SDK8ec; её runtime не обновляется на лету. Научных выводов из данного fixture отказа не делаем.
