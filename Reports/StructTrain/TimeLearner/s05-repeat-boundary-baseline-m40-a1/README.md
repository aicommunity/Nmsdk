# Repeated-N0 boundary baseline

All ten addressed native tests on m40 fail exactly two summary assertions: absent search_history_retained and absent candidate_repeat_groups after import. Other checks in these actual storage/scheduler/Train-Test/frozen/fresh-process/warm controls produce no separate assertion failures. This is a defect reproduction, not a passing training campaign or recognition verdict.

The original temporary runner also failed while JSON-serializing the Path returned by successful runtime verification. The separate terminal runtime-after-readback.json records the corrected hash readback. All attempts are retained without rewriting history. Fixed evidence is separate.
