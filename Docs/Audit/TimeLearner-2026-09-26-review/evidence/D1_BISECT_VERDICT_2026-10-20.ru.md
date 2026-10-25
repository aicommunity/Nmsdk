# D1 VERDICT — Classic N1 PulseLib window

Постановка: бисекция i=0 (`780ffc7`) vs i=11 (`d52dc1c`) по карте D1 для W01 и W02.

| Case | Trainer×Mode | Span | i=0 | i=11 | Train/Test (i=11) |
|---|---|---|---|---|---|
| W01_CL50_N1_PSIoff | Classic×N1 | 50 | converged_need0 | converged_need0 | D1.d52dc1c-…-20123 / attempt Train+Test |
| W02_CL480_N1_PSIoff | Classic×N1 | 480 | not_converged_at_stop TipR@Rmax | not_converged_at_stop TipR@Rmax | D1.d52dc1c-…-12466 |

**Вердикт по правилу карты §2:** для W02 i=0 тоже «плохо» → **СТОП бисекции**: на текущих входах регрессии Classic N1 **внутри** окна PulseLib 11.09–19.10 нет. Ухудшение пришло не из PulseLib этого окна или раньше 11.09 / вне PulseLib. W01 оба конца «хорошо» — бисекция на W01 не нужна.

Ось CL-N1 для F2–F8 / D2 остаётся открытой как алгоритм/параметры (EstDelay, γ, Rmax), не как поиск «плохого» коммита PulseLib в окне.
