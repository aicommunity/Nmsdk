# Точка продолжения: 29.10.2026, 06:36 MSK

Цель полного плана остаётся активной и не завершена. После сообщения о
восстановлении связи выполнена новая проверка: два подключения Paramiko,
независимый TCP connect (5 с) и штатный Windows OpenSSH (5 с) получили timeout
на `10.245.1.12:22`. Аутентификация не началась. Это не ошибка пароля и не
подтверждение недоступности самих workers. Сетевые настройки не изменялись.

Фактический маршрут Windows: `10.245.1.0/24` через `192.168.192.254`,
`Ethernet 3`, локальный адрес `192.168.192.50`. Шлюз имеет состояние
`Reachable`. Интерфейс AmneziaVPN присутствует, но более специфичный маршрут
выбирает Ethernet. Эта информация описывает наблюдение, а не устанавливает
причину сетевого сбоя. Вопрос о необходимом подключении передан пользователю.

## Сохранённые исходники

Рабочая ветка root и PulseLib: `stage08/posttune-boundary-transaction`.
До этого документального checkpoint деревья чистые, исходники опубликованы:

| Репозиторий | SHA |
|---|---|
| Root | `e15dceba45367c6c23d65272ae335811b775cbd0` |
| PulseLib | `c7266dcb93ec51a765125bc30647cf1b59129c91` |
| Bin | `f5e1d0200127223981daa71da22cf5ee02fdbc60` |
| Rdk | `1812624ff75c60f03ad57c10b379d3e3848590bc` |

Gitlinks соответствуют этим дочерним SHA. Рабочие изменения не приняты в
develop; принятый root develop — `b62127538694a3442771598420fd78fa7e405c8b`.
Не распространять его прежнюю full-suite приёмку на новые изменения.

## Порядок возобновления серверной проверки

Все пути ниже относительны к `/home/user/timelearner-refactor`.
Завершённые native jobs A2 повторно не запускать из-за обрыва соединения.
Терминальный exit 0 и по 14 успешных native cases получены ранее из сохранённых
SSH-сессий. Новая проверка не смогла перечитать серверные файлы.

| Worker | Замороженный source | A2 readback |
|---|---|---|
| `user@10.245.1.11` | `source-order-fixed-a1` | `readbacks/s08-boundary-normal-a2` |
| `user@10.245.1.17` | `source-order-baseline-a1` | `readbacks/s08-boundary-asan-a2` |

1. Проверить source SHA `325052a0802e431f45ed91619c089fbc0eef7922`, PulseLib
   `32dc2e0223cab8adca8280eb1c4586764b6a9c86` и terminal status A2.
   Активных заданий по последним полученным результатам нет; старые PID не
   считать действующими без проверки личности процесса.
2. До смены source выполнить два `test_boundary_evidence` с
   `TIMELEARNER_BOUNDARY_EVIDENCE_DIR=<A2 readback>/native`. Отдельно проверить
   production `audit_probe` для обеих проб каждого из десяти boundary cases,
   byte-exact до/после, XML 14/0 failures и четыре guard scenarios 0–3.
   Сопоставить с полными A1 CSV: ожидается 20 файлов Elder и 8 M40; это
   ожидание, ещё не результат A2 audit. Не добавлять отсутствующие после
   контролируемого прерывания M40 A1 файлы. Использовать новый каталог
   `readbacks/s08-boundary-data-a2`, не перезаписывать исходные readbacks.
3. Опубликовать A1, lifecycle baseline, A2 и независимый анализ через отдельные
   evidence branches Git. Сохранить неудачные/прерванные попытки с их реальным
   статусом. Проверить stored/raw hashes, source/runtime provenance. Не заменять
   старые source SHA новыми и не объявлять SIGTERM memory-error finding.
4. Только затем проверить новый owner-policy API, отдельный runtime/readback:
   root `912ef71b36fbc040c6177a82070a796ee5eb99de`, PulseLib
   `c7266dcb93ec51a765125bc30647cf1b59129c91`. Девять
   `NativePostTuneOwnerPolicy.*` ещё нигде не собраны/не выполнены. Elder normal
   j2, M40 ASan j1; дополнительно затронутые graph/guard regressions.
   Fixture sync tolerance 1 с не является научным допуском нового алгоритма.
5. Независимая Python-проверка root
   `670f2ff79d843d72f0703783cab49defc4159274`:
   `test_condition` и `test_runtime` из пакета
   `Scripts.StructTrain.TimeLearner.tests`. Ожидается 18 methods, фактическое
   число и результат должны быть получены на worker. Эти проверки пока не
   запускались. Затем нужны реальные relocation/roundtrip проверки runtime,
   а не только unit fixtures.
6. Обновить документы и согласованные gitlinks по фактическим результатам.
   Приёмка этих подэтапов не завершает всю candidate transaction, production
   controller integration, calibration, frozen Test или полный план.

В серверных исходниках до завершения анализа не выполнять checkout/build,
который изменит данные проверяемой попытки. Синхронизация только через Git;
слияния только `--no-ff`, дочерние commits публикуются до корневых gitlinks.

Полная карта незавершённого объёма:
[CurrentStatus-2026-10-29.ru.md](CurrentStatus-2026-10-29.ru.md).
Детали границ реализации:
[PostTuneBoundaryTransaction.ru.md](PostTuneBoundaryTransaction.ru.md) и
[ConditionIdentities.ru.md](ConditionIdentities.ru.md).
