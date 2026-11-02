> Исторический снимок плана и команд от20.10.2026. Инструменты удалены из текущего дерева; их точные исходники: [Git snapshot](https://github.com/aicommunity/Nmsdk/tree/0c12a71757d4eb34412f043028f56edfa38ba974/Docs/Audit/TimeLearner-2026-09-26-review/plans/AGENT_PLAN_2026-10-20/tools). Действующий план и причины миграции: [реестр](../../../../../StructTrain/TimeLearner/PlanToolRetirement.ru.md). Старые команды не являются текущей инструкцией запуска.

# C2. Офлайн-таблица «модель нейрона × длина паттерна»

**Цель:** воспроизвести на сервере расчёт модели кабеля: длины физической синхронизации и предельный запас разделимости. Сделать это для четырёх моделей нейрона и пяти длин паттерна. Таблица задаёт ожидания для G1 и показывает, где пассивный кабель в принципе не может дать положительный запас.
**Уровень:** слабый. **Хост:** любой. **Console:** 0. **Время:** 15 мин.
**Зависит от:** A0 (numpy, `cable`).

## Шаги

```bash
source "$HOME/tl-agent/env.sh"
OUT="$REPORTS/C2_$(date -u +%Y%m%d)_$HOSTTAG"; mkdir -p "$OUT"; cd "$CABLE"
test -x ./cable || gcc -O2 -o cable cable.c -lm
: > "$OUT/sweep.jsonl"
for m in "0.01 0.005" "0.01 0.001" "0.0025 0.002" "0.00025 0.001"; do
  python3 sweep.py $m 25,50,100,200,480 | grep '^{' >> "$OUT/sweep.jsonl"
done
wc -l "$OUT/sweep.jsonl"
python3 "$TOOLS/compare_sweep.py" "$PLAN/cards/data/C2_expected_sweep.jsonl" "$OUT/sweep.jsonl" | tee "$OUT/compare.txt" | tail -3
python3 ideal_delay.py > "$OUT/ideal_delay.jsonl"; cat "$OUT/ideal_delay.jsonl"
```

**Ожидаемо:** 20 строк, `C2_MATCH`. В `ideal_delay.jsonl` для τ = 0.25 мс запас равен 0.1158 (25 мс), 0.2044 (50 мс), 0.2446 (100 мс), 0.2499 (200 мс), 0.25 (480 мс).

## Как читать (вставить в отчёт таблицу)

| Поле | Смысл |
|---|---|
| `L` | длины 4 дендритов, при которых пики синхронны (Classic, отвод на кончике) |
| `fwhm_over_S` | ширина EPSP самого длинного дендрита / длина паттерна |
| `m_equal`, `m_ampnorm`, `m_oracle` | запас (tgt − max foil)/tgt при равных Rs, при выравнивании амплитуд, при оптимальном переборе длин; > 0 — разделимо |
| `feasible=false` | нужна длина > 100 сегментов (MaxL) |

Ожидаемый вывод, который нужно подтвердить: для пассивного кабеля с τ = 10 мс `m_oracle` ≤ 0 на всех длинах. Положительный запас (> 0.1) даёт только «быстрый EPSP + точная задержка» (`ideal_delay`). Если на сервере это не так, записать `C2_DIFF` и приложить `compare.txt`.

## Выход

`sweep.jsonl`, `compare.txt`, `ideal_delay.jsonl`, `REPORT.md`, `result.json`.
