# Статус кампании 2026-10-20 ~23:25 MSK

Продолжение AGENT_PLAN после idle: разблокировка E2 на `.17` и сборка F4/F6 Console на `.11`.

## Инфра (закрыто в этом тике)

На `.17` soft-cold падал с `STOP Avail=76.4G < 80G`, потому что `free_gib()` смотрит том скриптов Bin (корень `/`), а не Data. Неиспользуемые lane `d2*`/`d2b*`/`e2-s*-w01` offload’нуты на Data; Avail корня ≈108 ГБ. Параллельно сняты pre-staged индексы Bin в lane (queue с `--no-commit` всё равно требует пустой index).

Корень падения повторного E2 после диска: whole-wave `--prepare` спотыкался о устаревшие `matrix_definition_sha256` у чужих кейсов волны. Для выбранных E2-кейсов сделан точечный `--prepare --refresh --case-ids …` на Nmsdk-s0/Nmsdk/Nmsdk-e1 и lane; Bin `774704fc` теперь готовит только selected case-ids.

## Train/Test (E2 R8)

| Ряд | Cases | Train/Test |
|---|---|---|
| W01 Classic×N0 | `W01_CL50_N0_PSIoff` | `TimeLearnerMatrix/W01/inputs/W01_CL50_N0_PSIoff/{Train,Test}` |
| W02 Classic×N1 | `W02_CL480_N1_PSIoff` | `TimeLearnerMatrix/W02/inputs/W02_CL480_N1_PSIoff/{Train,Test}` |
| W04 Branch×N1 | `W04_BR100_N1_PSIoff` | `TimeLearnerMatrix/W04/inputs/W04_BR100_N1_PSIoff/{Train,Test}` |
| W10 Branch HIST | br25/50/100 preinh + br25 gen/nextseg | `TimeLearnerMatrix/W10/inputs/<case>/{Train,Test}` |

Host `.17`, limit ≤12 Console; S0=Nmsdk-s0 baseline, S1=Nmsdk audit, S2=Nmsdk-e1 (E1 flags). На момент снимка S0×W04 и S0×W10 уже в train/test; остальные 10 серий перезапущены после refresh.

## F4/F6 (`.11`)

PulseLib `agent/tl-audit-f2-f3` @ `696f6d7` (UseRelativeAmpEps + PreferConfiguredResistanceMinFloor); Bin whitelist `27015f88`→queue fix `774704fc`. Сборка `NeuroModelerConsole` ~86 % (linux-gcc-debug-local); cold F4/F6 — после replace Console.

## Вывод

Кампания снова в движении: диск и matrix-prepare больше не стопят soft-cold на выбранных кейсах; полный E2 R8×3 и F4/F6 cold — следующий измеримый gate. G1/Controller/SYNTHESIS по-прежнему после E2+F*.
