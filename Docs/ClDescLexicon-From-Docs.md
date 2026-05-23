# Построение лексикона ClDesc из документации библиотек

Краткая инструкция по заполнению и обновлению описаний компонентов в **ClDesc** (XML в `Bin/ClDesc/`) с использованием документации из папок `Libraries/*/Docs/Components/`.

## Шаг 1 — построение лексикона из документации

Скрипт `Scripts/build_cl_desc_lexicon_from_docs.py` обходит документацию компонентов в библиотеках:

- **Rdk-CvBasicLib**
- **Nmsdk-PulseLib**
- **Nmsdk-MotionControlLib**
- **Rdk-HardwareLib**
- **Rdk-BasicLib**

и извлекает из Markdown-файлов краткий заголовок (Header) и описание (Description) для каждого класса. Результат записывается в JSON-лексикон, который использует NeuroModelerConsole при генерации ClDesc.

**Запуск** (из корня репозитория `Nmsdk`):

```bash
python Scripts/build_cl_desc_lexicon_from_docs.py
```

**Опции:**

| Опция | Описание |
|-------|----------|
| `-o`, `--output PATH` | Путь к выходному JSON (по умолчанию: `Docs/ClDescLexicon.json`) |
| `--no-merge` | Полностью перезаписать лексикон; по умолчанию существующий файл дополняется (секции `tokens`, `propertyFallbacks` не затираются) |
| `-v`, `--verbose` | Выводить список обработанных классов и файлов |

**Примеры:**

```bash
python Scripts/build_cl_desc_lexicon_from_docs.py -o Docs/ClDescLexicon.json --verbose
python Scripts/build_cl_desc_lexicon_from_docs.py --no-merge
```

**Результат:** файл `Docs/ClDescLexicon.json` с секцией `classOverrides`, готовый для ClDescGenerator.

## Шаг 2 — генерация ClDesc с использованием лексикона

После построения лексикона запустите утилиту **NeuroModelerConsole** с задачей генерации описаний классов и путём к лексикону:

```bash
NeuroModelerConsole -g -l Docs/ClDescLexicon.json
```

или коротко:

```bash
NeuroModelerConsole --generate-cldesc --cldesc-lexicon Docs/ClDescLexicon.json
```

Если лексикон уже лежит в `Docs/ClDescLexicon.json`, генератор по умолчанию подхватит его:

```bash
NeuroModelerConsole -g
```

Чтобы принудительно перезаписать уже заполненные заголовки и описания в ClDesc из лексикона:

```bash
NeuroModelerConsole -g -l Docs/ClDescLexicon.json -F
```

(флаг `-F` / `--cldesc-force`).

**Итог:** обновлённые XML-файлы в `Bin/ClDesc/<Library>/ru-RU/<ClassName>.xml` с расширенными Header и Description из документации библиотек.

## Рекомендуемый порядок

1. Выполнить **шаг 1** (скрипт) — построить или обновить `Docs/ClDescLexicon.json`.
2. Выполнить **шаг 2** (NeuroModelerConsole) — сгенерировать ClDesc с новым лексиконом.

## Примечания

- Для **Rdk-CvBasicLib** используется явный маппинг имён класса в Storage и имени в документации (например, класс в Storage — `Pipeline`, в документации — `UBPipeline`); маппинг задан в скрипте.
- В остальных библиотеках имя класса совпадает с именем файла документации без расширения (например, `NManipulator.md` → класс `NManipulator`).
- Подробнее о формате лексикона и генерации ClDesc см. [PropertyAliasGeneration.md](PropertyAliasGeneration.md).
