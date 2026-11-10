# Полный compact primary native119 — 11.11.2026

Обе закрытые серии SDK22e9714/Pulse165 прошли119/119 cases,43 leaf gates и310 artifact rules. Теперь полностью сохранены исходный result tree и controller tree каждого worker:4826 обычных файлов+42 проверенных glog aliases,4868 полных archive members. Обе исходные outer+43 child группы проверены закрытыми до и после сжатия; упаковщики завершены, leases released. Исторические model/test statuses не переписаны.

| Worker | Expanded bytes | XZ bytes | SHA256 |
|---|---:|---:|---|
|Elder|1164189933|8934992|0404e830a1a00c00f2397e9094c2953dcdef71ebffb603ef4ce500b8d9df7850|
|M40|1164428569|8917304|f9196adc86ed760dcc0b1fe85c96500ac052f57f885a379f4fe797cee47d0902|

Полные первичные модели, traces, JUnit, события и controller evidence находятся в `Reports/StructTrain/TimeLearner/Native119-20261111/{Elder,M40}`: bundle.json,primary.tar.xz и исходные collection proof/controller/closure/terminal. Передача выполнена Git packs, после восстановления файлов сверены SHA и размер каждого archive.

[Elder — манифест, closure и Git-передача](ValidationPlans/ElderNative119CompactPrimary-20261111/collection-and-git-stage.json).

[M40 — манифест, closure и Git-передача](ValidationPlans/M40Native119CompactPrimary-20261111/collection-and-git-stage.json).

Перекрёстное восстановление принято: M40 прочитал архив Elder за59.116762s, Elder прочитал архив M40 за67.394192s. На каждом проверены4868/4868 members,43 JUnit gates/119 уникальных expected cases,310 исходных artifact rules и13 настоящих package states. Остановленные/default-sync nonexact и stopped-after-exact состояния сохранили null/public-nonexact статусы; source execution authority не создавалась восстановлением.42 glog aliases сохранены как regular bytes архива; при повторении правил учитывался исходный regular/link namespace. Процессы читателей закрыты, leases released. [M40 reader](ValidationPlans/M40Native119IndependentRestore-20261111/actual-result.json), [Elder reader](ValidationPlans/ElderNative119IndependentRestore-20261111/actual-result.json).119 — точная выбранная выборка, не вся mode/physics matrix и не классификационный научный результат. Исходные этапы1–12 остаются частичными.
