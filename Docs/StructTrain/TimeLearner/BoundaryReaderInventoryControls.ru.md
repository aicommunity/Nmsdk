# Раздельные отрицательные контроли пустого реестра и отсутствующей ссылки

H12 rootfd8a10b02797ceace0eb87e0d9de4e36bd1e9e62/Pulse54516bcc0aa7b0437c68f818598a19788e20eb55
прошёл адресные6/6 и full native213/213. Readers86/87: единственный failure
CapacitanceBoundaryEvidenceTest.test_missing_capture_witness_is_rejected.
Полная квитанцияeb0441f31b9ba51155a14e4705e27d75786dbe3b сохраняет not_accepted.

Production auditor сначала требует непустой C-history registry. Когда capture
и current имеют общий единственный witness, удаление capture оставляет пустой
registry и корректно даёт invalid_capacitance_boundary_inventory. Исходный test
ошибочно ожидал missing_capacitance_boundary_witness и для этого другого случая.

Исправление только в тестах, без изменения auditor/численных данных/допусков:

- Missing-capture control заменяет capture_witness_id на заведомо отсутствующий
  корректно сформированный ID, сохраняет весь непустой actual registry и требует
  точную missing-reference диагностику для каждого package. Ни один fake witness
  не создаётся. Это работает и при общем единственном capture/current witness.
- Отдельный empty-inventory control очищает registry каждого из12 actual
  completed/stopped packages, пересчитывает envelope digest и требует точную
  invalid-inventory диагностику. Корректный общий capture/current witness
  исходной модели по-прежнему разрешён.

Требуемый повтор: те же опубликованные primary CSV/model/graph packages H12,
новый isolated Python source из Git, полные88 readers без skips/errors/failures.
Повтор C++ обучения не нужен для исправления Python test expectation. В составе
native Cursor A/B общий reader gate станет105 (88 +17), с отдельным полным
213-case native verdict и точными waveform hashes. Все исходные этапы0–12 и
остальная матрица сохраняются; native success не заменяет reader acceptance.

На момент фиксации кода повторная серверная проверка ещё не выполнена.

Прямая проверка всех12 H12 packages показала по одному общему capture/current
witness: этот transport corpus не включает изменение effective model между
reference capture и export. Поэтому первый неподтверждённый draftdafecee16,
требовавший multi-witness fixture, исправлен до запуска проверки: missing-link
контроль теперь меняет ID на отсутствующий, не удаляя единственную запись.
Нельзя считать этот corpus доказательством multi-revision boundary transport;
для этого остаётся отдельный реальный C-edit/growth native контроль.


## Повтор H16 подтверждён на первичных данных H12

Reader source90c4074a6d2049b298fd923052112e738db9ae3b:88/88 без failures/errors/skips.
Evidenceaeb9664b092332555d41eefd0ac8de5fd63cc9b4:10 members/24678 compressed
bytes и400 точных Git source hashes независимо сверены. Исходный H12 пакет
eb0441f31b9ba51155a14e4705e27d75786dbe3b:2259 members/32323202 bytes сверены;
C++ target6/full213 положительны, первоначальный reader failure остаётся
not_accepted в своей неизменённой квитанции. Новый анализ не пересчитывал модели.
C++ sources/tests, child gitlinks и production Python auditors совпадают;
из Scripts изменён только указанный test module с двумя отдельными controls.

H15 native Cursor worker отказался до сборки, поскольку первоначальный H12
общий gate не был принят. Evidence86914b5cdc115858dc5e8aded1502281bd47a319:
6 members/1068 bytes независимо сверены. Это корректный fail-closed переход,
а не неуспех Cursor runtime; следующий A/B должен явно требовать составное
доказательство native H12 + corrected readers H16, сохраняя обе версии source.


## Schema4 reader backward compatibility, H18

Reader root `ab95ba64323114f9b8a3fb05cdb46527c20d452a` (production native
 auditor7) проверен отдельно на неизменённых schema3 H12 данных. Native source
остаётся `fd8a10b02797ceace0eb87e0d9de4e36bd1e9e62`, evidence
`eb0441f31b9ba51155a14e4705e27d75786dbe3b`; исходный overall not_accepted не
переписан. Результат88/88, без failures/errors/skips. Новый C++ код rootab95
не считается проверенным этими старыми primaries.

Evidence `12dcdef6ee05c8a9ebab25740021f81a7920b8d7`,
[пакет](../../../Reports/StructTrain/TimeLearner/s07-boundary-readers-schema4-h18/bundle.json):
независимо сверены10 archive members /25536 compressed bytes и416 точных
Git source hashes. Это закрывает адресную backward-reader проверку schema4
на полном88-control corpus; ASan/native C-search, multirevision roundtrip,
весь physics/mode corpus и научные эксперименты остаются отдельными gates.
