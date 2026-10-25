# E2. A/B на регрессионном наборе R8: baseline, патчи скриптов, Console E1

**Цель:** доказать (или опровергнуть), что (a) патчи Bin B1+E0 не меняют результаты, и (b) Console E1 с флагами по умолчанию даёт те же результаты, что baseline. Заодно получить разброс трёх повторов на каждом случае. Без зелёного E2 выводы D2b не принимаются.
**Уровень:** слабый. **Хост:** `.17` (до 12 Console). **Время:** 2–4 дня машинного времени.
**Зависит от:** A0, A1, B1, E0, E1.

## R8

| Wave | Cases (в одном вызове) |
|---|---|
| W10 | `W10_HIST_br25_nextseg W10_HIST_br50_preinh W10_HIST_br100_preinh W10_HIST_br25_gen W10_HIST_br25_preinh` |
| W01 | `W01_CL50_N0_PSIoff` |
| W02 | `W02_CL480_N1_PSIoff` |
| W04 | `W04_BR100_N1_PSIoff` |

## Плечи

| Плечо | Источник checkout | Bin | PulseLib | Console |
|---|---|---|---|---|
| S0 | `$HOME/tl-agent/Nmsdk-s0` | `bin_refresh_commit` (без B1/E0) | `d52dc1c` | A0 |
| S1 | `$NMSDK` | с B1+E0 | `d52dc1c` | A0 |
| S2 | `$NMSDK_E1` | с B1+E0 | `agent/audit-flags-20261020` | E1 |

Создать источник S0 (один раз):

```bash
source "$HOME/tl-agent/env.sh"; S0="$HOME/tl-agent/Nmsdk-s0"; test -e "$S0" && echo "exists (ok, reuse)" || {
  git clone -q "$NMSDK" "$S0" && cd "$S0"
  for p in $(git config --file .gitmodules --get-regexp path | awk '{print $2}'); do git config "submodule.$p.url" "$NMSDK/$p"; done
  git -c protocol.file.allow=always submodule update --init -q
  git -C Bin checkout -q --detach <bin_refresh_commit из A0>; }
git -C "$S0/Bin" log -1 --format='%h %s'
```

## Запуск (12 серий: 3 плеча × 4 волны, по 3 повтора)

```bash
source "$HOME/tl-agent/env.sh"; export NMSDK_E1="$HOME/tl-agent/Nmsdk-e1"; S0="$HOME/tl-agent/Nmsdk-s0"
C0="$NMSDK/Bin/Platform/Linux/NeuroModelerConsole"; C2="$NMSDK_E1/Bin/Platform/Linux/NeuroModelerConsole"
series() { # arm src console wave jobs cases...
  arm=$1 src=$2 cons=$3 wave=$4 jobs=$5; shift 5
  tmux new-session -d -s "drv-E2-$arm-$wave" "source $HOME/tl-agent/env.sh; export NMSDK='$src' NMSDK_CONSOLE='$cons' HOST_LIMIT=12; \
    bash $TOOLS/run_series.sh e2-$arm-$wave E2.$arm.$wave $wave '$*' $jobs 3 > $REPORTS/drv-E2-$arm-$wave.log 2>&1"; }
for arm in S0 S1 S2; do
  case $arm in S0) src="$S0"; cons="$C0";; S1) src="$NMSDK"; cons="$C0";; S2) src="$NMSDK_E1"; cons="$C2";; esac
  series $arm "$src" "$cons" W10 5 W10_HIST_br25_nextseg W10_HIST_br50_preinh W10_HIST_br100_preinh W10_HIST_br25_gen W10_HIST_br25_preinh
  series $arm "$src" "$cons" W01 1 W01_CL50_N0_PSIoff
  series $arm "$src" "$cons" W02 1 W02_CL480_N1_PSIoff
  series $arm "$src" "$cons" W04 1 W04_BR100_N1_PSIoff
done
sleep 600; tmux ls | grep -c drv-E2; tail -n1 "$REPORTS"/drv-E2-*.log
```

`launch_queue.sh` внутри серии ждёт, пока Console на хосте станет ≤ 12 − jobs. Серии сами выстроятся в очередь. Если `pgrep -c NeuroModelerConsole` больше 12 дольше 10 минут, это СТОП: останови новые серии (`tmux kill-session -t drv-E2-…`), но работающие Console не трогай.

Проверка, что S2 действительно Console E1: в рабочих копиях S2 есть строка аудита `use_signed_delay_estimate=0;rmin_length_tol_factor=4`. В S0/S1 её быть не должно:

```bash
for w in $(ls -d "$TIMELEARNER_MATRIX_RUNS_ROOT"/*_work); do printf '%s ' "$w"; grep -rhoa 'use_signed_delay_estimate=[01];rmin_length_tol_factor=[0-9.]*' "$w" | head -1; echo; done | tail -30
```

## Сводка и критерии

Собрать таблицу case × плечо × повтор: `training_convergence`, `fires`, `separation_quality`, `DendriteLength`, `TipSynapseResistance`, `FixedLTZThreshold`. Для каждого случая и пары плеч (S0↔S1, S1↔S2):

- **EQUIVALENT** — в каждом повторе одинаковы категории `training_convergence` и `separation_quality` и `fires`; для сошедшихся `DendriteLength` совпадает, `FixedLTZThreshold` в пределах 1%;
- **EQUIVALENT_WITHIN_NOISE** — расхождения есть, но такие же встречаются между повторами одного плеча;
- **DIFFERENT** — иначе.

Ожидаемо: S1↔S2 — `EQUIVALENT`, поскольку флаги по умолчанию — no-op. S0↔S1 — `EQUIVALENT`, если гипотеза H-A15b (B1) неверна. **Любое DIFFERENT в S1↔S2 — СТОП для D2b и G1:** E1 не no-op, нужен разбор senior. DIFFERENT в S0↔S1 — важная находка: SoftCold-проводка влияет на обучение. Её нужно сразу сообщить человеку.

Разброс повторов (S0) записать отдельно: это шум, относительно которого оцениваются все остальные эффекты.

## Выход

`$REPORTS/E2/*/summary.tsv`, сводная таблица `E2_matrix.tsv`, вердикты пар, `REPORT.md`, `result.json`.
