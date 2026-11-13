# Холодное Classic N4/N1 обучение запущено

M40 s07-n1-coupled-classic-cold4-m40-a1, исходный административный PID2743327. Проверен именно созданный kernel handle: execution=running, all_processes_closed=false; unittimelearner-ac1095f3-22b0-4bc7-a793-2f117b354be8.service, invocation872e4b3cc34b4c89b4fd215f797f72c5, initial_main_pid2746661, start_ticks368362417. При потере связи повторный запуск не разрешён до проверки этого handle.

Source/runtime — принятый coupled SDK74e5/Pulse7c6c, runtime105ccc46. Native recovery4/probes128/edits1280/candidates128/sweeps4/wall1800s; finalization300s отдельно. Прежний Classic recovery16 не считается same-budget A/B. Использован существующий production-prepared Classic job без изменения; request SHA2560a5c0fbe7370d14e39c198b5019a10c91e703eda09ee9f31f354718b7b01b5ab. Control commitc1d8d95a1d45a098b85d946173047f234cb3bae5; корневая фиксация условий1a66a646eee5c799876d5b192d02e7bb114eb506.

[Постановка](PLAN.ru.md), [действующий job](classic-job.json), [launch readback](launch-readback.json), [наблюдение handle](active-observation.json). Это подтверждение начала выполнения, не training convergence и не научный результат. Test и подбор порога автоматически не запускаются.
