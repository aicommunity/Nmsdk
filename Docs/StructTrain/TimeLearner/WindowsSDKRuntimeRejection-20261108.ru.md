# Windows SDK: вычисления выполнены, runtime gate отклонён

На .14 скомпилирован root8314e98f7 /PulseLib9e06409. Native-only A2
прошёл23/23 scalar C++ cases и все21 physical assertions без skips.
Первый unit gate принят с cooperative capture и37 module records.
Полный physical gate **не принят**, научный worker не допущен.

## Два разных отказа

1. Build A1: cmd завершился с exit0, но внутри принадлежащего ему Job остался
   PID10872. Backend закрыл Job и вернул `descendants_remaining`.
   Идентичность уже закрытого потомка не установлена; compiler service —
   только возможное объяснение, не установленный факт. Build execution failed.
2. Native A2: C++ выполнил21 cases за1403503ms и записал полный JUnit PASS.
   На границе выхода был записан правильный ready PID/creation FILETIME,
   но фактическая инвентаризация DLL вернула `windows_module_path_unavailable`.
   Запускатель закрыл процесс. Returncode остался unknown, gate —
   `incomplete_test_observation`, assertion status — `not_assessed`.
   JUnit PASS и принятый end-to-end gate здесь не объединяются.

Нельзя восстановить положительный runtime verdict по заранее ожидаемым DLL,
по unit23 mappings другого executable или по совпадению source HEAD.
Неизвестная module identity остаётся пробелом доказательности. Длинные модели
не перезапущены; дальнейшую диагностику collector следует начать на коротком
StorageComponents case, сохраняя этот failed attempt.

## Дополнительный дефект размещения логов

Exe/DLL/ini сохранены, но в runtime появилась новая
`EventsLog/NeuroModeler.DESKTOP-RV8IOD6.User.log.INFO.20261107-230307.1076`.
Сейчас native gate не направляет этот engine log в отдельный job output.
Перед допуском необходимо исправить адресацию логов и включение их в manifest,
а не объявлять весь runtime каталог неизменным. Инвентаризация before/after
и имя нового файла сохранены; его содержимое ещё требует отдельного сбора.

## Артефакты

Evidence `9822ce2e1248787b2f494063d82f90c75a799eec`:194 primary members,
775916B compressed, SHA256
`3b8b71aeb1eada6ffdb398f100eff028bd62c9c5ffe8970a40edd90d81ed1249`.
Включены source/runtime manifests, команды, build logs, JUnit, CSV,
ready record, gate rejection и свежая проверка закрытия всех трёх Jobs.
[Независимая metadata-сверка](WindowsSDKRejectionVerification.json) проверила
каждый member и согласованность трёх осей: assertions, execution и validity.
Передача выполнена Git pack; локальных численных проверок не было.

Полный refactor, stage2/10 и научная матрица этим не завершены. Linux jobs
продолжаются независимо; пользовательский `C:/Projects/Nmsdk` не менялся.

Подготовлено отдельное диагностическое уточнение backend: сохраняются операция
PSAPI, код Win32, адрес модуля и уже прочитанные пути, а также накопленные
частичные mappings при неуспешном завершении. Они не подменяют завершённый
cooperative capture и не делают A2 валидным. Повторное считывание с пропуском
неудобного модуля не введено: сначала требуется воспроизведение на коротком
реальном SDK case с этой диагностикой.

08.11 выполнены две новые попытки. Первая выявила ошибку записи диагностик
дважды в immutable file и последующую утечку host lock; native gate не начинался.
Исправлено: файл записывается один раз после закрытия owned Jobs, lock
освобождается в finally даже при ошибке сохранения. Добавлен реальный
отрицательный контроль: дочерний процесс создаёт конфликтующий report file,
после отказа записи следующий worker получает тот же lock.

Вторая попытка прошла17/17 backend controls без skipped и короткий реальный
`NativeBurstAssignment/BranchWrongPhysicalSelector` с валидным cooperative
capture. Отдельный poll зарегистрировал `EnumProcessModulesEx` Win32 error299;
успешный boundary capture выполнен позже по фактическим mappings, без
подстановки ожидаемых DLL. Старое исключение при неудаче чтения имени модуля
не входило в перехватываемые poll ошибки; новое сохраняет операцию/Win32 код
и обрабатывается как ошибка наблюдения. Ошибка boundary остаётся отказом.

Обе попытки опубликованы в evidence `092de4cf8bfe831c834b75d082151f4a104bb994`,
266 members,38628B compressed. [Независимая сверка](WindowsModuleDiagnosticsVerification.json)
проверила все members, creation identity и закрытие19 owned Jobs. Старый
418-byte runtime EventLog также теперь сохранён в Git с исходным hash.
Исходный длинный отказ этим не объявлен воспроизведённым или исправленным
в полном SDK. Начат отдельный A3:23 unit и21 physical checks на прежнем
compiled root8314e98 и backend289c3bc, с отдельными первичными данными и
cooperative capture. Build execution, вынос EventLog и scientific admission
остаются открытыми.
