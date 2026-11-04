# Изолированная ASan-сборка joint-кандидата

M40 build-only source `9f92a40b97b5868b84b156e38b91903e6b0d8176`,
Pulse `cc97149c90ce98ff24ca688452f4a40d54e0e63d`: построены
Test_PulseLib_StorageComponents и NeuroModelerConsole. Worker3717866/
start284925354 работал с одним compiler, cgroup memory4GiB/tasks128,
preflight MemAvailable>=36GiB. Native gates и модельные расчёты не запускались.
Whole worker закрыт, его schema1 reservation освобождена; ledger живого K1
не мигрировал, первоначальный ASan regression продолжает работу независимо.

Proof `3e07bd1104e6bee7917c3c79b7451e225bd6f287` содержит сжатый primary,
source/build/runtime manifests, kernel closure и четыре фактических flags.make
с `-O1 -g1 -fsanitize=address -fno-omit-frame-pointer` для Rdk/Pulse/tests/Console.
Manifest разрешает libasan в фактических linked dependencies; loaded-process
capture не заявляется, поскольку native test ещё не запускался.
[Сверка](JointASanBuildVerification.json):65 members,510 исходных blobs
побайтно равны ранее независимо проверенному normal9f snapshot, четыре
instrumented target flags, завершение и освобождение ресурса.

Этот source содержит известную ошибку fixture expectation из failed normal42.
Перед gate нужна пересборка corrected source
`8021301e894368aefd045f9d77274fcce9f60245`. Отдельный build-only a2 уже
подготовлен после kernel-подтверждения закрытия predecessor: source/build
можно использовать инкрементально, а новый runtime имеет отдельный каталог.
Прежний runtime-a1 и его manifests сохраняются. Production C++/App/CMake
и семь gitlinks между9f и8021301e одинаковы; изменены test/spec/docs.

Новый build также не запускает gates: focused44/full304/readers разрешаются
отдельно по завершению текущего K1 и фактическим ресурсам. Успешная компиляция
не является runtime-приёмкой joint algorithms, проверкой новой физики либо
научным результатом. Все исходные этапы1–12 остаются частичными.
