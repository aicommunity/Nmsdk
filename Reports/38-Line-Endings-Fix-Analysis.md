# Анализ и исправление проблемы с окончаниями строк в сабмодуле Rdk

## Проблема

При редактировании файлов в сабмодуле Rdk из Windows, Git показывал файлы как полностью изменённые, хотя реальные изменения были только в нескольких местах.

### Причина проблемы

1. **Файлы в репозитории**: имеют окончания строк LF (Linux/Unix формат)
2. **Файлы в рабочей директории Windows**: автоматически конвертируются в CRLF (Windows формат)
3. **Git конфигурация**: `core.autocrlf = true` пытался автоматически конвертировать, но это не работало корректно для сабмодулей

### Доказательства проблемы

```bash
# Проверка окончаний строк в файлах
git ls-files --eol CMakeLists.txt GUI/Qt/UGEngineControlWidget.cpp

# Результат ДО исправления:
i/lf    w/crlf  attr/                 	CMakeLists.txt
i/lf    w/crlf  attr/                 	GUI/Qt/UGEngineControlWidget.cpp
```

Где:
- `i/lf` - файлы в индексе имеют LF
- `w/crlf` - файлы в рабочей директории имеют CRLF
- `attr/` - нет атрибутов для нормализации

### Масштаб проблемы

- **Файл**: `GUI/Qt/UGEngineControlWidget.cpp`
- **Реальные изменения**: 7 блоков изменений (hunks), 50 строк добавлено, 4 строки удалено
- **Показывалось Git**: весь файл как изменённый из-за различий в окончаниях строк

## Решение

### 1. Создан `.gitattributes` файл в Rdk

Файл `Rdk/.gitattributes` устанавливает правила нормализации окончаний строк:

```gitattributes
# Устанавливаем LF окончания строк для всех текстовых файлов
* text=auto eol=lf

# Явно указываем для исходных файлов C/C++
*.cpp text eol=lf
*.h text eol=lf
*.c text eol=lf
*.hpp text eol=lf
*.cc text eol=lf
*.cxx text eol=lf

# CMake файлы
CMakeLists.txt text eol=lf
*.cmake text eol=lf

# Другие текстовые файлы
*.txt text eol=lf
*.md text eol=lf
*.json text eol=lf
*.xml text eol=lf
*.pro text eol=lf
*.pri text eol=lf
*.ui text eol=lf
*.qrc text eol=lf

# Бинарные файлы
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.pdf binary
*.zip binary
*.exe binary
*.dll binary
*.so binary
*.a binary
*.lib binary
*.vsd binary
```

### 2. Настроен VS Code / Cursor

Обновлён файл `.vscode/settings.json`:

```json
{
  "cmake.configureOnOpen": false,
  "cmake.useCMakePresets": "always",
  "cmake.generator": "Ninja",
  "cmake.environment": {
    "VCPKG_ROOT": "${env:VCPKG_ROOT}"
  },
  "cmake.sourceDirectory": "${workspaceFolder}",
  "git.ignoreLimitWarning": true,
  "files.eol": "\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true,
  "editor.insertSpaces": true,
  "editor.detectIndentation": false,
  "editor.tabSize": 2
}
```

Ключевые настройки:
- `files.eol: "\n"` - использовать LF окончания строк
- `files.insertFinalNewline: true` - добавлять финальный перевод строки
- `files.trimTrailingWhitespace: true` - удалять пробелы в конце строк

### 3. Создан `.editorconfig`

Файл `.editorconfig` обеспечивает единообразие настроек редактора:

```ini
root = true

[*]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
indent_style = space
indent_size = 2

[*.{cpp,h,c,hpp,cc,cxx}]
indent_size = 2

[CMakeLists.txt]
indent_size = 2

[*.{json,xml}]
indent_size = 2

[*.md]
trim_trailing_whitespace = false
```

### 4. Настроен Git для сабмодуля Rdk

```bash
cd Rdk
git config core.autocrlf false
git config core.eol lf
```

## Результат

### После применения исправлений

```bash
# Проверка окончаний строк ПОСЛЕ исправления:
git ls-files --eol CMakeLists.txt GUI/Qt/UGEngineControlWidget.cpp

# Результат:
i/lf    w/crlf  attr/text eol=lf      	CMakeLists.txt
i/lf    w/crlf  attr/text eol=lf      	GUI/Qt/UGEngineControlWidget.cpp
```

Теперь:
- `i/lf` - файлы в индексе имеют LF ✅
- `w/crlf` - файлы в рабочей директории имеют CRLF (нормально для Windows)
- `attr/text eol=lf` - Git автоматически конвертирует CRLF → LF при коммите ✅

### Статистика изменений

```bash
git diff --cached --numstat

# Результат:
39	0	.gitattributes
5	0	CMakeLists.txt
50	4	GUI/Qt/UGEngineControlWidget.cpp
```

Теперь Git показывает только **реальные изменения кода**, а не весь файл из-за различий в окончаниях строк!

## Рекомендации

### Для разработчиков

1. **При работе в Windows**: редактор будет показывать CRLF в рабочей директории, но Git автоматически нормализует их в LF при коммите благодаря `.gitattributes`

2. **При работе в Linux**: файлы будут иметь LF как в рабочей директории, так и в репозитории

3. **При создании новых файлов**: редактор автоматически использует LF благодаря настройкам VS Code и `.editorconfig`

### Для IDE

- **VS Code / Cursor**: настройки применятся автоматически
- **Другие редакторы**: должны учитывать `.editorconfig` файл
- **Git**: будет использовать `.gitattributes` для нормализации

## Проверка работы

Чтобы убедиться, что всё работает правильно:

```bash
cd Rdk

# Проверить настройки Git
git config core.autocrlf
git config core.eol

# Проверить окончания строк в файлах
git ls-files --eol | Select-String -Pattern "CMakeLists.txt|UGEngineControlWidget.cpp"

# Проверить изменения (должны показываться только реальные изменения)
git diff --stat
```

## Заключение

Проблема решена путём:
1. ✅ Создания `.gitattributes` для нормализации окончаний строк
2. ✅ Настройки VS Code для использования LF
3. ✅ Создания `.editorconfig` для единообразия
4. ✅ Настройки Git конфигурации сабмодуля

Теперь Git будет показывать только реальные изменения кода, а не весь файл из-за различий в окончаниях строк между Linux и Windows.
