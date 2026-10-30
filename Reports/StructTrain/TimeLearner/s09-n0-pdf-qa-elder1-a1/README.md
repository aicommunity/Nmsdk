# Read-only PDF visual QA and complete-set spike policy

Two unchanged vector PDFs (Classic overview and Branch zoom) were rendered at 160 dpi by worker Poppler. Source PDF hashes are verified against the exact Git-published full-report parent commit. The two previews were opened and visually inspected by Codex on 2026-10-30; see visual-review.json for source hashes and scoped findings. Labels and overlaid signals are readable without visible overlap or clipping. No PDF was edited. The original manifest retains its historical human-review=false; no human review or full-matrix acceptance is claimed.

The stricter complete-set readback at root 7b808c11e passes two tests on all 132 trials / 198 soma pairs, including explicit record_spikes=false and spike_count=null. Unknown spike response is not measured silence. Native scientific/physics matrix remains open.
