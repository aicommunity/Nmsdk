# Установка Qt5 WebEngine (Linux)

## RU

Для рендеринга Markdown и Mermaid-диаграмм в описаниях конфигураций NeuroModeler использует **Qt5 WebEngine**. Без него описание показывается через встроенный в Qt рендеринг Markdown (без Mermaid).

## Debian / Ubuntu

Установите пакет с заголовками и библиотеками:

```bash
sudo apt update
sudo apt install qtwebengine5-dev
```

Или только runtime (если Qt уже собран с WebEngine):

```bash
sudo apt install libqt5webenginewidgets5
```

Для разработки и сборки через CMake нужен именно **qtwebengine5-dev** — в нём есть `Qt5WebEngineWidgetsConfig.cmake`.

## Проверка

После установки пересоберите проект:

```bash
cd /path/to/Nmsdk
rm -rf build
cmake -B build -S . -G "Unix Makefiles"
```

В логе не должно быть ошибки про `Qt5WebEngineWidgets`. Приложение соберётся с поддержкой WebEngine, и в окне описания конфигурации будут отображаться Mermaid-диаграммы из README.md.

---

## EN

NeuroModeler uses **Qt5 WebEngine** to render Markdown and Mermaid diagrams in configuration descriptions. Without it, descriptions use Qt's built-in Markdown renderer (no Mermaid).

## Debian / Ubuntu

Install headers and libraries:

```bash
sudo apt update
sudo apt install qtwebengine5-dev
```

Or runtime only (if Qt was already built with WebEngine):

```bash
sudo apt install libqt5webenginewidgets5
```

For development and CMake builds you need **qtwebengine5-dev** — it includes `Qt5WebEngineWidgetsConfig.cmake`.

## Verification

After install, rebuild the project:

```bash
cd /path/to/Nmsdk
rm -rf build
cmake -B build -S . -G "Unix Makefiles"
```

The log should not show a `Qt5WebEngineWidgets` error. The app will build with WebEngine support, and Mermaid diagrams from README.md will render in the configuration description window.
