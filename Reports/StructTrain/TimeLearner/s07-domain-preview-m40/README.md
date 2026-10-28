# Read-only effective N1 domain preview

A1 root 64a9dc97a1a4c6c96bbf2a5924fd13935df1349b, PulseLib 4be5bc8: compilation failed at a const UEPtr-derived-to-base conversion in diagnostic readback. No native test ran; build log and clean source closure are retained.

Corrected root 9cb30c06515f29228716ed87f34d0e0f6b64cbc9, PulseLib 39179dac15cac5966fe0f2fadda0027c1a086ff3: four real native tests pass on Elder-1 normally and in a separate M40 ASan scoped run, detect_leaks=0. Unsafe proposed Rs can be inspected without applying it; the live model hash and parameters remain unchanged. The returned lower endpoint is applied through the existing native editor and its physical response checked. Fixed/scaled inhibition uses immutable storage profiles with actual different Exc/Inh capacities, not parent defaults or per-tick writes.

Elder-1 additionally passes all eight N0/N1 editor regression cases at 2000/20000 Hz, for twelve native cases total. M40 scoped A3 reuses the immutable A2 binary/runtime and independent output while the longer eight-case ASan editor regression continues separately; no claim about its terminal result is made here. All raw traces/diagnostic observations are retained, without a scientific selectivity verdict.

This source implements the domain inspection API only. The two reproduced controller mesh failures are not fixed here; later controller domain actions use another source snapshot and require their own runtime proof.
