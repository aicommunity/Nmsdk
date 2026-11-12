# Решение проблем с vcpkg и Qt Creator

## RU

## Проблема 1: boost-filesystem не собирается

**Ошибка:** `boost-filesystem:x64-windows failed with: BUILD_FAILED`

**Причина:** Проблема порядка сборки в vcpkg - `boost-filesystem` пытается собраться до того, как `boost-atomic` полностью собран.

**Решение:**
1. Подождите, пока vcpkg соберет все зависимости (может занять 30-60 минут)
2. Если ошибка повторяется, попробуйте:
   ```cmd
   cd E:\vcpkg
   vcpkg remove boost-filesystem:x64-windows
   vcpkg install boost-filesystem:x64-windows --triplet x64-windows
   ```

## Проблема 2: CMake не может найти Ninja

**Ошибка:** `CMake was unable to find a build program corresponding to "Ninja". CMAKE_MAKE_PROGRAM is not set.`

**Решение:**

### Вариант 1: Установить Ninja системно (рекомендуется)
1. Скачайте Ninja с https://github.com/ninja-build/ninja/releases
2. Распакуйте `ninja.exe` в директорию, которая есть в PATH (например, `C:\Windows\System32` или создайте `C:\Tools\ninja` и добавьте в PATH)
3. Или запустите `install-ninja.bat`

### Вариант 2: Использовать Visual Studio генератор
В Qt Creator выберите пресет `win-vs2022-debug` или `win-vs2022-release` вместо `win-msvc-debug/release`. Эти пресеты используют генератор Visual Studio, который не требует Ninja.

### Вариант 3: Указать путь к Ninja вручную
В Qt Creator:
1. Откройте настройки проекта (Projects)
2. В разделе Build Settings найдите "CMake Configuration"
3. Добавьте: `-DCMAKE_MAKE_PROGRAM=E:/vcpkg/downloads/tools/ninja-1.13.2-windows/ninja.exe`

## Проблема 3: atlmfc не найден

**Ошибка:** `Unable to locate 'afxres.h'. Ensure you have installed the ATL/MFC component of Visual Studio.`

**Решение:**
1. Откройте Visual Studio Installer
2. Нажмите "Изменить" для вашей установки Visual Studio
3. На вкладке "Отдельные компоненты" установите:
   - `C++ ATL для последней версии v143 build tools (x86 и x64)`
   - `C++ MFC для последней версии v143 build tools (x86 и x64)`
4. После установки перезапустите Qt Creator

## Рекомендации

1. **Используйте Visual Studio генератор** вместо Ninja - он не требует дополнительных инструментов
2. **Дождитесь завершения сборки всех пакетов vcpkg** - первый запуск может занять много времени
3. **Не прерывайте процесс сборки vcpkg** - это может привести к неконсистентному состоянию

---

## EN

## Issue 1: boost-filesystem fails to build

**Error:** `boost-filesystem:x64-windows failed with: BUILD_FAILED`

**Cause:** vcpkg build order issue — `boost-filesystem` tries to build before `boost-atomic` is fully built.

**Solution:**
1. Wait for vcpkg to build all dependencies (may take 30–60 minutes)
2. If the error repeats, try:
   ```cmd
   cd E:\vcpkg
   vcpkg remove boost-filesystem:x64-windows
   vcpkg install boost-filesystem:x64-windows --triplet x64-windows
   ```

## Issue 2: CMake cannot find Ninja

**Error:** `CMake was unable to find a build program corresponding to "Ninja". CMAKE_MAKE_PROGRAM is not set.`

**Solution:**

### Option 1: Install Ninja system-wide (recommended)
1. Download Ninja from https://github.com/ninja-build/ninja/releases
2. Extract `ninja.exe` to a directory on PATH (e.g. `C:\Windows\System32` or create `C:\Tools\ninja` and add to PATH)
3. Or run `install-ninja.bat`

### Option 2: Use Visual Studio generator
In Qt Creator, choose preset `win-vs2022-debug` or `win-vs2022-release` instead of `win-msvc-debug/release`. These presets use the Visual Studio generator and do not require Ninja.

### Option 3: Specify Ninja path manually
In Qt Creator:
1. Open project settings (Projects)
2. In Build Settings, find "CMake Configuration"
3. Add: `-DCMAKE_MAKE_PROGRAM=E:/vcpkg/downloads/tools/ninja-1.13.2-windows/ninja.exe`

## Issue 3: atlmfc not found

**Error:** `Unable to locate 'afxres.h'. Ensure you have installed the ATL/MFC component of Visual Studio.`

**Solution:**
1. Open Visual Studio Installer
2. Click "Modify" for your Visual Studio installation
3. On the "Individual components" tab, install:
   - `C++ ATL for latest v143 build tools (x86 & x64)`
   - `C++ MFC for latest v143 build tools (x86 & x64)`
4. Restart Qt Creator after installation

## Recommendations

1. **Use the Visual Studio generator** instead of Ninja — no extra tools required
2. **Wait for vcpkg to finish building all packages** — first run can take a long time
3. **Do not interrupt vcpkg build** — may leave an inconsistent state
