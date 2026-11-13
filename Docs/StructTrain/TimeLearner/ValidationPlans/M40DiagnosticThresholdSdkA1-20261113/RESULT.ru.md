# SDK64e / Pulse ea88068: ограниченная приёмка диагностического порога

Сборка завершена. Из10 объявленных и полностью учтённых native cases прошли2 диагностических (ClassicN1/BranchN1);8 ordinary NativeThresholdCandidate cases завершились failure в предварительном обучении: service.Certificate() отсутствует, maximum_sweeps_exhausted, до вызова порогового конструктора. Общий cohort FAILED; закрытие процессов не меняет этот исход. Actual test inventory, JUnit, stdout, terminal и все310 native primary files сохранены.

Диагностические2 случая проверяют остановленную модель, immutable source, единственную разрешённую правку Threshold, сохранение null training/calibration certificates, native import/Build/Init/Reset и frozen trials; ordinary import и повторное построение цепочки кандидатов отвергаются. DATA audit отдельно прошёл5/5. Это позволяет ограниченный диагностический эксперимент с остановленной моделью, но не объявляет весь SDK принятым.

Два ordinary N1_2000 отказа воспроизведены на прежнем Elder SDK92ad/Pulsedfb в том же предусловии. Остальные6 прежних baseline cases не перепроверены; нельзя экстраполировать проверку двух на все восемь. Исправление completed-training fixtures остаётся открытым; научные допуски не ослаблять ради теста.

Все outer/leaf группы закрыты; heartbeat_errors=[] и final_capture_errors=[]. Сборка: root64e18d24f8a6c8d3982c04b7aa9ddb7dfc66871c, Pulseea88068b632007627a8a6bb22afe156fa4035cc2. Controlb0a39031d10a40130f7cf02be5e77cfd72358c6e. 355 исходных Git blobs импортированы без JSON-пересериализации; producer348fe7e6851b85a256a08fdc1a969ffd0f1dd2fe. Проверки не измеряют качество распознавания8 паттернов.
