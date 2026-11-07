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
