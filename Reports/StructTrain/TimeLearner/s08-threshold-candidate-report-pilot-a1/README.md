# Threshold candidate report pilot

Branch N1 at 2000 Hz; new dispersed two-pattern fixture, not the historical eight.
Four native presentations are retained, including reset-per-trial and continuous probes.
The complete report is a reproducible M40 cache; only three selected PNGs are stored here.
Three report readback checks passed. This is not acceptance of the complete native matrix, calibration controller, or stage 8.

Extract primary.tar.xz into a new directory. From the declared reader revision run:

    python3 -m Scripts.StructTrain.TimeLearner report report/primary/evaluation.json --format threshold-candidate-evaluation --model report/primary/model.json --output NEW_CACHE

The archive also retains native training CSV and model/probe packages for primary-source audits.
manifest.json lists uncompressed file hashes. Soma units remain unverified; graph review is pending.
