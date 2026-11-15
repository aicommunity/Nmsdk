# Windows package6: отдельная проверка сборки

Это дополнительная подготовка .14, не приёмка native119 и не научная серия.
Проверка исходников/доставки11/11 описана в [предыдущем отчёте](WindowsPackage6SDKPreparation-20261109.ru.md).

## Условия

[Specification](ValidationPlans/WindowsPackage6Build-20261109/specification.json) фиксирует Root877/Pulse674/Bin918/Rdkd6, тот же namespace4052, VS2026/MSVC14.51, Python3.14.2 и vcpkg1577.
Source `source-package6-native119-win-a1` остаётся неизменным. Новые build/runtime/output называются соответственно `build-package6-native119-win-a1`, `runtime-package6-native119-win-a1` и `jobs/windows-package6-sdk-build-a1`, все под C:/Projects/TimeLearnerWorker.

Используется уже установленный dependency prefix build-a4/vcpkg_installed с **VCPKG_MANIFEST_INSTALL=OFF**. Manifest/triplet совпали по bytes с прежним профилем; status hash7e02dc6d4b89d5711c3b62c60d607430189dcc3c599da8581449c300bf0b63ca и полный inventory prefix до/после обязательны. Это повторное использование read-only зависимостей, а не изменение старой сборки.

Versioned `workers/windows-vs2026/sdk-build.py` создаёт фиксированные команды Release/Qt5, BUILD_TESTING=ON, LLM/OpenCV/Python/ODE OFF, один compiler job, два targets: NeuroModelerConsole и Test_PulseLib_StorageComponents. Изолированный deploy/resource root задаётся явно. Перед vcvars устанавливается process-local VSCMD_SKIP_SENDTELEMETRY=1. Никаких исправлений backend ради PASS: существующий windows_process.execute проверяет 4GiB committed memory,32processes,7200s owned command wall budget, loaded files и закрытие Job descendants. Начальное хеширование source/dependencies выполняется до этого owned-command budget; родительский одноразовый Scheduled Task ограничен3h. Потоки этим backend не ограничиваются; parallel=1 ограничивает compiler jobs.

`launch-sdk-build.ps1` принимает точные tool commit и specification Git blob, отказывает при существующей попытке/активном TimeLearner task, проверяет worker/Python bytes и сохраняет task XML/instance/dispatch. Изменений пользовательского C:/Projects/Nmsdk нет. Новая компиляция не продолжает старые неудачные задания.

## Приёмка и оставшиеся шаги

Обязательны actual completed/valid/closed backend result, неизменные source/tools/dependencies, оба executable и runtime inventory. Ошибка configure/compile/descendants/provenance сохраняется как отрицательный результат; exit0 оболочки недостаточен. Данная проверка **не запускает C++ tests или модели**. После успешной сборки остаются отдельные native/portability checks, cooperative DLL capture, model export/import, Console Train→Test и научные допуски. Обязательные проверки двух Linux workers не заменяются Windows.

## Фактический запуск A1

Tool source3059baa4a176f5d7e0047e93b9b1206934a9c069 доставлен отдельным Git pack; specification blob2cdb4c30fb4a99cec15a37ae1b4a722fb4dd73d7 проверен до dispatch. Создан ровно один task TimeLearner-package6-sdk-build-a1, instance28E4AC18-AF33-428F-B716-011B9C9EDAB2. [Dispatch](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-build-a1-launch-root-observation/dispatch.json) и [первое наблюдение supervisor](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-build-a1-launch-root-observation/first-task-and-supervisor.json): Python PID14080/creation UTC2026-11-09T18:29:48.8688660Z, parent10108; task running.

После сверки4052 source files и inventory dependencies создан owned Job Local\\TimeLearner-a56fe0fd-f271-4648-a644-92ccfb92e326. [Kernel/compile readback](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-build-a1-launch-root-observation/first-owned-kernel-and-compile.json) подтвердил cmd PID984 с точным creation FILETIME134387227012441181, runtime fingerprint9d804641001c4965d9347641603500f58fb98026d9a67640741c419701998ddd; процесс live. CMake configure/generate завершён, Ninja реально начал526 build actions. Обнаруженный CMake compiler ID MSVC19.51.36260.0 записан отдельно от пути tools14.51.36231. Предупреждения CMP0167 и unused VCPKG_OVERLAY_TRIPLETS сохранены; dependency installation отключён, фактический installed triplet выбран CMake.

Terminal result пока отсутствует. Первое чтение live cmd stdout через ReadAllText было отвергнуто Windows sharing rules; это ошибка наблюдения, не остановка задания. Повторное чтение использовало FileShare.ReadWrite/Delete и сверило тот же process identity. Повторный запуск не выполнялся. Полного build PASS, native tests и научного результата ещё нет; ни один раздел общего плана не закрывается на основании dispatch или первых compile actions.
