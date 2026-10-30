# LTZone event history: m40

Baseline 9ecb3967f: two native failures reproduce a fake timestamp retained after Reset. A real spike at t=0 is preserved. Fixed d13620e1e / PulseLib 1de63d0: 12 tests pass, zero skips/errors; ten lifecycle cases and two fresh-destination owner regressions. Extended native test checks two distinct real rising edges, a sustained pulse without duplicated onset, and empty history immediately after Reset and after a silent tick. The native process returns zero; original outer login-shell status remains one and is preserved.

The independent short shell diagnostic A2 reproduces login-shell return 1 versus non-login return 0 with identical successful body and parent SHLVL=0. The worker .bash_logout invokes clear_console under SHLVL=1; set -e turns its failure into the outer exit status. A1 nested-shell diagnostic had a different SHLVL and both returns were zero; its failed assertion is preserved. No model rerun is inferred from that diagnostic and no original status is rewritten.

Runtime manifests and path/hash records were rechecked before publication. Complete original XML/logs and fresh-owner primary observations are retained losslessly. This is scoped component/integration evidence. It does not validate complete spike windows, all LT classes, calibration, target/foil evaluation, or scientific selectivity.
