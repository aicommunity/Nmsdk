# Серверная проверка общего export boundary

Canonical preparation s08-shared-export-sdk-canonical-m40-a1 завершена: completed/exit0,82.51365973614156s, whole group closed, diagnostics clear;4160 files/8 repos,30 SDK Python modules,102 selected IDs. [Исходные подтверждения](canonical-readback/readback-integrity.json).

Fresh Release/O3 build обоих targets Test_PulseLib_StorageComponents и NeuroModelerConsole завершён. [Сохранённый ранний снимок](build-and-running-readback-a1/readback-integrity.json) содержит build receipt, compiled inventory102 и11 completed valid passed cases без отказов; cohort продолжает работать. Это нижняя граница подтверждённого прогресса данного снимка, не финальный результат102/102. SourceRoot c73575fe545b00cc7c9bf170c81c185c30b7026a / Pulse dfb9a98244f91b4f4029d8470465fd40116436ca, Python actor7bd3684732e1d3f7a0aa038d659fd52bc95892bf.

[Независимая проверка Elder](../ElderSharedExportBoundarySdkA2-20261112/PLAN.ru.md) имеет тот же code/cohort, отдельный actor binding и изолированный runtime; A1 launch отвергнут до native из-за избыточного дискового резерва. Окончательная функциональная приёмка на обоих workers ещё не завершена.

После неё остаются большой67-group export в прежние300s и один конечный scientific rerun. Нынешние данные не добавляют сертификат сходимости или научный PASS; весь исходный план частичен.
