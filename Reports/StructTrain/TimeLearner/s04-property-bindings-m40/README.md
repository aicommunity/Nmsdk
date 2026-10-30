# Pooled direct property bindings: m40

The pre-fix full maintained CTest fails identically on both workers: three suites pass, PulseLib has 395 tests, 370 pass, 10 skips and 15 learned-state export/import failures involving external/null Dataset/Generator bindings. A separate production Python primary-data audit verifies 16 completed source trainings and 208 trial CSV/JSON on each worker; it does not convert failed transport into a pass.

The native test-only baseline reproduces stale external scalar/matrix pointers across Return/Take and Copy (two failed cases, one lifecycle-preservation pass). Fixed A1 still contains two matrix-fixture failures: direct operator()(0,0) accesses a cached local matrix rather than effective connected data. A2 reads GetData()(0,0) and adds constructor/internal/mixed-vector wiring preservation; the baseline scalar and binding-identity failures remain valid evidence of the production defect.

Rdk 1223bcc18cf1ba106e8f8a17f20cce8c000c104d cleans external sources at pooled cold reuse and replacement Copy/full BreakLinks boundaries, preserves native internal wiring and remaps direct closed internal links during UNet Copy. Ordinary Build/Reset/Default keep live bindings. Model identity is not relaxed. Eighteen native unit cases pass on Elder-1 normally and M40 under ASan (detect_leaks=0).

Elder-1 additionally passes 25 native builder cases followed by five learned-state cases in one process, 18 container cases and nine independent Python tests. The five model packages include fresh-process import, frozen response and actual rollback controls; primary-data checks cover 62 training trials and four rollback probes.

These are addressed implementation checks, not whole-plan acceptance or scientific recognition results. Post-fix full maintained CTest is a separate pending gate. All attempts and original data are retained through Git with independent compressed/raw SHA256. No credentials or executable is committed.
