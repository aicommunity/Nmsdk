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

## F4/F6 (`.11`) — cold закрыт

PulseLib `696f6d7`, Console `8dac9680…`, Bin `774704fc`.

| ID | Train | L | TipR | Test |
|---|---|---|---|---|
| F4.rel UseRelativeAmpEps | converged_need0 | 25 22 15 1 | 2.88 М×3+86 М | gate hang −15 |
| F6.floor PreferConfiguredRminFloor | converged_need0 | 25 22 15 1 | та же | gate hang −15 |

Train/Test: `W01/inputs/W01_CL50_N1_PSIoff/{Train,Test}`. Evidence: `F4_F6_FLOOR_COLD_2026-10-20.ru.md`.

## Вывод

E2 R8×3 на `.17` крутится (S1/S2 W04 уже rep≥2); F4/F6-floor Need=0 на той же L, что F2/F6mid, но TipR не все@Rmin. Дальше: F5, silent-Test, дождаться SERIES_DONE E2 → G1.
