# Windows .14: новый согласованный package6 SDK

Доступ по существующему SSH-ключу к user@10.245.1.14 подтверждён. Наблюдены9384370176bytes свободной RAM и1777677946880bytes на C:, активных Scheduled Tasks TimeLearner нет. Пользовательский C:/Projects/Nmsdk остался на8a723d07ff22bbcc75351457400e3c9e5c8ed1d1 с пустым tracked status; его исходники/ветки не менялись.

Через Git pack/index-pack доставлен отдельный C:/Projects/TimeLearnerWorker/source-package6-native119-win-a1. Root877c1534686d4769142eb690b25799950c1fac81, Pulse6741b3c4c05855bf6b53102d27c07cba64378657, Bin918ae5e1a2d6085b9ff148f7162eb9e744126592, Rdkd6c9df759a3ee20ad42fa0a83841f19385fba60a и ещё четыре libraries совпадают с Linux A2. Восемь standalone repositories clean, без alternates; все4052 фактических файла сверены по размеру/SHA256 с тем же namespace Git blob48ab6e2abe6dbf6a189d66362f00336b8f9129c6. core.autocrlf=false/core.eol=lf применены к новым private repositories для точного соответствия Git bytes.

[План и полные SHAs](ValidationPlans/WindowsPackage6SDK-20261109/plan.json), [namespace readback](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-sdk-root-observation/namespace.json), [closure](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-sdk-root-observation/closure.json), [память/пользовательская копия](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-sdk-root-observation/capacity-and-user-project.json), [tool paths](../../../Reports/StructTrain/TimeLearner/s02-windows-package6-sdk-root-observation/build-tools.json).

## Исправления подготовки

Начальная передача столкнулась с Windows command-line limit на270 sparse patterns Bin. Подача длинного JSON через PowerShell stdin затем зависла; остановлен только собственный powershell PID9724 с проверенными creation UTC2026-11-09T17:39:41.4595260Z и SHA payload9f0769e6ab5e1b62ca5baeb87b75e6b5d138816c387642e8388de75f11a8100a. Вычислительные задания не затрагивались.

Временный cmd guard `if errorlevel 1` не обнаружил отрицательный exit после остановки и позволил пройти к следующему child. Его exit0 поэтому не являлся доказательством доставки всего SDK. Bin завершён отдельно через metadata Git blob e769bf65c9f1f2f099a07c1b0e917c5a925ddbf1; после этого независимо проверены все4052bytes/paths и8HEADs/status, а не только код оболочки или строки DELIVERED.

Для последующих операций логика вынесена в корневой пакет workers/windows-vs2026/GitPreparation.psm1: любой native exit!=0 отвергается, metadata читается из Git blob, sparse patterns записываются LF непосредственно в Git metadata, существующий checkout не переписывается. verify-sdk.ps1 проверяет полный namespace, отсутствие extra files/reparse paths и фактическую Git closure. test-git-preparation.ps1 содержит адресные проверки signed/unsigned failures, long sparse fixture, отказ изменения готового checkout/пользовательского пути и actual4052 SDK. На момент первого source commit эти новые utilities ещё не исполнялись; их source-only нельзя путать с уже выполненным независимым readback SDK.

## Следующий build

Доступны VS2026/MSVC14.51.36231, CMake/Ninja, private Python3.14.2 и установленный dependency prefix build-a4/vcpkg_installed. Vcpkg HEAD1577f17ee57f42a0ef6d75bbb82cb37d0b76d7e8. VsDevCmd.bat SHAa7815e85d636828e5cf70fe4235b11fcb41750896a4d2d60756b43bacaf4f0b2. Первый найденный python.exe внутри Perl/venv не считается интерпретатором worker; использовать именно tools/python/python-3.14.2-x64-1/python.exe после version/hash readback.

Нужны отдельные новые build/runtime/output, bounded Windows JobObject, process-local VSCMD_SKIP_SENDTELEMETRY=1 до vcvars, один compiler job, Release/Qt5/BUILD_TESTING=ON/RDK_USE_LLM=OFF и явная проверка dependency profile. Старые source/build/runtime не перезаписывать. Diagnostic256MiB/no-op не является full-build budget; прежние18/18 native cases не подтверждают новый snapshot. Не игнорировать оставшихся descendants или отсутствующий DLL capture ради PASS.

Новая компиляция/новые C++ tests/научные модели на этом SDK ещё не запускались. M40 A2 продолжает независимо работать; .14 — дополнительная подготовка и не заменяет обязательные Linux checks или новый Console Train→Test. Этапы1–12 полного плана остаются частичными.
