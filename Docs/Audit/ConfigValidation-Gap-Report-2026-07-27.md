# Config Validation — Gap Report (2026-07-27)

## RU

Свежий прогон Track 5 umbrella roadmap.

### Команда

```bash
python3 Scripts/generate_detailed_validation_report.py --subdir TestValidation --time-budget-seconds 120 --finalize
```

### Результаты (`Bin/Configs/TestValidation`)

| Metric | Value |
|--------|-------|
| Total | 7 |
| Valid | 3 |
| Invalid | 4 (expected negative fixtures) |
| Model missing | 2 |
| Other errors | 4 |

Отчёт: [ConfigValidation-Detailed-Report.md](../../Reports/ConfigValidation-Detailed-Report.md). Кэш: `Reports/ConfigValidation-Results.jsonl`.

### CI / интеграционные тесты

Покрытие в [Tests/Integration/ConfigValidation/](../../Tests/Integration/ConfigValidation/):
- valid / missing model / missing parameters / invalid XML / empty model / invalid classes / invalid links

**Gaps vs historical [Reports/NextSteps-Plan.md](../../Reports/NextSteps-Plan.md):**
1. Полный прогон всех `Bin/Configs/SpikeSamples` + legacy — не в CI (долго); запускать с `--subdir SpikeSamples` по необходимости.
2. Исторические «288 несуществующих классов» / «другие ошибки» на полном дереве — требуют отдельного nightly budget (`--time-budget-seconds` ≥ 540) и сверки с `check_registered_classes.py`.
3. CI gap: ConfigValidation tests покрывают synthetic fixtures, не production SpikeSamples corpus.

### Рекомендации

- Держать CI на `TestValidation` + `Test_ConfigValidation`.
- Nightly: `--subdir SpikeSamples` с артефактом JSONL.
- Не применять массовые fix-скрипты из 2026-01 без свежего полного отчёта.

---

## EN

Fresh Track 5 validation pass.

`TestValidation` fixtures: 7 configs, 3 valid / 4 invalid (expected). Full SpikeSamples corpus remains a nightly/manual budget item; CI covers synthetic ConfigValidation fixtures only.
