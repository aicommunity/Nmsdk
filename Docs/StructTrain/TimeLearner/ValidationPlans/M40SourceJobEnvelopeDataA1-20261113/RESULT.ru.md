# Byte-exact source envelope: четыре проверки пройдены

s10-source-job-envelope-data-m40-a1 на M40:4/4 passed за2.250s собственно unittest, без failures/errors/skipped. Внешняя группа закрыта, lease released. Code Roote2e5503a4ba0476b91561ac48a6aa3a7716147e2; Tool7bd3684732e1d3f7a0aa038d659fd52bc95892bf. Замороженные controls и исходные completed-readback сохранены рядом, без повторной сериализации. Producer Git96643dc79254ed75ba62c4543701d21ae227a4c5.

Проверены12 реальных input/job.json и native/job.json из шести завершённых Classic/Branch Console процессов A4. Оба production layout — Python indent2 и Qt indent4 — прошли побайтное восстановление. Исходные документы4,515,087–7,907,637 bytes представлены recipe3,147–3,699 bytes плюс общий неизменный reference source document. Это размер только envelope, не полный размер архива с reference/primary.

Отвергаются изменённый reference/cache binding, повреждённые prefix/suffix и original digest, неизвестные schema/fields, повреждённый base64. Неподдержанный layout или отсутствующий source_stopped остаётся literal.216 JSON fixture files остались неизменными. Численные/native расчёты не выполнялись, scientific verdict отсутствует.

Полные исходные fixture bytes доступны в [ранее опубликованном компактном A4 corpus](../M40BurstReadbackA4PrimaryA1-20261113/RESULT.ru.md). Для завершения компактной N4 публикации ещё нужны recipe index с закреплённым source dependency, восстановление полного namespace и production audit восстановленных файлов. Эти4 проверки не закрывают всю инфраструктуру публикации и не заменяют actual-file проверку большого N4 job.
