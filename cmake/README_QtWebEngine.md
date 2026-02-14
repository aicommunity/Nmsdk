# Установка Qt5 WebEngine (Linux)

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
