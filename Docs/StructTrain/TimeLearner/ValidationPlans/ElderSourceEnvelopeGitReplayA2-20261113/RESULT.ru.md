# Независимое восстановление первичных данных из Git на Elder

Принят ограниченный контроль: 1/1 production test, 4.803 s; whole owned group closed, lease released. Root источников dac0d75de000596ddd0414b0221c33b9669dc6f7; Tool SDK929dbc176a0804910544539aaf79bdc4a02aa82a; control Git de00e5e8650012c6399144f88889da8dd4d63b7f. Исходные receipts сохранены без изменения bytes в receipt; producer Git1df40e1c7bcafc6c18a116b1b15231c0de1dd56b.

На Elder из отдельного чистого Git checkout восстановлен пакет SourceEnvelopeFormatFixture-M40-20261113: 706 regular files, 18 исходных job files, полный namespace712 logical members с проверенными glog aliases. После сверки bytes выполнены шесть production primary audits: Classic/Branch replay/matched/changed. Оригинальные каталоги M40 не использовались, manifests не переписывались. Размер всего нового пакета1,082,331 B против прежнего1,234,243 B. Это проверка хранения/повторного анализа, без нового native execution или научного verdict; большая N4 модель ещё не проверена этим способом.

Предыдущая A1 остановилась на capacity preflight до запуска worker: free2,385,563,648 B не удовлетворяли floor2GiB + output1GiB. Её request/context сохранены в a1-preflight, controls в a1-control. Для A2 сохранены тот же полный тест и floor2GiB, output ограничен200MiB на основании измеренного M40 peak183,144,448 B. Данные не удалялись и проверка свободного места не отключалась.

Контроль не закрывает целиком этапы2/3/10 и не подтверждает сходимость обучения или классификацию.
