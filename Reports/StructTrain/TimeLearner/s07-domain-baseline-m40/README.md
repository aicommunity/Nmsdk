# Native N1 candidate-domain baseline

Root fda22b8d99e7a65bb8f97ac4d2ce288219ced9c0, PulseLib 87e6c2247f0cd962609bc40a04fd92dafa024a0b (tree identical to 12c5ef5), Rdk 1223bcc. Two real native Classic/Branch tests each fail exactly one assertion: the declared resistance mesh spends one of its three candidate slots on an Rs rejected by the production integration preflight as channel_step_not_certified_strictly_stable. The rejected candidate never changes the live model. This is a search-domain/budget defect, not a demonstrated unstable applied edit or proof of physical infeasibility.

The fixture uses 2000 Hz, N1, fixed attachment geometry, declared 0.5 MOhm to 1 GOhm bounds. It records actual native trials and requires at least two measured candidate evidences and an applied edit; it does not require any particular convergence outcome. Independent production Python audits validate all 20 actual JSON/CSV trials across both topologies and verify any final certificate from measured data.

Normal Elder-1 and M40 ASan (detect_leaks=0) are published as separate packages. No fix is claimed yet. These expected-failure tests must not be accepted into develop without the algorithm change. The tests and findings do not invalidate historical August observations or restart Series D.
