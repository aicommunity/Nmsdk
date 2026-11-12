# Optional / Deprecated ML Libraries

## RU

### Статус

Следующие библиотеки **не входят** в `.gitmodules` и **не checkout'нуты** в текущем дереве Nmsdk. Они упоминаются в legacy-конфигурации (`.pro`, `Libraries.h`) как опциональные зависимости.

| Библиотека | CMake / define | Статус |
|------------|----------------|--------|
| `Rdk-TensorflowLib` | `RDK_USE_TENSORFLOW` | Deprecated / optional — submodule absent |
| `Rdk-PyMachineLearningLib` | `RDK_USE_PYTHON` | Deprecated / optional — submodule absent |
| `Rdk-DarknetLib` | `RDK_USE_DARKNET` | Deprecated / optional — submodule absent |

### Активные библиотеки (в `.gitmodules`)

Используйте документацию:

- [Rdk-BasicLib](Rdk-BasicLib.md), [Rdk-CvBasicLib](Rdk-CvBasicLib.md) — подготовка данных
- [Nmsdk-PulseLib](Nmsdk-PulseLib.md) — SNN
- [Nmsdk-MotionControlLib](Nmsdk-MotionControlLib.md) — управление движением

### Legacy-ссылки в коде

- `Libraries/Libraries.h` — условные `#include` при `RDK_USE_PYTHON` / `RDK_USE_TENSORFLOW`
- `App/NeuroModeler/*.pro` — `NMSDK_LIBS_NAMES` для ML-библиотек

Включение ML-библиотек требует восстановления субмодулей и отдельного тикета на сборку. Документация по интеграции ML **не является активным путём** для новых проектов.

### См. также

- [Build System](../Build-And-Deploy/Build-System.md) — опции `RDK_USE_*`
- [Libraries Overview](Overview.md)

---

## EN

### Status

The libraries below are **not** listed in `.gitmodules` and are **not present** in the current Nmsdk tree. Legacy project files still reference them behind optional compile flags.

| Library | CMake / define | Status |
|---------|----------------|--------|
| `Rdk-TensorflowLib` | `RDK_USE_TENSORFLOW` | Deprecated / optional — submodule absent |
| `Rdk-PyMachineLearningLib` | `RDK_USE_PYTHON` | Deprecated / optional — submodule absent |
| `Rdk-DarknetLib` | `RDK_USE_DARKNET` | Deprecated / optional — submodule absent |

### Active libraries (in `.gitmodules`)

See [Libraries Overview](Overview.md) for supported component libraries.

### Legacy code references

- `Libraries/Libraries.h` — conditional includes
- `App/NeuroModeler/*.pro` — optional `NMSDK_LIBS_NAMES` entries

Restoring ML integration requires submodule restoration and a separate build task. **Do not** use ML library examples as the primary integration path for new work.
