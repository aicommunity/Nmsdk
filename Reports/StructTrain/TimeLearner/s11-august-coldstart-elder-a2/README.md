# August native pre-stimulus cold-start gate

Exact old root de02a3809395dd0bbd11e2ba792bfc04a51c89f3, same historical executable. Four successful native gate operations before the first input pulse (model limit0.0005s). Native StatesFile ResetToUntrainedState=1 with ProjectAutoSaveStateFlag=1 gives four actual L1 segments, zero references,86M Ohm per tip and no input pulses. Turning the state-load switch off leaves116 old segments. Parent-only cold overlays declare L1/1/1/1 but retain116 actual segments: rejected graph/parameter mismatch, never eligible for cold Train.

Initial a1 stopped on that newly observed discrepancy after3 Console operations; retained as failed. Corrected a2 preserves it as a measured negative control and completes all4 operations. This changes experiment validation, not old algorithms or lifecycle.

Archive includes all original and post-run model/config/state files, process/runtime receipts and49 reconstructed prepared inputs verified against their original pre-run hashes. Prepared input capture is now automatic in the producer. Full160s cold Train is separate and still running; no scientific convergence or recognition verdict.
