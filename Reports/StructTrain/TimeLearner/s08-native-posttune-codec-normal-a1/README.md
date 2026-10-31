# Shared PostTune configuration: mechanical production proof

Root d48837f1 / PulseLib 30f737c8: the production Console now uses the common strict typed decoder instead of its own nine-control parser. No physical model, mathematical target, native scheduling or algorithm was changed. Three native codec cases passed without skips, including all 18 original published production jobs and direct numeric field bindings, malformed fields/types/budgets/nonfinite controls.

Two actual owned Console A/B jobs, Classic-auto_metric and Branch-synthetic, used the original unchanged job documents and primary sources. Both transaction.json and final model.json matched the original Git primary bytes exactly; portable production run audits passed. The original source was reconstructed from commit 3c1751f977b26a6d6a1d82065f34a44c456a1b41. The baseline-source extraction is reproducible from that bundle and is not duplicated in this archive; extraction recipe and expected digests are preserved.

This scoped mechanical acceptance does not implement learner-property phase dispatch, continuation, the full mode/profile/frequency matrix or independent scientific classification. The configured optional-mode guard remains.
