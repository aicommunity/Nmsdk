# Configured native controller evidence (m40)

ControllerVersion defaults to 1 for existing configurations. Version 2 parses the explicit serialized ControllerConfiguration, constructs the physical model through native storage images, and starts the shared training service from the native scheduler. There is no manual BeginNativeTraining call in these configured controls. Both direct property configuration and real native cold XML Load are exercised.

A1 root 17eff7e4d01dd7b542342302524c23637f1f8f6d: 6/6 new and 97/97 old-builder/service/editor/lifecycle/bounded/final/assigned regressions pass. A2 root e6b576d2a36a309a84f49e33ef359b216f8154bf: 12/12 new and 97/97 regressions pass. A2 adds real trained-marker XML Load and Copy(false/true) guards with individual child capacity. The marker is also a parameter because Rdk Copy builds before copying state.

A3 root cb9e035b390390746ada5caa2c500917b8884612: 14/14 configured controls and 21/21 addressed old native builder/service regressions pass. Two extra controls load cold XML and run actual Classic/Branch training without assigning receiving-object configuration parameters or invoking the training API. The model retains its parameters across forced Build/Reset.

Initial independent A2 analysis is preserved with two failing corruption tests: they assumed isolated selection and made a no-op mutation on actual assigned-policy data. Production auditor rules were not relaxed. Corrected A3 tests explicitly request isolated semantics for a whole-burst window and change the actual selection to the other policy. All 18 tests pass on configured assigned data and separately all 18 pass on real legacy isolated data, without skips.

Independent primary-data audit covers 308 service packets/CSV and 22 negative certificate summaries across A2/A3, including 28 actual cold-XML probe packets. It also checks 16 native builder packets and four earlier assigned/isolated diagnostics. These are implementation controls with SearchUnresolved outcomes, not independent scientific retrainings or recognition success. Full CTest and the full physics matrix are not claimed.

ConfiguredModelInitialized prevents silent cold reset of saved models when the process-local declaration is unavailable. Such XML/Copy state is held with an explicit state-import diagnostic. The full trained-state codec, Train-to-Test, configured retarget/protocol changes, dynamic resistance domains, C-trim, conversion/PostTune/calibration, production experiment tooling and scientific controls remain required.

Git is the sole transfer path. All attempts, failed analysis logs, runtime/source manifests, cold XML and JSON, primary CSV and model identities are retained with stored/raw SHA256. No binary or credential is committed.

ASan with detect_leaks=0: A2 12/12 configured controls; A3 9/9 cold XML, saved XML/Copy and strict codec checks. Absence of all leaks is not claimed.
