# REPASS_ITI6 interim (hourly check 2026-10-24 21:15Z / 00:15 MSK)

ITI 6 s, target at position 1 (ref) and 4 (tpos4). Detection = target spikes, samples do not, in BOTH orders.

- .11 REPASS_ITI6_e11_20261024T2011Z: 36/74 cases done (28 NO_RESULTS), jobs 6/17; max sep -0.0002; no positive sep. br25/br50 nextseg, br25sim k1/k2: no selectivity (confirms ITI carry-over conclusion).
- .17 REPASS_ITI6_e17_20261024T2012Z: 20 cases done (2 NO_RESULTS), jobs 2/8.
  - W08_BR480_N0_PSIoff_NEXT: sep=+0.0196 in BOTH orders; target spikes at pos 1 and pos 4, no sample spikes. Only order-invariant candidate so far. Margin is thin: closest sample residual 0.0358 vs target 0.0365. Needs replication (other seed/jitter, ITI 12 s) before calling it detection.
  - W04_BR480_N0_PSIoff: ref sep=1.0 but tpos4 sep=-inf (only the first trial responds) -> first-trial artifact.
  - W01_CL50_N0_PSIoff: ref +0.0142, tpos4 -0.0188 -> order artifact.
  - br100 keep/nextseg/gen, asym100: negative sep.
- Throughput: REPASS launcher runs batch-wise; .11 batch tail leaves cores idle (4/8 Console busy incl. E0). E0-E5 series active on .11 (~/e05_runs) by a parallel process.
- Disk: .11 / 150G free (67%); .17 / 119G free; /media/user/Data 429G free (88% used, above 5% threshold).
