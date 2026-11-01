# Cursor skills (Nmsdk)

Канон скиллов для агента Cursor. **Править только здесь** (`Skills/Cursor/`), затем синхронизировать копию для автовызова:

```bash
./Skills/Cursor/sync.sh
```

Копия: `.cursor/skills/` (project skills; Cursor подхватывает их в этом репозитории).

Не трогать `~/.cursor/skills-cursor/` — служебный каталог Cursor.

## Скиллы

| Каталог | Когда применять |
|---------|-----------------|
| [`structtrain-experiments`](structtrain-experiments/SKILL.md) | Cold/PostTune StructTrain, `posttune_verify`, обновление `EXPERIMENTS.md` / `SUCCESSFUL_EXPERIMENTS.md` |
| [`nmsdk-build`](nmsdk-build/SKILL.md) | Сборка PulseLib / NeuroModelerConsole (cmake presets) |
| [`nmsdk-gitlinks`](nmsdk-gitlinks/SKILL.md) | Коммит в submodule (Bin, PulseLib, …) + bump gitlink в root |

## Правила

1. Description в frontmatter — на английском (third person, trigger terms); тело можно на русском.
2. Рабочие скиллы **без** `disable-model-invocation: true` (нужен автовызов).
3. После правок канона всегда `./Skills/Cursor/sync.sh` и коммить **оба** дерева (`Skills/Cursor/` и `.cursor/skills/`).
