# Branch N0 report A1: unit прошёл, общая аттестация отклонена

Job s11-stock-n0-branch-report-m40-a1 закрыт; unit1/1 PASS313.294с, но outer process_error342.7854298199527с при returncode0. Причина `runtime_content_changed:/usr/lib/x86_64-linux-gnu/libc.so.6`; runtime_provenance=invalid_or_incomplete_runtime. Это **не принятый report gate**. [Оригинальный controller result](completed/controller-result.json), [unit log](completed/worker/validation/unittest.log), [closure](completed/process/whole-group-closure.json).

dpkg на M40 обновил libc6/libc-bin2.39-0ubuntu8.9→2.39-0ubuntu8.12 14.11.2026 в06:23:48–49. Текущий libc SHA256755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a. [Runtime до изменения](completed/process/runtime.json) сохранён без исправления hashes. Проверка процесса обнаружила реальное изменение среды, а не SSH/VPN ошибку.

Renderer завершил построение всех пар исходной восьмипаттернной Branch N0 матрицы; [manifest](completed/worker/tmp/stock-n0-frozen-gallery/manifest.json) и [analysis](completed/worker/tmp/stock-n0-frozen-gallery/analysis.json) сохранены как сведения отклонённой попытки. Unit PASS не подменяет отказ общей аттестации. Native frozen observations не запускались заново и не менялись. Новый read-only report A2 объявлен после обновления среды; старое задание и его runtime не перенастраивались. Результаты активных native SDK/threshold jobs требуют отдельных проверок; успешность им автоматически не приписывается.

Producer466c03463213a0f71cff3db0854ff1fdc685c9b0, pack176719B SHA2563ccb8e6ce1dca05407eb4d0c4ae95549cea8f1add9acadca5e8aa973305bf7ca. Raw receipts импортированы буквально; причина process_error не изменена.
