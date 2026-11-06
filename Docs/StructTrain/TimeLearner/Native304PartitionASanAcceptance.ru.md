Дополнение06.11: [новый SDK2e/Pulse12d full normal304 принят](SharedSdkNormal304Acceptance.ru.md). Прежнее ожидание normal304 ниже относится к предыдущему снимку; ASan и научные проверки отдельные.

Дополнение06.11: [ASan fresh owner8/readers128 приняты](JointOwnerReplayASanAcceptance.ru.md); старые формулировки ожидания ниже относятся к предыдущему снимку. Новая shared SDK проверяется отдельно.

# Полный изолированный ASan304: приёмка программных проверок

06.11.2026 завершён полный объявленный набор304 случаев на M40. Каждый случай
запущен отдельным настоящим C++ процессом через production native gate.
Итог: completed/valid/passed,304/304, без пропущенных случаев. Это SDK
root `8021301e894368aefd045f9d77274fcce9f60245`, PulseLib
`cc97149c90ce98ff24ca688452f4a40d54e0e63d`, tool root
`86118630da6fed4763715209e4405980cad59f0d`.

Полный [primary bundle](../../../Reports/StructTrain/TimeLearner/s07-native-partition-full-asan-a2/bundle.json)
в data commit `fe0eb83ed076a65ddf3a3b328213e31669def305`:

- 12095 архивных файлов,3004016565 несжатых bytes;
- сжатый архив23863564 bytes,
  SHA256 `9e13eeaee1700e31b2ff86946b51667bcfa3a508453bc15bb703cbcd1a5d5ef6`;
- wall time native partition runner38135.457s;
- whole-worker cgroup peak **через завершение native**3696586752 bytes
  при cap45097156608 bytes; events max/oom/oom_kill равны0;
- leak detection выключен (`detect_leaks=0`), отсутствие утечек не доказано.

## Проверка доказательств

На сервере и после получения через Git повторно проверены все archive member
hashes. [Независимая сверка](Native304PartitionASanVerification.json) проверяет
304 исходных JUnit, ровно один фактический случай на partition, завершение
каждого процесса с returncode0,304 различных boot/PID/start идентичностей,
соответствие executable/runtime fingerprint и реальную libasan mapping
каждого процесса. Все683 compiled-source files и325 tool-source files
сверены с точными Git blobs их собственных commits.

Aggregate native.xml является производным от исходных XML. Единый
`native-result/process/result.json` для якобы совместного процесса не создавался.
Lossless native projection проверена серверным publisher по исходным case
файлам; differing same-name files не перезаписывались. Primary содержит
как исходные partitions, так и manifest этой проекции.

Parent cgroup свежо проверена закрытой, reservation освобождён. Результат
не выведен из числа строк OK или наличия файлов: проверены полный inventory,
исходные test outcomes, runtime и archive closure. Прежний монолитный ASan
StackStore failure сохранён и этим прогоном не превращается в PASS.
Разделение процессов — явно отдельный протокол исполнения проверок.

## Продолжение и границы

Данные опубликованы в origin, точный remote ref проверен. В очередь
`s07-joint-asan-owner-readers-a3-queue` записан agent-owned
`native304-published-origin.json` с exact data commit и archive SHA256.
Это разрешает следующий адресный этап, но не утверждает его успех.

Далее идут fresh owner8 и readers128; только после их PASS/closure —
сборка новой shared SDK2e/Pulse12d ASan, focused8 и lifecycle133.
Данный ASan304 относится к SDK802/Pulsecc, **не** к новой SDK2e/Pulse12d.
Нормальный полный304 на новой SDK запущен отдельно на Elder без пересборки,
после проверки runtime и освобождения подтверждённых дубликатов/кэшей.
Его результат пока неизвестен; прежние8+133 его не заменяют.

Этот документ — приёмка программного gate, не отчёт классификации восьми
паттернов и не independent evaluation. Все физические профили, режимы,
legacy/V2 A/B, научные order/ITI/reset проверки и полный план этим не закрыты.
Общая цель и этапы1–12 остаются открытыми.
