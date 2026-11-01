# Развёртывание Neuro Modeler на Windows

## RU

## Требование: Visual C++ Redistributable

Для запуска Neuro Modeler на целевой машине Windows необходим **Microsoft Visual C++ 2015–2022 Redistributable (x64)**.

- Сборка с пресетом **localqt** (Qt 5.15.2 из `C:\Qt\5.15.2\msvc2019_64`) соответствует инструменту **VS2019**; на целевой машине должен быть установлен пакет, содержащий runtime 14.28.x.
- Рекомендуется установить официальный пакет «Visual C++ 2015–2022 Redistributable (x64)» с сайта Microsoft.
- Ссылка на загрузку: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

**Важно:** для сборки под развёртывание с локальным Qt 5.15.2 (msvc2019_64) используйте **только** пресеты **win-vs2019-release-localqt** / **win-vs2019-debug-localqt**. Пресеты «VS2022 + локальный Qt 5.x» удалены: Qt 5.15.2 msvc2019_64 собран под VS2019 (v142), а проект под VS2022 — под v143; смешение CRT в одном процессе ведёт к падению на чистой Windows (APPCRASH в MSVCP140.dll). Исправление невозможно без перехода на VS2019 для всей сборки.

Для пресетов win-vs2019-*-localqt зависимости vcpkg (curl, boost, glog и т.д.) собираются с **триплетом x64-windows-v142** (инструмент VS2019, v142), так что все DLL в `Bin\Platform\Win` используют один и тот же CRT (v142), как и Qt из C:\Qt.

---

## EN

## Requirement: Visual C++ Redistributable

Для runtime Neuro Modeler на target machine Windows is required **Microsoft Visual C++ 2015–2022 Redistributable (x64)**.

- Build с preset **localqt** (Qt 5.15.2 из `C:\Qt\5.15.2\msvc2019_64`) matches tool **VS2019**; на target machine must be installed package, containing runtime 14.28.x.
- Recommended set official package «Visual C++ 2015–2022 Redistributable (x64)» с site Microsoft.
- Link на download: https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist

**Important:** для build под deployment с local Qt 5.15.2 (msvc2019_64) use **only** presets **win-vs2019-release-localqt** / **win-vs2019-debug-localqt**. Presets «VS2022 + local Qt 5.x» removed: Qt 5.15.2 msvc2019_64 built под VS2019 (v142), а project под VS2022 — под v143; mixing CRT в one process leads к crash на clean Windows (APPCRASH в MSVCP140.dll). Fix impossible без transition на VS2019 для entire build.

Для presets win-vs2019-*-localqt dependencies vcpkg (curl, boost, glog и т.д.) are built с **triplet x64-windows-v142** (tool VS2019, v142), так what все DLL в `Bin\Platform\Win` use one и тот же CRT (v142), как и Qt из C:\Qt.

---
