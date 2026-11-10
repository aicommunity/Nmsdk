# Native Load history и replay реальной модели — 10.11.2026

## Состояние и границы

Полный regression20 на SDK739/Pulse608 завершился3 executed/2PASS/1FAIL/17not-run; [primary сохранён и проверен](NativeImageRest20Preservation-20261110.ru.md). Classic package roundtrip сохраняет InputFeedbackSignal1×1zero против0×0empty. Не объявлять эту ошибку исправленной на основании новых syntax/preparation checks. Цель всех этапов1–12 остаётся открытой; нового научного результата классификации нет.

Новые6 generic controls используют реальные NPMembraneBio/storage/Environment, native Save/Load/Init/Reset и root scheduler при2000/20000Hz. Ненулевой local input0.25 отличает потерю данных от разного представления нуля. Проверяются fresh target, target с прежним внутренним источником0.75 и отдельный положительный контроль с native disconnect/удалением прежних детей до Load. Проверяются полный physical identity, исчезновение старого child/source, local input до/после Load/Reset и8 actual feedback/time samples. Это fixture локального динамического входа, не изменение общей физики профилей.

Порядок SetComponentProperties перед DelAllComponents в UNet::LoadComponent — гипотеза о влиянии прежнего графа. Она пока не подтверждена runtime; виды property connections (external source/pointer) могут различаться. Test наблюдения явно сохраняют тип прежнего источника. Даже подтверждение общего Load-дефекта само по себе не докажет причину ошибки конкретного trained package: нужен actual model replay и исходный full roundtrip.

## M40 A1: ошибка компиляции теста

SourceRoote6335f89665925165c0596195d5b98b0c569d0ce/Pulse608/Bin8cb/Rdkd6,4070files/8repos. Canonical source preparation прошёл, затем build остановился на const UEPtr→UContainer в новом Test_PulseLib_NativeLoadHistory.cpp:46. **Built=false;0 actual tests,6not-run**, без вывода об алгоритмах. Supervisor3965131 отсутствует; outer227a3e60-4a16-4140-ab25-245c4ceaab7b и compiler descendants закрыты,0native children, record/heartbeat/final_capture errors пусты. [Все56 output/controller files и CMakeCache сохранены побайтно](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/m40-a1-full-compile-failure-records-exact.json.gz). Старые source/build/runtime не обновлялись.

Test-only fixf19979362 использует явный static_pointer_cast. Production Rdk/Pulse алгоритмы не менялись. Нельзя называть эту compile failure новой ошибкой обучения или общим дефектом Rdk.

## A2: сначала actual saved model

SourceRootdcc2a3a749d3546de38258aa870fcaa6c47c2bc8 имеет4073files/8repos и дополнительный NativeClassImageReplay/ClassicActualSavedModelAcrossNativeGraphRelease. [Source fixture](../../../Tests/Integration/Data/NativeWindowPackage6Classic/descriptor.json) — точные исходные4812359bytes ранее опубликованного N2 train_learned_state.json, SHA2561c8d50628e7eea87c2bad230428526000802ec73e9627bd5d7d7f414bb69e05c. Qt-compatible lossless compression323020bytes; JSON не переписывается, SHA проверяется до parsing. Файл получен из evidence978ca1af3e8fbc44e65e035d614a023301e468d2, original source739/Pulse608. Это saved-state engineering replay; он не заменяет cold Train или научную N4 серию и не подтверждает весь source learner package.

Replay3 раза выполняет реальные PrepareModelArchive→dataset/model Import→Export, проверяет полный archive и всю physical identity. Затем native BreakLinks/Free освобождает реальные дочерние графы перед новым циклом. UStorage::ReturnObject сам только деактивирует/отсоединяет root и снимает UseFlag; он не освобождает детей. Поэтому прежние2 successful image controls с ReturnObject этот путь не покрывали. Ни XML fields, ни hashes из equality не исключаются.

[Точная declaration7](ValidationPlans/NativeLoadReplay7A2-20261110/cohort.json): сначала actual saved-model replay отдельным process, затем6 generic controls другим process. Fail-fast сохраняется: если первый leaf не проходит, последующие6 считаются not-run. ASan4GiB per leaf/8GiB outer,2compile jobs, отдельные source/build/runtime/output. CapturedPerInput, tolerances и существующие mathematical defaults не меняются.

Actual syntax-only compiler check Rootdcc TU завершён completed/exit0 с закрытой cgroup,2GiB/60s; никакие test/model не запускались. [Raw records](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/syntax-preflights-and-success-exact.json.gz) сохраняют и первый отказ до запуска из-за loader manifest с null. Более ранний reservation refusal также сохранён отдельно. Финальный caller учитывает фактический legacy registry без capacity policy и сохраняет cgroup limits; policy/quotas registry не изменялись. Syntax check не является linked integration acceptance.

A2 canonical preparation прошёл4073files/29same-SDK modules/71closed prior bindings. [Native dispatch](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/m40-a2-replay-launch.json): supervisor4058982/start336717332, boot0340843f-8a05-4b7e-bd66-afeefecdbe55. [Свежий kernel readback](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/m40-a2-first-kernel-exact.json) подтвердил supervisor/outer live, bindingd0989c3513b5ded9db96da1997bf9903f5132331188ad3842dd6d9fca1d5a09a. Verdict7 ещё отсутствует.

## Параллельная Windows .14

Отдельный source-native-load-history-win-a1 содержит **e633/Pulse608/4070files**, а не новый dcc4073. Все8Git checkouts доставлены без alternates; [штатный verify-sdk.ps1](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/windows-sdk-verification-exact.json) проверил4070physical/Git files и чистые8HEAD. Первый прямой вызов module не настроил console UTF8 и отказал на кириллическом имени; повторена только проверка через штатный CLI. Source checkout не пересоздавался.

[Windows build dispatch](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/windows-build-dispatch.json): TimeLearner-windows-native-load-history-build-a1, instance32FE39E7-2C52-44C0-9247-2544CCBE0BB1, Toolc3ac2470487635c176b4ba7d375f44d667e4f12e, specblob2509f0507f78277835e03958102dc175d06e8408. [Owned main16540/FILETIME134387634942144163](../../../Reports/StructTrain/TimeLearner/s04-native-load-history-preparation-root-observation/windows-build-first-live-identity.json) подтверждён живым с совпавшим временем создания; named JobLocal\TimeLearner-b73757b8-40d1-409d-bac8-baef2a63c530. Эта сборка исходного e633 не обновлялась после Linux compile fix; её фактический итог нужно получить отдельно. На Windows новые6/7 native tests ещё не запускались. Старые4/4 SDK4eb/Pulsef1 не являются приёмкой нового608.

После runtime наблюдений исправлять подтверждённую причину на уровне владельца и проверять actual package5/reader16/full119/Console Train→Test. Не менять поле XML вручную и не заменять требования сходимости более лёгкой scientific задачей. Полная приёмка стадий1–12 остаётся открытой.
