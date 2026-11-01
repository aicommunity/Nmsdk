# A0. Подготовка окружения и сборка baseline

**Цель:** на каждом сервере получить отдельный чистый checkout baseline, собрать Release Console и unit-тесты, записать provenance.
**Уровень:** слабый агент. **Время:** 1–2 ч (в основном сборка). **Console:** 0.

## Предусловия

- Linux, `git`, `cmake ≥ 3.21`, `gcc/g++` (C++20), `make`, `python3 ≥ 3.8`, `numpy`, `tmux`. Зависимости сборки (Qt5/Qt6 dev, Boost, glog, curl dev) уже стоят на `.17` и `.11`: там Console собиралась раньше.
- Доступ к GitHub `aicommunity/*` (по SSH-ключу сервера или по HTTPS).

Проверка инструментов:

```bash
for t in git cmake gcc g++ make python3 tmux sha256sum; do printf '%-10s ' $t; command -v $t || echo MISSING; done
cmake --version | head -1; python3 -c "import numpy; print('numpy', numpy.__version__)"
```

**Ожидаемо:** нет строк `MISSING`, cmake ≥ 3.21, numpy импортируется. Если numpy нет, попробуй `python3 -m pip install --user numpy`. Если и это не помогло, задачи C1/C2/F1 на этом хосте не выполнять и записать это в отчёт.

## Шаги

### 1. Каталоги данных

```bash
export DATA="/media/user/Data/TLAgent-20261020"   # на .11: выбрать диск с ≥ 200 ГБ, путь записать в отчёт
mkdir -p "$DATA/runs" "$DATA/agent-reports" "$DATA/bisect" "$DATA/scratch"
df -h "$DATA" | tail -1
```

**Ожидаемо:** свободно ≥ 200 ГБ. Если меньше — СТОП.

### 2. Клон baseline (отдельный от рабочих папок людей)

```bash
mkdir -p "$HOME/tl-agent" && cd "$HOME/tl-agent"
test -e Nmsdk && { echo "Nmsdk already exists: STOP, ask human"; exit 1; }
git clone https://github.com/aicommunity/Nmsdk.git Nmsdk
cd Nmsdk
git fetch origin timelearner_fix
git checkout --detach 03c8cb912748a7a9df9f6cf19eca092489a16ebc
# если на сервере нет SSH-ключа GitHub, перевести URL сабмодулей на HTTPS (только локальный конфиг):
git config --file .gitmodules --get-regexp url | while read k u; do n=${k#submodule.}; n=${n%.url}; \
  git config "submodule.$n.url" "$(echo "$u" | sed 's#git@github.com:#https://github.com/#')"; done
git submodule update --init
git submodule status
```

**Ожидаемо** в `git submodule status` (первые символы SHA):

```
 e75092633c… Bin
 d52dc1ca15… Libraries/Nmsdk-PulseLib
 b3b2472dc3… Rdk
```

Перед SHA не должно быть `+` или `-`. Если хоть один не совпал — СТОП.

Если пакет плана ещё не в репозитории, скопируй его: `cp -r <пакет> "$NMSDK/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20"`. Это единственная разрешённая правка дерева, и она не трекается. В отчёте укажи «пакет плана скопирован вручную».

### 3. Сборка Release

```bash
export NMSDK="$HOME/tl-agent/Nmsdk"; cd "$NMSDK"
cmake --preset linux-gcc-release-local > "$DATA/scratch/A0_configure.log" 2>&1; echo "configure rc=$?"
cmake --build build/linux-gcc-release-local --target Nmsdk-PulseLib.core NeuroModelerConsole Test_PulseLib_StorageComponents \
  -j"$(nproc)" > "$DATA/scratch/A0_build.log" 2>&1; echo "build rc=$?"
ls -la Bin/Platform/Linux/NeuroModelerConsole
grep -m1 CMAKE_BUILD_TYPE build/linux-gcc-release-local/CMakeCache.txt
```

**Ожидаемо:** `configure rc=0`, `build rc=0`, файл Console существует, `CMAKE_BUILD_TYPE:STRING=Release`. При ошибке приложи последние 60 строк `A0_build.log` — СТОП.

### 4. Unit-тесты (без экспериментов)

```bash
cd "$NMSDK"
ctest --test-dir build/linux-gcc-release-local -R PulseLib_StorageComponents --output-on-failure > "$DATA/scratch/A0_ctest.log" 2>&1; echo "ctest rc=$?"
tail -5 "$DATA/scratch/A0_ctest.log"
cd "$NMSDK/Bin/Configs/SpikeSamples/StructTrain/scripts"
python3 -m unittest tests.test_softcold_fix_unit test_timelearner_matrix > "$DATA/scratch/A0_pytest.log" 2>&1; echo "py rc=$?"; tail -3 "$DATA/scratch/A0_pytest.log"
```

**Ожидаемо:** `ctest rc=0`. Python-тесты: записать итог («Ran N tests … OK/FAILED (errors=k)»). Если что-то упало, это допустимо только при совпадении с другим хостом; в отчёте перечисли имена упавших тестов.

### 5. Smoke Console без расчёта

