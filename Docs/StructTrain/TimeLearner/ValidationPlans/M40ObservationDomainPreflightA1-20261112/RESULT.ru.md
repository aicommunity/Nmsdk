# Полный записанный домен:приёмка5/5 — M40,12.11.2026

**5/5 PASS**,без skips/errors/failures:четыре declaration regressions и один integration test с двумя настоящими native preflight Classic/Branch. [Unittest](completed/worker/validation/unittest.log), [result](completed/worker/validation/result.json). Source/actor309412edc57b60d18cc7b01ae205ec3f223a945c, package6736f8183b8208f8cfe9898d5a1ce84c504daf1252f3c5437d2e0241c494e7c9. Native SDK8362/Pulse111/runtime61f3e2f0 неизменен.

Public prepare-full-window создал plan3/config8. Это версия Python-плана, **не новый ControllerVersion/StructureBuildMode**. Реальные native preflight подтвердили полное равенство исходных stock graphs,2000Hz, N4/N1 и прежнюю физику. [Classic](completed/worker/native-full-domain-preflight/Classic-stock-cold8-N1/index.json), [Branch](completed/worker/native-full-domain-preflight/Branch-stock-cold8-N1/index.json). Train не запускался.

Declaration checks подтверждают:исходные model/target/reference capture windows/амплитудные цели/tolerances/search budgets не меняются; полная область0..sample_count−1 не сдвигается при измененииL/Ns/Rs/C; повреждённый input inventory/reference domain/source digest отвергается. Native preflight подтверждает применение и допустимость конфигурации/графа, но ещё не измеренные live proposals нового Train. [Сформированные jobs](completed/worker/native-full-domain-preflight/prepared/index.json).

[Outer result](completed/controller-result.json), [closure/released lease](completed/closure-and-reservation.json):вся группа закрыта, lease released, diagnostics clear. Source/tool/fixtures before/after побайтно совпадают, heartbeat_errors отсутствуют. [SHA256 raw readbacks](completed/readback-integrity.json).

Следующий допуск — новый реальный cold Train с plan3:проверить фактические candidate frames полного домена, measured assigned basins, свежую верификацию всех inputs и честную причину остановки. Старый Train invalid_observation не переписывается; ни Exact, ни8/8 этой приёмкой не заявлены.
