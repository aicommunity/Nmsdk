# E1. Диагностические флаги C++ (F1, F7, F8, Branch EstDelayPerSegInit)

**Цель:** собрать Console с четырьмя новыми свойствами тренеров. Значения по умолчанию воспроизводят `d52dc1c` бит в бит, а включаются флаги через `--train-param` (E0) только в копии Train.
**Уровень:** средний. **Хост:** любой (сборка). **Console:** 0. **Время:** 1–2 ч.
**Зависит от:** A0.

| Свойство | Тренеры | По умолчанию | Что делает |
|---|---|---|---|
| `UseSignedDelayEstimate` | оба | 0 | F1 (A2): уточнение `EstDelayPerSeg = 0.7·est + 0.3·(prev_dt − dt)/ΔL` со знаком. Работает и при перескоке (смене знака dt); Branch — и при укорочении |
| `RminLengthTolFactor` | оба | 4.0 | F7 (A3): заменяет `constexpr kRminLengthTolFactor`. Значение 1 убирает расширение допуска при TipR@Rmin/Rmax |
| `FreezeSynapseResistanceBase` | оба | 0 | F8 (A14): `MeasureMaxPotentialAndTime` больше не переписывает `SynapseResistanceBase` |
| `EstDelayPerSegInit` | Branch | 0 | стартовая оценка задержки на сегмент; при 0 — `kDelayPerSegDefault` (= 0.005). Физически ≈ Rm·C = 0.01 для C = 1e-9 |

Все четыре значения печатаются в строке параметров C++-аудита (`;use_signed_delay_estimate=…;rmin_length_tol_factor=…;freeze_synapse_resistance_base=…`), чтобы по логу было видно, что Console их прочитал.

## Шаги

Отдельный checkout для E1 (основной `$NMSDK` остаётся baseline):

```bash
source "$HOME/tl-agent/env.sh"
export NMSDK_E1="$HOME/tl-agent/Nmsdk-e1"; test -e "$NMSDK_E1" && { echo "exists: STOP"; exit 1; }
git clone -q "$NMSDK" "$NMSDK_E1" && cd "$NMSDK_E1"
for p in $(git config --file .gitmodules --get-regexp path | awk '{print $2}'); do git config "submodule.$p.url" "$NMSDK/$p"; done
git -c protocol.file.allow=always submodule update --init -q
git -C Bin checkout -q --detach "$(git -C "$NMSDK/Bin" rev-parse HEAD)"      # та же Bin, что в основном checkout (с E0/B1)
cd Libraries/Nmsdk-PulseLib && git checkout -q -b agent/audit-flags-20261020 d52dc1ca15d1c698f70924f2307a738ccd3073b3
git apply --check "$PLAN/patches/pulselib_audit_flags_F1_F7_F8.patch" && git apply "$PLAN/patches/pulselib_audit_flags_F1_F7_F8.patch"
git diff --stat
git -c user.name=tl-agent -c user.email=tl-agent@localhost commit -qam "feat(TimeLearner): audit diagnostic switches F1/F7/F8 + Branch EstDelayPerSegInit (defaults = d52dc1c) [AGENT_PLAN E1]"
cd "$NMSDK_E1" && git apply --check "$PLAN/patches/root_tests_audit_flags.patch" && git apply "$PLAN/patches/root_tests_audit_flags.patch"
```

**Ожидаемо:** `git diff --stat` — 4 файла (`NNeuronTimeLearner{,Branch}.{h,cpp}`), около 92 добавленных строк.

Сборка и тесты:

```bash
cd "$NMSDK_E1"
cmake --preset linux-gcc-release-local > "$DATA/scratch/E1_configure.log" 2>&1 && \
cmake --build build/linux-gcc-release-local --target NeuroModelerConsole Test_PulseLib_StorageComponents -j"$(nproc)" \
  > "$DATA/scratch/E1_build.log" 2>&1; echo "build rc=$?"
grep -E "error|warning: .*(RminLengthTolFactor|UseSignedDelayEstimate|FreezeSynapseResistanceBase|EstDelayPerSegInit)" "$DATA/scratch/E1_build.log" | head
ctest --test-dir build/linux-gcc-release-local -R PulseLib_StorageComponents --output-on-failure > "$DATA/scratch/E1_ctest.log" 2>&1; echo "ctest rc=$?"
"$NMSDK_E1/Bin/Platform/Linux/Test_PulseLib_StorageComponents" --gtest_filter='TimeLearnerAuditFlags20261020Test.*' | tail -5
sha256sum "$NMSDK_E1/Bin/Platform/Linux/NeuroModelerConsole" | tee "$REPORTS/E1_console.sha256"
```

**Ожидаемо:** `build rc=0`; `grep` пуст (или только чужие предупреждения); `ctest rc=0`; фильтр `TimeLearnerAuditFlags20261020Test.*` — `[  PASSED  ] 3 tests`. SHA Console отличается от `A0_CONSOLE_SHA256`.

Если сборка падает **внутри изменённых строк**, это СТОП. Приложить первые 30 строк ошибок; патч не исправлять. При подготовке он проверялся только `g++ -fsyntax-only` для двух `.cpp` и для новых тестов, без полной сборки.

## No-op проверка (обязательна до E2)

Флаги по умолчанию не должны менять поведение. Это проверяется в E2 (плечо E2-1 против A1/E2-0). До E2 Console из E1 для выводов не использовать.

## Выход

`E1_console.sha256`, SHA коммита PulseLib-ветки, логи сборки и тестов, `REPORT.md`, `result.json` (`console_sha256`, `pulselib_commit`, `ctest_rc`, `flag_tests_passed`).
