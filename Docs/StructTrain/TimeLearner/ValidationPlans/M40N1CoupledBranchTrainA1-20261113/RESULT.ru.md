# Branch N4/N1 coupled-search: локальная сходимость, затем неоднозначное измерение

Прогон M40 s07-n1-coupled-branch-train-m40-a1 завершён. Production CLI/DATA проверка —1/1 PASS,1952.901s; это подтверждение корректности сохранённых данных и честного статуса, а не успешной сходимости всей модели. Native процесс completed/closed1376.077062s, outer completed/closed1976.853124s; heartbeat errors отсутствуют.

Training outcome **invalid_observation**, reason **rejected_candidate_window:ambiguous**, certificate=null, final verification groups отсутствуют. Зафиксировано22 consumed candidate measurements,28 domain assessments,25 edits,54 search probes и5 rejection records. В архиве58 complete logical groups×6 native trials=348 CSV.

## Что получилось

Третий вход (input_index=2, закреплённый третий импульс) впервые в этой серии имеет один реально измеренный кандидат, одновременно выполняющий исходные допуски: timing residual+0.002499999999940883s при SyncTolerance0.02s, amplitude residual−1.496405621637109e−8 при абсолютном допуске1e−5. Относительный допуск выключен. Геометрия[28,28,27,1], Rs[86000000,86000000,21232304.307596028,86000000], Ns=1. Это group48/search88, epoch21; fresh anchor group47/search87. Интерполяция только предложила кандидат, значение получено native расчётом.

Затем второй вход(input_index=1) дал ambiguous в пяти законченных группах(search90/95/99/103/107), исчерпав объявленное восстановление4. Последняя группа58 complete, selection.geometry.validity=ambiguous, reason composite_train_assignment_ambiguous;omission_group_closed. Отсутствие однозначного закреплённого пика не заменяется максимумом всей пачки.

Фактический terminal vector[28R86M,27R21.232304307596M,27R21.232304307596M,1R86M] отличается от локально успешного кандидата. Graph revision0612d586ce9b1403e5a57ee86703f87db2ea6c1a51d9bc798e38e997fa9dea60 совпадает; одной graph SHA недостаточно для переноса результата между разными logical parameter assignments. Production search projection требует также совпадения полного вектора. Ни final state, ни вся модель не объявляются Exact.

## Воспроизводимость

Source SDK root74e5d206d4b619fcf81f77f11b54ebec7b8f0f6e/Pulse7c6c94785af0c83104d348bb3b733ed1f149c8a8, actor181d4d1980423ad82edb9839a3d3fe77f118e6a0, runtime105ccc46bf2d23aa093ee6ec5fb088d9f33faa8e572f8191869f8cc279377a8a. [SDK93/93](../M40N1CoupledSdkA4-20261113/RESULT.ru.md) — адресная helper/controller приёмка, не full CTest/physics matrix.

[Actual job/initial comparison](actual-condition/comparison.json): native job bytes и initial-state bytes побайтово равны baseline producerbc543c15879454a29337edcb05f5226203f9a2af; hashes93556039955e15a3de1ec88b55d546b2f54bb7e680deb3fc1e499799a524c55d и94ba3ec35d540de3961f7c0e9891054fdee0e6a1db031ff3c52569d75b345d9b. Во время сравнения run ещё выполнялся; поле run_is_still_in_progress в исходном receipt не переписывается. Scientific budgets/tolerances, CapturedPerInput, fixed anchor и физика сохранены.

[Original completed receipts](completed/worker/validation/unittest.log), [native execution](case/runs/train/native/execution.json), [manifest](case/runs/train/run-manifest.json), [полный compact primary](../M40N1CoupledPrimaryA1-20261113/RESULT.ru.md). Train producer65592b000927b6bbc74bf34e57fd757887030457; pack171929B SHA2566237163cb47eddc73dceb3220783026b7bd94be1128afac824b4ff9af7c1e0dd. Actual-condition producer6e956338431adce778650058cbc7efd23cb089d9.

[Графики групп48/58 и научный отчёт](../../N1CoupledScientificReport-20261113.ru.md) готовы: read-only report1/1 PASS,4original PNG просмотрены. Frozen классификация этого состояния ещё не измерена; изменение порога или новые8pattern результаты сюда не приписываются. SeriesD не возобновляется. Августовские4/8–6/8 сохраняют исходную доказательность.
