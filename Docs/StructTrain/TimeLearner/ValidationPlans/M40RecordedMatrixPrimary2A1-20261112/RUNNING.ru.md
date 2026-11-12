# Независимое чтение и галерея запущены

Job `s11-recorded-matrix-primary2-m40-a1`, source `557decacf65bb5f13af43cb5195093e890360411`, controller Tool40e28802. Supervisor PID345224; проверен реальный main PID348108, unit `timelearner-f94bb0dd-d43f-44af-9aa5-efdaed580f79.service`, invocation `05e78845fa4d4044a8015b9fad14a3d5`, active/running. Это Python DATA replay и рендеринг, без нового Train или изменения моделей.

Первичные файлы закреплены fixture inventories: 91 JSON исходного запуска, все 7 staged inputs, 18 controller JSON и отдельный raw runtime. Исходный Console job предварительно проверен как завершённый с original exit0, двумя закрытыми child groups и освобождённой lease.

Лимиты нового задания: 6 GiB RAM, 64 tasks, 21600 s, output до 12 GiB. Полные HTML/PNG/SVG/PDF будут в `worker/tmp/recorded-n4-diagnostic-gallery`; это кэш M40. Принятость двух tests и визуальная приёмка пока не заявляются. При потере связи задание не перезапускать: сначала проверить этот binding и controller-result/worker terminal.
