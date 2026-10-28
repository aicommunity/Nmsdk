# Native N1 controller uses effective resistance domains

A1 root c2507722661ad4a0c0965b11ab6d91471f445322, PulseLib e875ca53c66fee93ba18cf7f7da05a87f33d32f9: both formerly failing Classic/Branch mesh cases pass; 24 actual primary JSON/CSV trials and four domain assessments are independently audited. The effective lower endpoint is really measured. Unsafe mesh edit rejections are absent.

A2 root 157a5301ed418d61f4ccd86829ba483308c4300c uses the same production PulseLib and adds tests: fourteen arithmetic/controller cases and six native cases all pass. Native controls cover Classic/Branch at 2000/20000 Hz, bounded shared Branch banks retaining a singleton geometry, and free upstream banks separating for Rs search. The anchor remains unchanged. Native evidence audit validates 68 actual primary trials and fifteen domain assessments; final certificates, where present, are checked against original measurements. The two Branch geometry controls deliberately stop after the required measured decision and carry no convergence certificate.

Domain actions use read-only native previews, preserve declared search bounds and CapturedPerInput goals, and refresh after effective edits. Raw traces and domain summaries are retained. The synthetic arithmetic cases test stale/NaN/domain failure rejection, independent non-intersecting input intervals and empty-domain SearchUnresolved; they are not substitutes for real component tests.

ASan of the new controller, learning/export regressions, the complete physical/inhibition/C-trim matrix, full refactoring stages and scientific evaluation remain open. Earlier API-only checks and expected-failure baselines are separate source snapshots. No binaries or credentials are published.
