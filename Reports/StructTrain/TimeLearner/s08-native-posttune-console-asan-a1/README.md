# Production measured PostTune: ASan

M40 ran 18 genuine owned Console jobs using the saved normal N1/two-input/2000 Hz models: all five modes, Auto/LTZone/SomaSum, silent threshold and recording budget. Nine calibrated, seven search_unresolved, two budget_exhausted. The corpus also includes six calibration regressions, two extra public calibration CLI jobs, two model-tick stops and four strict native CLI rejections. All four PostTune reader checks (112.103 s), eight calibration worker checks (234.799 s) and four provenance checks (15.333 s) passed without skips.

Binary source ffd5b15a2, Python worker 74f49a5f0. ASan leak detection was disabled. This is saved-model pipeline validation, not independent retraining or eight-pattern scientific classification. All primary artifacts are losslessly archived; analysis source is available by exact Git commit. Full production waveform reports, N0/profile/frequency/dimension matrix, learner dispatch and continuation remain open.
