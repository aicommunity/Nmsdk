# Intermediate native readout and matrix diagnostics: normal

All fixed-readout attempts a1/a2/a3 and the direct production MDMatrix baseline are retained with their original code/runtime/process results. a1 combines remaining N1 role errors with an incorrect test expectation that Ready Build should repair a buffer. a2 corrects that expectation but still fails all8 N1 cases. a3 normal passes32 native and21 regression tests; the same a3 ASan run stops during Reset because old Rdk MDMatrix Resize reads rows that did not exist when changing1x2 to3x1 within retained capacity.

The direct matrix baseline passes10 ordinary tests but reproduces the same ASan finding immediately. Normal reader16/16 is included only as an audit of actual normal a3 data. Joint implementation acceptance is withheld. These numerical diagnostics have no scientific selectivity verdict. Later corrected Rdk and full integration runs belong to separate artifacts.

The archive contains exact native XML/model/graph/waveform exports where available, all test and process records, source/runtime provenance and original diagnostic messages. No binary build products or regenerated image caches are included.
