# Classic/Branch: три торможения — постановка, формулы, псевдокод (2026-10-23)

**Ветка:** `timelearner_fix3`  
**Done кампании:** coldtrain сетки Classic 8×3×2 (48) + Branch 8×3 N1 (24).  
**Вне scope:** A / SeparateInputLines / F1b / H0-88.

Постановка: вход Classic **не меняем** (один Generator1 → fan-out). Изучаем три механизма торможения по одному и в комбинациях; на Branch — тот же набор, включая SegEI как полноценную опцию (абляция \(d\) vs NextSeg).

---

## 1. Три механизма

### 1.1 Обозначения

- \(S\) — span (с); \(t_0,\ldots,t_3\) — времена импульсов цели.
- \(L_k\) — длина дендрита \(k\) (Classic tip = сегмент \(L_k\)).
- \(K_E(L,t)\), \(K_I(L,t)\) — EPSP/IPSP на соме.
- \(\tau=R_m C\), \(\delta\approx\tau\) — задержка на сегмент.
- \(m=(P_{\mathrm{tgt}}-\max_j P_{\mathrm{foil},j})/P_{\mathrm{tgt}}\).

Текущая топология (одна линия):

\[
V(t)=\sum_{k=0}^{3}\sum_{j=0}^{3} w_k\, K(L_k,\,t-t_j).
\]

### 1.2 PSI / preinh

Пресинаптическое масштабирование (\(k_{\mathrm{PSI}}=2.5\)): класс синапса / флаги preinh в EXP. Не даёт \(\Delta t\) Exc vs Inh на кабеле.

### 1.3 NextSegInh

\[
K_{\mathrm{NS}}(L,t)=K_E(L,t)-\beta\,K_I(L+1,t),\quad
\Delta t_{\mathrm{NS}}\approx\delta\approx\tau.
\]

Branch: уже есть (`EnableNextSegmentInhibition`). Classic: **порт** — на каждом дендрите Exc@\(L_k\), Inh@\(L_k+1\).

### 1.4 SegEI

\[
K_{\mathrm{EI}}(L,d,\alpha;t)=K_E(L,t)
-\alpha\cdot\frac{\max K_E(L)}{\max K_I(L+d)}\,K_I(L+d,t),
\quad\Delta t\approx d\cdot\tau.
\]

Старт волны: \(d=8\), \(\alpha=1.0\); нейрон SymInh (\(\tau_{\mathrm{inh}}=\tau\)).  
На одной линии линейный оракул даёт \(m_8<0\); cold измеряет Console/нелинейность и отличие от NextSeg (\(d=1\) vs \(d=8\)).

| | NextSeg | SegEI |
| --- | --- | --- |
| \(d\) | +1 | параметр (8) |
| API | `EnableNextSegmentInhibition` | `EnableSegExcInh` + `SegExcInhDelta` + `SegExcInhAlpha` |

При \(d=1\) и обоих флагах — не дублировать Inh (Segei XOR NextSeg).

---

## 2. Псевдокод (канон реализации)

См. исполняемый Cursor-план кампании (не дублировать сюда дословно при расхождении — этот файл = evidence постановки). Ключевые API:

```
EnableNextSegmentInhibition, EnableSegExcInh, SegExcInhDelta=8, SegExcInhAlpha=1.0
TipSeg(k), InhSeg_NS(k)=TipSeg+1, InhSeg_EI(k)=TipSeg+d
Ensure*Inh, Relink* → Generator1.Output → Inh.Input
WireAllInh: clear stale Inh links; SegEI then NextSeg if d!=1
```

Branch SegEI: `InhSeg = PulseAttachPos(pulse) + SegExcInhDelta`.

Neuron: `NSPNeuronGenSymInhC1e9` (Rm_inh = Rm_exc), не overwrite AsymRm HIST.

---

## 3. Сетка coldtrain

**Classic** (`.11`≤8): 8 Mod × Span{25,50,100} × {N0,N1} = 48.  
**Branch** (`.17`≤12): 8 Mod × Span{25,50,100} × N1 = 24.

Mod: `gen`, `preinh`, `nextseg`, `segei`, `preinh_nextseg`, `preinh_segei`, `nextseg_segei`, `all`.

Метрики: `training_convergence`, `sep_margin`, fires/Acc. Автокоммит артефактов по ходу.

---

## 4. Статус

| Шаг | Статус |
| --- | --- |
| Этот документ | done |
| PulseLib NextSeg Classic + SegEI Classic/Branch + SymInh | done (40f09a2) |
| Bin EXP сетка | done (01baf8d4, 72 EXP) |
| SoftCold Classic 48 | **очередь Done** (48/48); после disk_stop re-run S25/S50 закрыты; Acc PASS не получен |
| SoftCold Branch 24 N1 | **очередь Done** (24/24); Acc PASS не сведён в таблицу |
| RESULTS | done → [`CLASSIC_BRANCH_INH_RESULTS_2026-10-24.ru.md`](CLASSIC_BRANCH_INH_RESULTS_2026-10-24.ru.md) (+ addendum disk_stop re-run) |
| Научный разбор Acc/mid/Need по Mod (абляция NextSeg vs SegEI) | **не выполнен** — нет сводной Acc N/8 / Цель |
| Branch×N0 | вне Done-сетки (как в постановке) |
