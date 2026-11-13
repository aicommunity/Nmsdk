# Cold Branch N4/N1 coupled-search: обучение выполняется

M40 s07-n1-coupled-branch-train-m40-a1, control ea3f6f5f6dc562b9b137a676976c7aabb081c158. Source SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, actor181d4d1980423ad82edb9839a3d3fe77f118e6a0, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. [SDK93/93 принята до запуска](../M40N1CoupledSdkA4-20261113/RESULT.ru.md).

Production prepare_recovery(full_observation=True) использован штатно. [Четыре исходных prepared files](controls/unchanged-prepared-files.json) — selected Branch job, два initial identities и reference-origin — побайтово совпадают с baseline. Все scientific budgets/tolerances, CapturedPerInput и fixed anchor сохранены; unused Classic не запускается. [Plan](controls/PLAN.ru.md), [declaration](controls/fixture/declaration.json), [runtime](controls/fixture/runtime.json).

Проверены живые outer и native kernel bindings; native cold preflight completed/closed1.716s. На промежуточном снимке записано145 live raw-trial CSV: это признак реального расчёта, не сертификат полноты/качества всех проб. Во время расчёта имена raw-trial-N.csv; при финализации они могут быть переименованы train_stopped_trial_N.csv. Мониторинг не должен объявлять отсутствие данных из-за старого prefix.

Outer unit timelearner-f7ae7a25-4736-490b-a1a2-6c7401d8eb66.service/invocation c54ed2606d4f46d7b2838d820930c74e, binding87fa1d74eeb0eca2f8bc8c51e84e3c23b8627799be1b8407f5568be89f171dad. Native train unit timelearner-84da06b3-7a48-4104-8733-5b69251c0c3e.service/invocation d72300d4d30e49a6a6bb1981b932da65, binding2e0e2835836af56348cfbdc3bd1ec2a81569094a9ffe593a6df2b52e342fffc4. При потере связи сначала проверяется тот же handle, задания не перезапускаются.

Outcome/сходимость/классификация ещё не установлены. Требуются закрытие процесса, complete raw DATA audit, фактические candidate residuals и all-input certificate. Sign bracket старого local-turn A3 и SDK PASS не заменяют исход этого нового варианта. Ни порог, ни scientific budget не увеличиваются; SeriesD не возобновляется.

Controls producer2ec757e72cc9f37c2f70b517ff4a8081fdb3c42f, pack26629 bytes SHA2564861e2e073cbeda49fa9d7b265407dacff137b44c97055a80e4cda6f1fc161eb. Raw launch receipts сохранены отдельно; неисполняемые декларации заменяют launcher copies в Docs.
