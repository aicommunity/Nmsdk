# Neuro Modeler SDK (Nmsdk)

## RU

SDK for spiking neural networks and robotics simulation on the Rdk component architecture.

## Documentation

**Start here:** [Docs/README.md](Docs/README.md)

| Topic | Link |
|-------|------|
| Quick start | [Docs/Overview/QuickStart.md](Docs/Overview/QuickStart.md) |
| Architecture | [Docs/Overview/Architecture-Overview.md](Docs/Overview/Architecture-Overview.md) |
| Build system | [Docs/Build-And-Deploy/Build-System.md](Docs/Build-And-Deploy/Build-System.md) |
| Doc audit hub | [Docs/Audit/README.md](Docs/Audit/README.md) |

## Repository layout

- `App/` — NeuroModeler (GUI), NeuroModelerConsole
- `Rdk/` — core engine (submodule)
- `Libraries/` — component libraries (submodules)
- `Bin/` — configs, ClDesc, runtime resources (submodule)
- `Docs/` — project documentation

## Submodules

Initialize with:

```bash
git submodule update --init --recursive
```

See [.gitmodules](.gitmodules) for the canonical list (Rdk, Bin, five Libraries).

## Build (quick)

```bash
cmake --preset linux-gcc-debug
cmake --build build
```

See [Docs/Build-And-Deploy/](Docs/Build-And-Deploy/) for platform-specific guides.

---

## EN

SDK for spiking neural networks and robotics simulation on the Rdk component architecture.

## Documentation

**Start here:** [Docs/README.md](Docs/README.md)

| Topic | Link |
|-------|------|
| Quick start | [Docs/Overview/QuickStart.md](Docs/Overview/QuickStart.md) |
| Architecture | [Docs/Overview/Architecture-Overview.md](Docs/Overview/Architecture-Overview.md) |
| Build system | [Docs/Build-And-Deploy/Build-System.md](Docs/Build-And-Deploy/Build-System.md) |
| Doc audit hub | [Docs/Audit/README.md](Docs/Audit/README.md) |

## Repository layout

- `App/` — NeuroModeler (GUI), NeuroModelerConsole
- `Rdk/` — core engine (submodule)
- `Libraries/` — component libraries (submodules)
- `Bin/` — configs, ClDesc, runtime resources (submodule)
- `Docs/` — project documentation

## Submodules

Initialize with:

```bash
git submodule update --init --recursive
```

See [.gitmodules](.gitmodules) for the canonical list (Rdk, Bin, five Libraries).

## Build (quick)

```bash
cmake --preset linux-gcc-debug
cmake --build build
```

See [Docs/Build-And-Deploy/](Docs/Build-And-Deploy/) for platform-specific guides.
