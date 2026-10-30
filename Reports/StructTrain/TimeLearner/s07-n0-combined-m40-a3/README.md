# Combined N0 / infrastructure integration gate

Root 2b7267526c834484be12549f3614d3d967b4bc9b: 53/53 production Python tests on m40, no skips/errors/failures, plus actual XML parsing and repeated-N0 ClassDesc readback of Bin 34a9e60d0b8e38522e1cce4d59378b6a9bda7844. Real native A2 primary data and all 132-trial / 198-soma-pair plots are reused unchanged; no new model training is claimed.

Attempts a1/a2 are retained failures of job preparation: a1 omitted native subdirectories and mistakenly substituted a Python environment-variable name; a2 selected obsolete domain-preview kind. Neither is an algorithm failure or passing run. Corrected a3 uses explicit native paths and verifies input kind before testing. Positive figures under test_actual_cli_all_recorded_somas_common_axes_and_primary_hashes use actual Classic/Branch data; other test_* figures contain declared corrupted metadata controls.

Scientific verdict and full-matrix visual acceptance remain unclaimed. Module list, exact counts and input hashes are in a3/validation.json and a3/input-provenance.json.
