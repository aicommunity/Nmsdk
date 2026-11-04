# Чистый рекурсивный checkout принятого develop

На M40 заново получен root `e218753e49b12f05708a60a4f22266882f810430`
и все семь точных gitlinks исключительно из origin, без --shared, reference
или alternates. Использован новый каталог на Data; старые source/build/runtime
не переключались. Clone/fetch/checkout и Git connectivity receipts сохранены.
SDK не собирался, численных моделей эта проверка не запускала.

| Repository | Проверено tracked files | Байты |
|---|---:|---:|
|Root|81448|1732648659|
|Bin|15853|2949361136|
|MotionControlLib|145|1879860|
|PulseLib|554|7009993|
|Rdk-BasicLib|74|411046|
|Rdk-CvBasicLib|213|1109425|
|Rdk-HardwareLib|409|4506574|
|Rdk|1838|23148614|

Итого100534 файла. На worker байты каждого tracked file/symlink сверены
с Git blob identity; все repositories чисты. Независимая локальная проверка
сопоставила полное множество путей/объектов каждого tree и заново посчитала
SHA256 Git blobs для всех записей (с кэшем одинаковых objects). Это проверка
содержимого и доступности, не только существования branch name.

[Receipt](FreshDevelopCheckoutVerification.json) содержит точные commits,
counts/bytes и archive SHA. Proof `3adc459e496c710b487b87bc9a77da68e08fbfe1`,
primary4,721,260B, раздел `s00-current-develop-checkout-m40-a1`. Полный inventory
не дублирует содержимое исходников и результатов в Git; они получаются из
своих точно записанных commits.

Проверенный root включает Pulse develop9ec4566, Rdk10e9d05 и Bin99f58da.
Следующая документационная актуализация rootb0e2465 не меняла App/Tests/Scripts/
gitlinks. Будущие algorithm/containment branches этой проверкой не принимаются.
Новая executable closure всё равно требует соответствующей сборки, runtime
manifest и реальных проверок своей области. Исходный план1–12 не закрыт.
