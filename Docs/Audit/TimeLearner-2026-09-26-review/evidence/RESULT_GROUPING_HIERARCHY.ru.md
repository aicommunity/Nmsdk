# Канон группировки результатов TimeLearner / StructTrain

Дата: 2026-10-19.  
Обязателен для STATUS, SYNTHESIS, boundary maps, N1_EXECUTE, chat-тиков и evidence-сводок после этой даты.

## Термины

| Термин | Смысл |
|---|---|
| **Trainer** | `Classic` (`NNeuronTimeLearner`) или `Branch` (`NNeuronTimeLearnerBranch`) |
| **Mode** | **N0** — чисто структурный (`NormalizationMode=0`); **N1** — структурная синхронизация + параметрическая нормализация TipR (`NormalizationMode=1`) |
| **N0/N1 vs M0/M1** | N0/N1 — ось Mode в конфиге/матрице. Исторические ярлыки кампании **M0/M1** (track BR-M0 / BR-M1) соответствуют тому же Mode; в новых текстах писать `N0/N1 (равн. M0/M1 track)` один раз и дальше предпочитать N0/N1 |
| **Span** | Длина паттерна: 25 / 50 / 100 / 480 мс (ось **временного паттерна**, не модель нейрона) |
| **NeuronModel** | Семейство модели нейрона/элемента: baseline Branch W10, AsymRm, FastSpan, LTZ, … — **не** «семья паттерна» |
| **Mod** | Модификация протокола: `gen`, `preinh`, `nextseg`, PSI on/off и т.п. |
| **PostTune** | Колонки ON / OFF (и при необходимости tip-modes), не отдельный верхний уровень группировки |

## Иерархия заголовков (сверху вниз)

1. **Trainer × Mode** — четыре корзины: Classic×N0, Classic×N1, Branch×N0, Branch×N1. Не смешивать корзины в одной таблице без явных заголовков.
2. **Span** (25 / 50 / 100 / 480 мс).
3. **NeuronModel** (baseline / AsymRm / FastSpan / …).
4. **Строки = Mod** (`gen` / `preinh` / `nextseg` / …); **колонки = PostTune ON / OFF** (Need, fires, detected, `posttune_result`, SHA, Host, RUN_ID).
5. **Configs Train · Test** — в каждой строке ссылки на каталоги Train и Test, с которых готовился / на которых интерпретируется результат (см. скилл `structtrain-experiments`).

Шаблон:

```markdown
## Trainer=Branch · Mode=N1 (структурная sync + параметрическая TipR)
### Span=25 мс
#### NeuronModel=baseline (W10 Branch)
| Mod | Configs (Train · Test) | PostTune OFF: Need / fires / detected | PostTune ON: Need / fires / detected / posttune_result | SHA | Host | RUN_ID |
|---|---|---|---|---|---|---|
| gen | [Train](…/EXP_…/Train) · [Test](…/EXP_…/Test) | … | … | … | … | … |
```

## Запреты

- Не называть AsymRm / FastSpan «семьёй паттерна»: при одном Span ISI часто общий; различается модель элемента.
- Не класть Branch PASS×3 и Classic W01 в одну «общую» таблицу без колонки Trainer и без разделения корзин Mode.
- Постановки и выводы — развёрнутыми предложениями (см. rule `timelearner-experiment-prose` и скилл `structtrain-experiments`).
- Не публиковать сводную метрик без ссылок на Train и Test конфиги соответствующей строки.
