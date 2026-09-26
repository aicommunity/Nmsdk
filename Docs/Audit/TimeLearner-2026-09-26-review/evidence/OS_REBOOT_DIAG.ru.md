# OS reboot diagnostics (2026-09-26)

Host: ASUS All Series / Z87-PRO, BIOS 2103 (2014), kernel 6.8.0-138-generic, ~32 GiB RAM.

## Boots today

| Boot | Start | End (last journal) | Duration |
|------|-------|--------------------|----------|
| long session (−2) | ~2026-09-21 09:37 | 2026-09-26 **16:29:08** (ollama INFO) | ~5 days |
| short (−1) | **16:30:19** | **16:42:41** (gnome-shell Pixbuf spam) | ~12 min |
| current (0) | **16:43:53** | running | — |

## Verdict

Both reboots are **unclean hard resets** (power loss / hard button / hang without flush):

- **0** matches for `systemd-shutdown` / `Starting Reboot` / `Reached target Power` on boots −1 and −2.
- **No** OOM killer, kernel panic, oops, MCE, soft/hard lockup, thermal critical, disk I/O errors in journal before cut.
- Last lines are ordinary userspace (gnome-shell `ubuntu-appindicators` Pixbuf errors, Cursor gc-trace, ollama) then silence → next boot.

Not explained by SoftCold alone in the log (no NeuroModeler lines in the last minutes of either cut). SoftCold *was* running earlier in the long session / briefly after resume; abrupt power-off kills it without `provenance.json`.

## Likely hardware/power class (not proven in OS log)

Z87 + old BIOS + unclean dual reboot in ~13 min points to: PSU brownout, overheating without ACPI critical log, GPU hang hard-locking machine, or manual reset. OS journals cannot distinguish these without IPMI/BMC.

## Recommendations before more SoftCold

1. Do **not** stack heavy Train + GUI Cursor + ollama until stability check.
2. Optional: `sensors` under load; check PSU/temps; update BIOS if available.
3. Prefer SoftCold under `tmux`/`systemd-run` with `nice`/`cpulimit`; keep `PARALLEL=1`.
4. Persist progress frequently (already via `_repro/runs/`); expect reboot mid-run → re-run case.
