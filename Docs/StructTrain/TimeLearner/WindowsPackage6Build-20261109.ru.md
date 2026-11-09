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

На момент постановки результат новой сборки отсутствует; статус dispatch/terminal фиксируется отдельным фактическим readback. Ни один раздел общего плана не закрывается на основании подготовленного source/specification.
