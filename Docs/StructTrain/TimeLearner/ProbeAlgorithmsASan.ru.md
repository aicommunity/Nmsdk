# Быстрый контур production observer: ASan34 на M40

Приняты все34 unit checks без failures/errors/skips, включая семь новых
SingleImpulseMaximum controls. Это проверка численного observer/clock кода,
не нативных нейронных компонентов и не классификации. Проверки из того же
исходного файла остаются в общем storage executable; повтор не считается
новой независимой научной матрицей.

## Источники и действительная сборка

Root `62997ad1e7cb7869012d11da82b5a48b529ac1e7`, PulseLib
`24f9767ace1f498d5dc048a70fc303789adac757` (Core кандидата6c520fb).
`Test_PulseLib_ProbeAlgorithms` собирает непосредственно:

- production `Libraries/Nmsdk-PulseLib/Core/TimeLearner/ProbeObservation.cpp`;
- `Tests/Integration/Libraries/Test_PulseLib_ProbeObservation.cpp`;
- `Tests/Integration/Support/ProbeAlgorithmMain.cpp`.

Копии тела алгоритма в тестах нет. Четвёртый compile command — generated MOC
translation unit. Сохранены и проверены все четыре фактические compiler
commands, flags.make и link.txt. Target не линкуется с PulseLib/Rdk и не
создаёт Environment. Используются GTest и Qt Core для production capture
handshake. После всех tests тот же owned process остаётся жив до считывания
реальных mappings; повторение tests ради наблюдения короткого процесса не нужно.

RelWithDebInfo, `-O1 -g1 -fsanitize=address -fno-omit-frame-pointer`, ASan linker,
запрошен `detect_leaks=0`, leak check отсутствует. Реальная libasan есть в19
loaded-file records. Unit tests заняли0.005s по JUnit. Эти5ms не являются
временем сборки или измерением производительности физической модели.

Runtime `/media/user/Data/TimeLearnerRefactor/runtime-probe-algorithms-asan-a1`.
`unit-runtime.ini` — статический descriptor роли для manifest, не загружаемая
конфигурация нейрона; физические ресурсы этим executable не используются.
До изменения неактивного source/build проверены closure/release пяти прежних
групп.65 bindings пяти прежних runtime совпали после build/run. Сам worker
закрыт целиком, lease released; M40 schema1 не мигрировала.

## Приёмка и границы

Evidence `05083f7adc476bed4318ab069a70e33727f370db`.
[Bundle](../../../Reports/StructTrain/TimeLearner/s07-probe-algorithms-asan-a1/bundle.json):
43 members,69296 compressed bytes, SHA256
`79be0fba554f42c526d946b7d0f373d038033fecccf25936d56ffe4c7c0bffed`.
[Независимая сверка](ProbeAlgorithmsASanVerification.json) проверила каждый
member,496 root/265 PulseLib source hashes, все34 JUnit IDs, actual compiler
inputs, flags и loaded-file/owned-process/runtime bindings. Локально
выполнялись только Git/archive/hash/JUnit metadata проверки.

Проверены поздний более высокий пик, меньшие экстремумы, равные отдельные
максимумы и плато, clipped/incomplete и пик до фактического onset; schema4
остаётся прежней. Positive schema5 без настоящей одиночной пробы не разрешена.
Семь новых unit cases не доказывают physical routing, lifecycle или корректность
Train. Требуются полные native/Console gates, архивные многопиковые replay,
сопоставление штатной пачки и остальная исходная матрица плана.
