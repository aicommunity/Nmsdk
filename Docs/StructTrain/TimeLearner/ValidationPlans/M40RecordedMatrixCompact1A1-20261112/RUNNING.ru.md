# Compact actual-data roundtrip запущен

Job `s11-recorded-matrix-compact1-m40-a1`; source `3f5086df45aa2f03e222d4379d39cb231a4bda88`, Tool40e28802. Supervisor PID442290, actual main PID445270; unit `timelearner-dc15d251-8c78-46e0-a119-9200449b8e8d.service`, invocation `cc140195171744b2a959925080a77093`, kernel active/running. Проверка начата после принятия42/42 guards. Параллельный full-matrix gallery job остаётся отдельным read-only потребителем исходного A2.

Первая попытка dispatch завершилась FileExistsError на общем launch.log до Popen; target job directory тогда отсутствовал, расчёт не начинался. Повторный dispatch использовал отдельный launch-compact1.log и тот же ещё не созданный job ID. Исходный журнал42/42 не перезаписывался.

Ожидаемые outputs после приёмки: `worker/tmp/recorded-matrix-compact-primary/{bundle.json,primary.tar.xz}`, полное восстановление в `worker/tmp/recorded-matrix-compact-restored`, численный readback `worker/tmp/recorded-matrix-compact-readback.json`. До terminal success/closure/source equality и полного rescore результат не считается принятым и не публикуется как окончательный scientific primary. При потере связи сначала проверяется сохранённый binding; существующее задание не перезапускается по timeout наблюдателя.
