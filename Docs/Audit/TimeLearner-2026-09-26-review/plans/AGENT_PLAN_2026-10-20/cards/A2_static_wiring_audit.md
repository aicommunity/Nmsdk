# A2. Статический аудит проводки входов матрицы (дефект A15)

**Цель:** независимо подтвердить, что 45 Test-входов матрицы содержат повреждённую проводку. Тогда результаты этих случаев нельзя сравнивать с остальными.
**Уровень:** слабый. **Хост:** любой. **Console:** 0. **Время:** 10 мин.
**Зависит от:** A0.

## Что проверяется

`tools/check_model_wiring.py` для каждого `Model_00.xml` проверяет:

1. каждый `ExcSynapse*`/`InhSynapse*` подключён (`SynapticInputs`) ровно к одному каналу, и канал лежит в той же мембране (`synapse_fanout` — нарушение);
2. у `DatasetMatrix.Generator1` нет повторных связей (`generator_duplicate_link`);
3. Classic: ровно один отвод генератора на дендрит (`classic_multi_tap`), и он совпадает с `DendriteLength` из `Parameters_00.xml` (`taps_ne_DendriteLength`).

Происхождение дефекта: Bin-функция `repro_cold_lib.fix_generator_tip_links` переписывает **все** строки `…DendriteK_N.(Exc|Inh)Synapse`, включая `<Item>` связей синапс → собственный канал. Тогда синапс кончика начинает возбуждать все сегменты дендрита. Применение этой функции к чистой модели Bin `dfbfea63` побайтно даёт повреждённую модель `33abcb2b`.

## Шаги

```bash
source "$HOME/tl-agent/env.sh"
OUT="$REPORTS/A2_$(date -u +%Y%m%d)_$HOSTTAG"; mkdir -p "$OUT"
python3 "$TOOLS/audit_matrix_wiring.py" "$ST" --side both --out "$OUT/audit.tsv"
tail -4 "$OUT/audit.tsv"
grep -P '^Test\t.*\tFAIL\t' "$OUT/audit.tsv" | cut -f2,5 | sort > "$OUT/test_failures.tsv"
tail -n +2 "$PLAN/cards/data/A2_expected_test_failures.tsv" | sort > "$OUT/expected.tsv"
diff "$OUT/expected.tsv" "$OUT/test_failures.tsv" && echo "A2_MATCH" || echo "A2_DIFF"
cut -f2 "$OUT/test_failures.tsv" | sort | uniq -c
```

## Ожидаемо

```
TOTAL Test 352
FAIL Test 45
TOTAL Train 352
FAIL Train 52
A2_MATCH
     16 classic_multi_tap,taps_ne_DendriteLength
     29 generator_duplicate_link,synapse_fanout
```

Поражённые Test-входы по волнам:

- `synapse_fanout` + `generator_duplicate_link` (29): W01_CL25 ×4, W05 ×2, W09_HIST_asym25, W11, W13_ltz25 ×2, W16 ×4, W21 ×2, W29 ×3, W31 ×4, W33 ×4, W35 ×2.
- `classic_multi_tap` + `taps_ne_DendriteLength` (16): W12 fs ×5, W13_fs100_preinh, W46 ×8, W47 ×2.

Train-нарушения (52) менее важны: перед обучением SoftCold-сброс срезает Train-модель до сегментов `_1`. Их записать, но не разбирать.

## Дополнительная проверка (5 мин): воспроизвести происхождение

```bash
cd "$NMSDK/Bin"
git show dfbfea63:Configs/SpikeSamples/StructTrain/SelectivityAsymRm/EXP_span25ms_packA_gen/Test/Model_00.xml > "$OUT/clean.xml"
git show 33abcb2b:Configs/SpikeSamples/StructTrain/SelectivityAsymRm/EXP_span25ms_packA_gen/Test/Model_00.xml > "$OUT/corrupt.xml"
python3 "$TOOLS/check_model_wiring.py" "$OUT/clean.xml" | head -3
python3 "$TOOLS/check_model_wiring.py" "$OUT/corrupt.xml" | head -3
sha256sum "$OUT/clean.xml" "$OUT/corrupt.xml"
```

**Ожидаемо:** `clean.xml` даёт `FAIL` только по `classic_dendrite*_generator_taps` (устаревшие мульти-отводы 9/13/15, 9/11/12, 7/8 — тоже дефект, но другой); `corrupt.xml` даёт `synapse_fanout`. SHA `corrupt.xml` = `c3713170921c04c5ec4b4a0d33fc0b4b24a91dd19b05edd8bc708804ccbfe0ac`.

## Выход

`audit.tsv`, `test_failures.tsv`, `REPORT.md`, `result.json` (`total_test`, `fail_test`, `total_train`, `fail_train`, `match_expected`).

## СТОП

`A2_DIFF`: приложить вывод `diff`, ничего не исправлять.
