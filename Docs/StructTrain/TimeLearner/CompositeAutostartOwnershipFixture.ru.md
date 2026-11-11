# Исправление cold-autostart fixture

Static review до серверного запуска выявил ошибку fixture: после ConstructNativeModel он пытался поменять ControllerVersion1→2. Штатный SetControllerVersion при NativeTrainingOwned=true обязан отклонять такую смену.

Fixture теперь вызывает Default для освобождения прежнего владения, затем задаёт исходный cold6 declaration/version2, Build, Init и Reset штатного владельца. Проверяет прочитанные ControllerVersion2, IsReady, IsInit, ConfiguredModelInitialized до первого Calculate. Production setters/physics/measurement criteria не изменены; Pulse661 остаётся прежним. IDs10 и numerical expectations не меняются. Локальных сборок/численных запусков нет, runtime gate pending.
