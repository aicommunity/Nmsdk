# Controller v2 — заметка H3 mid + H4 margin (2026-10-22)

Краткая связка для [`CONTROLLER_V2_SKELETON_2026-10-21.ru.md`](CONTROLLER_V2_SKELETON_2026-10-21.ru.md) после offline mid-sweep и E1.1b.

1. **H3 (mid policy):** при NonSeparable Test не оставлять `FixedLTZ=1` как единственный классификатор — finite `candidate_mid` даёт foil fires (`01000101`); флаг `UseCandidateMidOnNonSeparableTest` (default off) — [`MID_POLICY_H3_COLD_2026-10-22.ru.md`](MID_POLICY_H3_COLD_2026-10-22.ru.md).
2. **H4 (sep_margin @ flat Rmin):** на Classic×N0 W01 TipR=86 МОм×4 target LTZ≈0.00223 &lt; `candidate_mid`≈0.00241 при отрицательном gap; E1.1b AsymRm показывает γ(L)≈const по TipR, поэтому **равномерный** midband scale (~×5.6) сохраняет знак gap — [`SILENT_TEST_H4_MARGIN_2026-10-22.ru.md`](SILENT_TEST_H4_MARGIN_2026-10-22.ru.md).
3. **AMP_ALIGN / TipR:** рычаг amp — log Rs и N (N≲8…16), не «γ(TipR)»; Verify должен измерять **sep_margin** (target−max_foil), а не Need=0.
4. **Cold TipR overlay:** отложен (D1 bisect); следующий cold — ось H2 KeepDone, не проверка сильного H4.
