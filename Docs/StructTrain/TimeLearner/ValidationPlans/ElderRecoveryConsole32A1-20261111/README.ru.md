# Native32 на Elder: одинаковый код и cohort, отдельная сборка

Source8362d58f/Pulse1110808,4132файла8Git trees. Cohort32 и все146artifact rules побайтно/семантически сохранены с M40; контроль4active-Build,7recovery Console artifact,11legacy wire и10recognition. Новый source/build/runtime/output; старые runtime не меняются.

Серверные отличия явны: Elder resources-bin8cb-native-archive-move-normal-a1 и framework-initial-threshold-normal-a4; quota slots1, память24GiB. Memory reservation8GiB, leaf8GiB/tasks128,21600s whole/900s leaf, физический floor2GiB сохранены. Disk reservation2GiB вместо M40 12GiB — ограничение роста нового job, не критерий обучения. Для ориентира предшествующий native10 имел~959MiB peak growth; места до подготовки3.8GiB, фактический расход контролируется. Удалены только доказанные derived restore copies и неиспользуемый предыдущий build; runtime и архив проверены до/после и сохранены. Нужна приёмка canonical и повторная проверка места перед численным запуском.

Этот набор проверяет технические fixtures N2/Sync0.2, не заменяет научный N4. Подготовка не означает успешную сборку или32/32.

Уточнение бюджета по actual readback: M40 build212537344bytes/runtime164343808/output348852224 на промежуточном снимке; прежний Elder native10 peak959336448bytes. Reservation2GiB сохраняет запас для полного32case набора и не меняет146artifact rules/число случаев/математические допуски. Initial3GiB была постановкой до проверки capacity preflight, runtime с ней не запускался. Сохраняется строгая проверка initial free >= reserve2GiB+floor2GiB и мониторинг фактического прироста.

[Review удалённых caches](derived-cache-retirement-review.json):528cached files являются archive copies (один — byte prefix interrupted extraction),2418files старого build — воспроизводимые объекты; CMakeCache полностью сохранён в Git primary. Active users не обнаружены; old job cgroups closed/leases released. [Result](derived-cache-retirement-result.json): freed499085312allocated bytes, free4452347904bytes. Уникальные models/primary/original outcomes иruntime не удалялись.
