# Elder: normal18 на том же SDK355 запущен

Source root `355c60df066bdc8da09bd6d7872b47f6e71c0494`, Pulse
`165d49da7e65cd6ac59bca2812ce52884ddd50c2`, Rdk
`de4134235c0dcb8b91fd9a43b267348ad1a163ca`, Bin
`8cb6dba07b30432272984c8ce3136b48ad06f064` совпадают с M40 move18.
Изменяется build profile: Release/O3/LLM Off, без ASan. Это отдельная
runtime-проверка, не доказательство побитовой эквивалентности сборок.

После завершения очистки старых tracked Reports copies подтверждены:
owner missing, no held leases и17256341504 свободных bytes. Декларация
резервирует12GiB диска при capacity14GiB; требование fresh build сохранено.
Protected historical runtime не обновляется. Источники/ресурсы доставлены Git,
все восемь repositories изолированы от пользовательских копий.

A1 canonical completed0/clear за67.11735970899463s, но native preflight
отклонил `owned_native_SDK_worker_helper_version_not_tested` до компиляции:
новый tool98 имел другую версию worker относительно SDK355. [Исходный отказ](ValidationPlans/ElderNativeArchiveMove18-20261110/launch-rejected.json).
Защитная проверка не ослаблялась. Выбран тот же native tool, что используется
на M40: `1386206616d82952166ece926e814cd2c5aafbb9`. Побайтно подтверждён
native_acceptance_worker SHA256
`e3069ca54c32af9a2a055135c7ac9e46154aa757d13a22ceaab82227bc13a910`.

A2 [замороженные спецификации](ValidationPlans/ElderNativeArchiveMove18Retry-20261110/cohort.json)
записаны в root `4692ea63de8afce248ff22ae36d9f0e724a890ab` до запуска.
Canonical completed0/clear за66.57090041879565s, group closed/lease released.
Это подготовка, не выполнение C++ tests.

[Запуск](ValidationPlans/ElderNativeArchiveMove18Retry-20261110/launch-observation.json)
и [kernel/build observation](ValidationPlans/ElderNativeArchiveMove18Retry-20261110/running-observation.json)
подтверждают supervisor1687/start388720843 и actual main7419/start388721787:
unit `timelearner-f33b896c-71f9-47e1-b01d-24a0d9a9ff70.service`,
invocation `563babb6408f448e8a4098df2ba11692`. Сборка действительно продвигается.
Output `readbacks/s05-native-archive-move18-normal-a2`, отдельные build/runtime
с тем же suffix. Все18 проверок сохраняются, package cases разделены по
процессам/JUnit;4GiB/128tasks leaf limits, whole43200s.

Полный результат normal18, сохранение primary и его независимая приёмка ещё
впереди. M40 ASan15 completed PASS подтверждены отдельно; C0 и две warm
проверки продолжаются. Ни этот запуск, ни освобождение диска не завершают
этапы1–12 и не являются новой научной классификацией.
