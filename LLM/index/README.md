# Dev knowledge index cache

## RU

This directory is **not** stored in git. NeuroModeler may create or update it on startup
(`UDocSearchIndex::syncFromCatalog`).

## Canonical prebuilt pack

Shipped / local build output:

```
Bin/LLM/index/
  index-manifest.json
  index.jsonl
  link-patterns.json
  connect-semantics.json
  …
```

## Rebuild

From the repository root:

```bash
cmake -S . -B build-llm-ci -DRDK_USE_LLM=ON -DBUILD_TESTING=ON
cmake --build build-llm-ci --target llm-index-pack
```

Runtime load order: `Bin/LLM/index` → this folder (`LLM/index/`) → full in-memory build from catalog.

To reset a broken cache: `rm -rf LLM/index/*` and restart the app or re-run `llm-index-pack`.

See `Rdk/LLM/Docs/Knowledge-Sources.md`.

---

## EN

This directory is **not** stored in git. NeuroModeler may create or update it on startup
(`UDocSearchIndex::syncFromCatalog`).

## Canonical prebuilt pack

Shipped / local build output:

```
Bin/LLM/index/
  index-manifest.json
  index.jsonl
  link-patterns.json
  connect-semantics.json
  …
```

## Rebuild

From the repository root:

```bash
cmake -S . -B build-llm-ci -DRDK_USE_LLM=ON -DBUILD_TESTING=ON
cmake --build build-llm-ci --target llm-index-pack
```

Runtime load order: `Bin/LLM/index` → this folder (`LLM/index/`) → full in-memory build from catalog.

To reset a broken cache: `rm -rf LLM/index/*` and restart the app or re-run `llm-index-pack`.

See `Rdk/LLM/Docs/Knowledge-Sources.md`.
