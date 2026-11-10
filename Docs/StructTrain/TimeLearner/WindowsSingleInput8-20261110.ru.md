# Windows .14: одновходовые native8,10.11.2026

Подготовлен отдельный native gate на неизменном audited SDK8ec/Pulse165/Rdkde/Bin8cb. Это дополнительная portability-проверка матрицы N=1, а не замена Elder/M40 и не классификация stock N4. Все исходные Windows build outcomes сохраняются; [closed-build audit](WindowsOpenArmPreparation-20261110.ru.md) прошёл отдельно.

[Точная спецификация](ValidationPlans/WindowsSingleInput8-20261110/native-specification.json), [сопоставление неизменных test blobs с Linux subject](ValidationPlans/WindowsSingleInput8-20261110/source-scope.json). Root8ec отличается от Linux f2 исправлением другого теста CompositeTraining; выбранные NativeExecution/NativeModelEditor blobs побайтно одинаковы.

Восемь actual cases:

- Classic/Branch single-input native probes при2000 и20000Hz —4 случая с реальными input/soma traces и свежей финальной проверкой.
- NativeLearnedState/ClassicOneInput и BranchOneInput —2 случая: cold construction/Train, reference/final, полный model export, same-process и fresh-process import, точное сравнение waveform CSV. Реальные условия:2000Hz, Classic TipResistance и Branch SynapseCount, CalculateMode1, explicit scalar protocol3, transport heterogeneous C=1.41e-9 в проверяемом канале. Не cold7/omission fallback.
- NativeRecognitionOwner/BranchSingleInput и NativeRecognitionState/BranchN1SingleInput —2 отдельных recognition control того же scalar boundary; не обещание target/foil разделимости.

Штатные production native gate schema4 и Windows Job backend берутся из compiled SDK. Budgets:4GiB committed memory,32processes,1800s wall. Обязательны полный exact8 JUnit inventory без skips, cooperative loaded-module capture, весь Job закрыт, source/runtime сохранены. Не допускать параллельного изменения runtime.

Сейчас gate подготовлен, но не запущен. После закрытия — полный compact primary в Git, independent hashes, читаемые временные графики с actual stimulus overlay. Полная N=1 матрица N0/N1×частоты×CalculateMode0/1/external stop/public Console не закрывается этими8 cases.
