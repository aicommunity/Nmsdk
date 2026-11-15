# Полная проверка coordinator schema1/schema2

06.11 завершены16/16 production unittest cases без skips/errors/failures,
40 различных actual native phase units. Обе схемы использовали один immutable
SDK2e/Pulse12d и прежний executable. Classic/Branch ModelSpec1/2 положительные
cold Train → boundary → continuation → export → measured calibration → frozen;
N0/N1 stopped controls не запускают export/Test. Продолжение завершённого
pipeline не создаёт новых native units и не меняет binding/learned-state bytes.

Для8 соответствующих случаев ConditionSpec fingerprints совпали;1456 исходных
CSV обеих схем повторно проверены на worker и побайтно совпали попарно.
Это протокольная эквивалентность двух схем orchestration, не независимые
научные повторы и не полная effective-factor attestation.

Tool/source root `83a82844a6792e23f39106d1d3f41e8638920077`, compiled SDK
`2e0618110a9abb48b94f6edc6b63c51f829ec810`, executable SHA256
`b2d98c8f85be0ff5d87769ddd4285bbc2ee2fc8b39609d2bd4833149865c5153`.
Data commit `2a23583be3a5bec914d8e5ddd616ec573dd2624f`,4505 primary members,
18677660 xz bytes, SHA256
`abd8ec1f72e3e70c5afb47ce11073b90adc72d832e22ba7c0dcccc9109c5ffaf`.
Все members и341 tool/fixture hashes независимо сверены. Fresh closures40
native groups, unique PID/start/boot identities, loaded binary и освобождённые
case/global leases подтверждены при публикации.
[Receipt](SharedControllerNovember6Verification.json).

Предыдущий A1 отказ из-за строки вместо Path в временном producer сохранён;
он завершился до native work. A2 исправляет только producer, не тесты/модель.
Данные доступны в Git. Полный pending C++ срез ещё не принят: исходный общий
ASan133 дал132 pass/1 output-directory assertion failure. После адресного
исправления runner полный свежий gate выполняется отдельно. Прежний отрицательный
verdict не заменяется этим coordinator PASS. Этапы1–12 остаются частичными.
