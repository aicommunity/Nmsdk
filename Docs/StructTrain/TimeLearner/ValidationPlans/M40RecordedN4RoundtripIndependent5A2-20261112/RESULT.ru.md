# Расширенный N4 readback A2: 4/5, provenance отказ сохранён

M40 job `s08-recorded-n4-independent5-m40-a2`, source `b9967e73d0faaf50d848018be926f1d67b75b7c0`. Пять тестов выполнены за533.963 s без errors/skips. Оба полного исходного и экспортированного model7 пакета, summary8, embedded primary и boundary responses прошли production DATA-аудит; qCompress corruption и создание временных рисунков также прошли. Это расширение A1, не новое обучение.

Единственный FAIL — первоначальная проверка controller:36 children вместо2. A2 был запущен до исправления явной привязки; его failure не переименовывается в PASS. Raw result/log/source/fixture snapshots и closure сохранены в `failed/`, все14 blob SHA проверены после записи в Git.

Галерея создана из реальных before/after responses в `readbacks/s08-recorded-n4-independent5-m40-a2/worker/tmp/recorded-n4-roundtrip-gallery`. Масштабы full/response, каждая записанная сома, реальные входные импульсы, разность потенциалов;1920×1200 без downsampling. Это только диагностический active input0 native burst. Отчёт по всем классификационным паттернам этим не заменяется. Выборочные рисунки и визуальное чтение будут опубликованы после собственного A3 acceptance.

Исправление проверяется отдельно A3: правильные controller proofs представлены явным Git fixture, посторонний controller должен отвергаться. Никакого scientific verdict или завершения обучения из A2 не следует.
