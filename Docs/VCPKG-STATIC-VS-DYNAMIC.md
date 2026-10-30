# Статическая и динамическая линковка зависимостей vcpkg (Boost, curl и др.)

## RU

## Текущее состояние (всё динамически)

- В проекте используется **динамическая** линковка зависимостей vcpkg: triplet `x64-windows` (VS2022) и `x64-windows-v142` (VS2019, overlay).
- Boost, libcurl, glog, opencv, python3, zlib и транзитивные зависимости поставляются как **DLL**; они копируются в `Bin\Platform\Win` скриптом `DeployVcpkgDlls.cmake`.
- Qt остаётся shared (DLL): из C:\Qt или из vcpkg.

## Можно ли собрать Boost и libcurl (и др.) статически?

Да. В vcpkg для этого используется triplet со статической линковкой библиотек и **динамическим CRT** (рекомендуемый вариант для развёртывания под Windows):

- **VCPKG_LIBRARY_LINKAGE** = `static` — библиотеки (boost, curl, zlib, glog и т.д.) собираются как `.lib` и линкуются в exe.
- **VCPKG_CRT_LINKAGE** = `dynamic` — CRT по-прежнему через `/MD` (DLL), совместимо с Qt и с VC++ Redistributable.

Стандартный triplet vcpkg: **x64-windows-static-md** (его можно взять за основу для overlay).

---

## EN

## Current state (всё dynamically)

- В in the project is used **dynamic** linking dependencies vcpkg: triplet `x64-windows` (VS2022) и `x64-windows-v142` (VS2019, overlay).
- Boost, libcurl, glog, opencv, python3, zlib и transitive dependencies are delivered как **DLL**; они are copied в `Bin\Platform\Win` script `DeployVcpkgDlls.cmake`.
- Qt remains shared (DLL): из C:\Qt или из vcpkg.

## Can ли build Boost и libcurl (etc.) statically?

Да. В vcpkg для this is used triplet со static linking libraries и **dynamicallyм CRT** (recommended option для deployment под Windows):

- **VCPKG_LIBRARY_LINKAGE** = `static` — library (boost, curl, zlib, glog и т.д.) are built как `.lib` и are linked в exe.
- **VCPKG_CRT_LINKAGE** = `dynamic` — CRT по-still via `/MD` (DLL), compatible с Qt и с VC++ Redistributable.

Standard triplet vcpkg: **x64-windows-static-md** (его can take за basis для overlay).

---
