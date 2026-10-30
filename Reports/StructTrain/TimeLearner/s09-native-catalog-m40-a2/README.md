# Immutable native test report inputs

Source fb01871cf2158ece735ab45e148fc20fc33594cd on m40: 7/7 addressed production catalog tests, no skips/errors/failures; transport exit 0 was observed. Includes actual A3 338-probe coverage and corruption controls for lost phases, last packets, orphan CSV, missing embedded fresh-process executions, duplicate sources and skipped JUnit cases. New guard rejects output within immutable input before any write or recursive copy. No native model was rerun.

This follows the combined 92-check gate; it is seven addressed checks after the new path guard, not a claim of rerunning the entire combined suite. Full graphical readback remains separate. No scientific verdict or full-stage acceptance is inferred.
