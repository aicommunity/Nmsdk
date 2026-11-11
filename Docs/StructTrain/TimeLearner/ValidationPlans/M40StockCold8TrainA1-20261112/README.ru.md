# Настоящий строгий N4 cold8 Train — M40 A1,12.11.2026

Предшествующая приёмка:stock cold8 preflight5/5, свежие исходные Classic/Branch graphs точно совпали с исходным stock physical identity. Native SDK8362/Pulse111, runtime61f3e2f0; новый Python harness c2c837e14 не изменяет C++/физику/поиск.

Два независимых unittest cases запускают фактические холодные Classic/Branch Train через public CLI. Стандартный порядок unittest запускает Branch первым; каждый case имеет отдельные native processes, cold graph и выходной каталог. Сохраняются2000Hz, N4/N1/CapturedPerInput, Sync0.02, abs amp1e-5/relative0, target[0.01,0.08,0.16,0.24], L1/Ns1/Rs86MΩ, anchor N−1 и stock profile без LTMembrane. Recovery:advance_rejected_candidate_window, исходный invalid budget4.

Нативный бюджет каждой попытки:128 search probes,1280 edits,128 candidates/input,4 sweeps,1800s wall/7200s model. Измерительные и первичные лимиты берутся без изменений из принятого prepared plan2. Дополнительные120s покрывают только запуск/stop/export процесса и не увеличивают search budget. Внешний controller:7200s,2GiB; native child:4GiB/tasks64; общий output budget4GiB/floor2GiB.

Вход:10JSON принятого prepared plan2; никаких learned-state imports. Перед каждым Train снова выполняется native preflight и полное сравнение cold identity. Проверки требуют корректно завершённого процесса, валидного package audit и неизменной физики, **не требуют Exact/8из8**. SearchUnresolved/BudgetExhausted/InvalidObservation не переименовываются в сходимость; scope PASS harness не является научным verdict. Test/калибровка в этом задании не выполняются. При ошибке сохранены native primary и CLI transcript; второе unittest case не исключается автоматически.

Результат до завершения и независимого аудита не принят. Работающий runtime/source не изменяется; timeout наблюдения не служит основанием для перезапуска.
