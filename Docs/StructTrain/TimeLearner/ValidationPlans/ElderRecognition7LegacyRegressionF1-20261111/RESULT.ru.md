# Регрессия recognition reader:14/14

На Elder-1 sourceca8be945377d9833a789a847ee5b7cae9241050f прошёл14
объявленных production reader/CLI проверок без failures/errors/skips.
Использованы восемь настоящих ранее сохранённых recognition models и322
исходных файла корпуса s08-recognition-normal-a4/native. Их fingerprint
fb0b7b3811d03873e60a644d47540442513872d1ce4f0de91d387862ad18ef5b
проверен до и после задания. Whole cgroup закрыта, собственный lease released.
Два Git lazy-fetch предупреждения сохранены, operational diagnostics needs_review.

Проверяются прежние conversion/complete frozen transport, реальный CLI,
изменённые capacity/storage/threshold/factor, повреждённое наблюдение,
исчезнувшие frames, изменение frozen model и запрет переноса solo certificate
на recognition. Это compatibility regression на старом настоящем корпусе.
Она не подтверждает новый source7 Branch/N1 reference dispatch и новый
coherent stopped-to-completed negative control: для них готовится native10
corpus, без synthetic fallback. C++ converter/import и научная классификация
этим Python прогоном не выполнялись.

Первичные records в completed сохраняются без изменения bytes; размеры и
SHA256 перечислены в readback-integrity.json.
