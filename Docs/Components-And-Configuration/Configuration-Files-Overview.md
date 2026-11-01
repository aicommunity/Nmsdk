# Обзор конфигурационных файлов (Configuration Files Overview)

## RU

### Обзор

**Примечание:** Детальная информация о работе с конфигурациями через классы Rdk (UProject, UApplication, UXMLEnvSerialize, UProjectDeployer) находится в [Rdk/Docs/Configuration-Management.md](../../Rdk/Docs/Configuration-Management.md).

Конфигурационные файлы в `Bin/Configs/` используются для настройки проектов, компонентов и приложения.

### Типы конфигурационных файлов

- **XML** - основной формат для проектов и компонентов
- **INI** - конфигурационные файлы приложения
- **JSON** - для некоторых настроек (стили, темы)

### Структура конфигураций

Конфигурации проектов содержат:
- Описание компонентов
- Параметры компонентов
- Соединения между компонентами
- Настройки выполнения

### См. также

- [Bin/Docs](../../Bin/Docs/) - детальная документация по конфигурациям
- [Component System](Component-System.md)

---

## EN

### Overview

Configuration files in `Bin/Configs/` are used to configure projects, components, and the application.

### Configuration File Types

- **XML** - main format for projects and components
- **INI** - application configuration files
- **JSON** - for some settings (styles, themes)

### Configuration Structure

Project configurations contain:
- Component descriptions
- Component parameters
- Connections between components
- Execution settings

### See Also

- [Rdk/Docs/Configuration-Management.md](../../Rdk/Docs/Configuration-Management.md) - detailed information about working with configurations through Rdk classes (UProject, UApplication, UXMLEnvSerialize, UProjectDeployer)
- [Bin/Docs/Configs-Structure.md](../../Bin/Docs/Configs-Structure.md) - configuration file structure in Bin
- [Bin/Docs](../../Bin/Docs/) - resources and configurations documentation
- [Component System](Component-System.md)
