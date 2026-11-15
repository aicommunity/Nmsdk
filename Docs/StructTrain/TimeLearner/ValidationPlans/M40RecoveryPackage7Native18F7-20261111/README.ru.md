# Точная UTF-8 проекция SDK

F6 отказал до сборки: canonical_source_projection_changed. При чтении старых
транспортных JSON без явного UTF-8 Windows использовал CP1251. Восемь имён
каталога HardwareLib испортились, и соответствующие файлы не материализовались.
Git commits и содержимое blobs не менялись. F7 читает реестр и namespace как
UTF-8 и доставляет полную новую отдельную проекцию4127 файлов восьми репозиториев.
Исходный F5 и контрольный F6 не изменяются. Native cohort18 и исходный
bdefc540/Pulse1110808 сохранены; новые build/runtime/output каталоги относятся F7.

Canonical preparation принята за81.47s:4127файлов,29same-SDK imports,
18cases/18leaves. Outer закрыт, lease released. Native controller запущен
с supervisor1357256/start349355548; outer1363178 и cmake1363682 реально
выполняют свежую Release SDK сборку. Компиляция и сами18 cases ещё не приняты.
Предыдущие source/runtime не изменяются.
