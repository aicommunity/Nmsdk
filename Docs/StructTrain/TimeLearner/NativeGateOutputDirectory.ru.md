# Изолированный native gate: каталог результатов

06.11.2026 установлен конкретный дефект общего Python runner. Он выставлял
TIMELEARNER_EXECUTION_OUTPUT, но не создавал назначенный каталог. Некоторые
fixtures создавали его сами, а BranchAliasing сохранял JSON с Qt NewOnly.
В монолитном normal304 каталог уже существовал благодаря предыдущим fixtures;
изолированный ASan test0090 не мог открыть первый JSON. Это зависимость от
порядка тестов, а не доказанная ошибка физики Branch или sanitizer finding.

Исходный ASan133 SDK2e завершил все133 actual processes:132 passed и1 failed,
NativeBranchAliasing/CoincidentLabelsExposeOneEffectivePhysicalBank.
Первичный JUnit указывает Test_PulseLib_NativeExecution.cpp:657,
file.open(QIODevice::WriteOnly|QIODevice::NewOnly)==false. На сервере подтверждено,
что cases/0090/native отсутствует. Исходные stdout/JUnit/manifest сохраняются;
отрицательный итог не переименовывается в PASS.

Исправление native_gate.run_native_gate: создать собственный пустой output/native
до установки переменной и запуска. Бинарники, native test body, model physics,
численные допуски, expected IDs и проверка JUnit/loaded files не меняются.
Существующий output по-прежнему запрещён; source/runtime overlap guard сохранён.
Проверка нужна на прежних normal/ASan binaries с этим точным isolated test,
затем свежий полный ASan133. До этого общий SDK gate остаётся непринятым.
Проверки с извлечённой копией тела функции или mock моделью не предусматриваются.

Адресная приёмка06.11: прежние SDK2e normal и ASan binaries прошли тот же
изолированный оригинальный C++ test, оба записали по2 штатных BranchAlias JSON.
Elder data `f52d481fd095987186ec2018855883cb872d4197`, M40 data
`58334ecb5454c0694ac90c230cb9e534680b22e3`; проверены все25 members каждого
архива,284 tool source hashes, реальные loaded binary/libasan и fresh closure/
released lease. [Receipt](NativeGateOutputDirectoryVerification.json).
Новый полный ASan133 A4 запущен отдельно на тех же бинарниках с исправленным
runner642a9c875; исходный A3 остаётся132 passed/1 failed. Ни адресный PASS,
ни запуск A4 не подменяют полный свежий итог. Область приёмки этого исправления —
подготовка output в Python gate, не весь SDK и не алгоритм Branch.
