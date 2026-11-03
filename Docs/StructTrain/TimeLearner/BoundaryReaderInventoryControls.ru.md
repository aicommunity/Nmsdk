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