```bash
"$NMSDK/Bin/Platform/Linux/NeuroModelerConsole" --help > "$DATA/scratch/A0_console_help.txt" 2>&1; echo "rc=$?"; head -20 "$DATA/scratch/A0_console_help.txt"
ldd "$NMSDK/Bin/Platform/Linux/NeuroModelerConsole" | grep -c "not found"
```

**Ожидаемо:** справка печатается (rc 0 или 1 — записать), `ldd … not found` = `0`.

### 6. Provenance и инструменты пакета

```bash
export PLAN="$NMSDK/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20"; export TOOLS="$PLAN/tools"
mkdir -p "$DATA/agent-reports/A0_$(hostname)"
bash "$TOOLS/provenance.sh" "$NMSDK" | tee "$DATA/agent-reports/A0_$(hostname)/provenance.txt"
cd "$TOOLS/cable_model" && gcc -O2 -o cable cable.c -lm && gcc -O2 -o cable2 cable2.c -lm && echo cable_ok
python3 -c "import sys; sys.path.insert(0,'$TOOLS/cable_model'); import library, numpy as np; \
k=library.sim(1,[(1,8.6e7,[0.0])],0.01,0.005,0.3,f=2000,Rm=1e7,sub=1); print('L1 peak', round(float(np.max(k)),6))"
```

**Ожидаемо:** `L1 peak 0.015781` (±0.000005). Это значение совпадает с `InitialSomaPotential` W04 из Console. `provenance.txt` показывает `dirty=0` для `.`, `Bin`, `Libraries/Nmsdk-PulseLib`. Пакет плана, скопированный вручную, даёт `dirty≥1` для root — это нормально, отметить в отчёте.

### 7. Файл окружения для всех карточек

```bash
cat > "$HOME/tl-agent/env.sh" <<EOF
export NMSDK="$HOME/tl-agent/Nmsdk"
export PLAN="\$NMSDK/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20"
export TOOLS="\$PLAN/tools"
export CABLE="\$TOOLS/cable_model"
export ST="\$NMSDK/Bin/Configs/SpikeSamples/StructTrain"
export DATA="$DATA"
export TIMELEARNER_MATRIX_RUNS_ROOT="\$DATA/runs"
export REPORTS="\$DATA/agent-reports"
export HOSTTAG="$(hostname -I | awk '{print $1}' | awk -F. '{print $4}')"
export A0_CONSOLE_SHA256="$(sha256sum "$HOME/tl-agent/Nmsdk/Bin/Platform/Linux/NeuroModelerConsole" | cut -d' ' -f1)"
mkid() { echo "\$1-\$HOSTTAG-\$(date -u +%Y%m%dT%H%MZ)-\$RANDOM"; }
EOF
source "$HOME/tl-agent/env.sh"; echo "$NMSDK $ST $HOSTTAG $A0_CONSOLE_SHA256"; mkid TEST
```

**Ожидаемо:** пути печатаются, `HOSTTAG` — последний октет IP (`17` или `11`), `mkid TEST` печатает строку вида `TEST-17-20261021T0900Z-12345`. Каждая карточка начинается с `source "$HOME/tl-agent/env.sh"`.

### 8. Обновить манифесты входов матрицы (обязательно, иначе очередь не стартует)

На Bin `e7509263` файл `TimeLearnerMatrix/matrix.json` изменён 19.10 (добавлена W48) уже после того, как были записаны манифесты входов. Поэтому `--prepare` любой волны падает с `matrix definition differs beyond line endings`; при подготовке пакета это проверено на W09 и W10. `--refresh` переписывает только `matrix_input_manifest.json`: при подготовке проверено на 17 волнах, файлы Train/Test не меняются. Делаем это на **локальной** ветке Bin:

```bash
source "$HOME/tl-agent/env.sh"; cd "$NMSDK/Bin"
git checkout -b agent/tl-audit-20261020          # от e7509263; ветку не пушить
bash "$TOOLS/refresh_waves.sh" "$ST" W01 W02 W04 W05 W09 W10 W11 W12 W13 W16 W21 W29 W31 W33 W35 W46 W47 \
  | tee "$REPORTS/A0_$(hostname)/refresh.txt"
git -C "$NMSDK/Bin" log -1 --format='%H %s'
```

**Ожидаемо:** для каждой волны `rc=0 … other_files_changed=0`. Для W10 `new_case_dirs=[TimeLearnerMatrix/W10/inputs/W10_HIST_br100_gen/]` — это новый зарегистрированный случай, так и должно быть. В конце печатается `refresh commit <sha>`; этот SHA записать в `result.json` как `bin_refresh_commit`. Любой `STOP:` — СТОП всей задачи A0.

В корне после этого `git status` показывает `modified: Bin (new commits)`. Это ожидаемо, корень не коммитить.

Внутренняя защита очереди: при свободном месте меньше 50 ГБ на диске `TIMELEARNER_MATRIX_RUNS_ROOT` worker останавливается с `HARD STOP Avail=… < 50G`. Это не ошибка обучения.

## Выход

`$REPORTS/A0_<hostname>/`: `provenance.txt`, `REPORT.md`, `result.json` с полями `console_sha256`, `build_type`, `ctest_rc`, `py_tests_summary`, `cable_L1_peak`, `bin_refresh_commit`.

## Готово, когда

Все шаги 1–6 дали «Ожидаемо». `console_sha256` записан. Дальнейшие карточки сверяют свой Console с этим SHA.
