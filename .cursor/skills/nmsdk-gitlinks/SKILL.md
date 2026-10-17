---
name: nmsdk-gitlinks
description: >-
  Commits changes in Nmsdk git submodules (Bin, PulseLib, …) and bumps the
  matching gitlink in the root repo. Use when the user asks to commit StructTrain
  docs, Bin configs, library fixes, or update submodule pointers without
  committing _work archives.
---

# Nmsdk: коммит submodule + gitlink

## Типичный поток (Bin + root)

1. **Submodule** (пример Bin):
   ```bash
   cd Bin
   git status -sb
   git add <только нужные файлы>
   git commit -m "$(cat <<'EOF'
   docs(structtrain): short message why

   EOF
   )"
   ```
2. **Root**:
   ```bash
   cd "$(git rev-parse --show-toplevel)"
   git add Bin Docs/...   # gitlink + связанные Docs
   git commit -m "$(cat <<'EOF'
   docs(audit): short message; bump Bin gitlink

   EOF
   )"
   ```

То же для `Libraries/Nmsdk-PulseLib` и других submodule из `.gitmodules`.

## Что не коммитить

- `*_work/`, StatisticLog, огромные `archives/statisticlog*`
- `__pycache__/`, `.bak_phase12_*` без явной просьбы
- Secrets / `.env`

## Правила git (как user rules)

- Не `git config`; не `--no-verify`; не force-push на main/master.
- Не `commit --amend`, если коммит уже запушен или создан не в этой сессии.
- Стиль сообщений репо: `docs(structtrain):…`, `docs(audit):…`, `fix(…):…`.
- Push только по явной просьбе; для пары root+Bin — push submodule, затем root.

## Проверка

```bash
git status -sb
git submodule status Bin   # или нужный submodule
git log -1 --oneline
```
