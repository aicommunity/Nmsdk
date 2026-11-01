# August Phase A passive native temporal primary

Three completed observed saved-state replays reproduce4/8,5/8,6/8; all three CSVs are byte-identical to untouched native replay. Each case records12 streams x80000 samples at2000Hz over40 model seconds: eight native soma channel outputs, neuron aggregate, actual stimulus, LT output and native learner soma vector. Reconstructed soma equals the native learner value at every sample.

Elder7/7 actual-stream reader/corruption tests passed. No historical C++ patches, cold retrain or robustness claim. Plots and M40 validation are separate pending deliverables. The legacy CSV schema itself remains completeness unknown; new raw traces supply their own explicit coverage evidence without manufacturing a training certificate.
