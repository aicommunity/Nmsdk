# Параллельная проверка rejected-search на трёх машинах

## Предмет проверки

Одна версия SDK: root `04f830a3a0f6c36cb9eb22b48075aa545b8aeb6c`,
PulseLib `558b9661c96efdd4dd1d44037a7c536ef29c8c72`; полный namespace —
4103 файла / восемь репозиториев. Исходники доставлены через Git в новые
изолированные каталоги. Пользовательская Windows-копия `C:/Projects/Nmsdk`
не изменяется.

Elder и M40 выполняют Release SDK build и одинаковый набор native29:
22 новых production integration cases допуска завершённого rejected Search,
четыре прежних valid factory cases, два реальных model/package roundtrip и
чтение сохранённого старого package6. Последний случай необходим для проверки
совместимости valid semantic proof ID, которую два новых writer/reader сами
по себе не доказывают. Полная матрица исходного плана этим набором не закрыта.

Windows .14 параллельно выполняет отдельную MSVC SDK-сборку той же версии.
Её исходники проверены: 4103/4103 файла, восемь точных HEAD, clean, без alternates.
После dispatch подтверждены один живой экземпляр scheduled task и настоящие
процессы cmake/ninja/cl. Dispatch не является завершённой сборкой. Следующими
нужны проверка исходного build outcome, закрытия процессов и runtime identity,
а затем отдельный native gate. Допуска к полному научному pipeline ещё нет.

## Принятые предварительные проверки

* Elder: canonical preparation A2 — completed/0, 67.34 с, whole group closed.
  Native supervisor PID 2001249, start_ticks 394916261; при status-проверке
  supervisor live и outer kernel cgroup running.
* M40: canonical preparation A3 — completed/0, 83.03 с, whole group closed.
  Native supervisor PID 3666175, start_ticks 345474126; при status-проверке
  supervisor live и outer kernel cgroup running.
* Windows: attempt `windows-rejected-search-full-sdk-build-a1`,
  specification blob `65514014eb83851fad7db229fede1349a20e71ae`.
  Наблюдавшиеся compiler PIDs — снимок, не основание для последующего kill.

Декларации, исходные отказы и launch identities находятся в
`ValidationPlans/{ElderRejectedSearchAdmissionA2,M40RejectedSearchAdmissionA3,WindowsRejectedSearchAdmissionA1}-20261111`.
Текущий terminal следует проверять у того же supervisor/task; не перезапускать
задание при истечении времени наблюдения.

## Сохранённые ошибки подготовки

1. Linux canonical A1 остановлен до сборки: namespace SHA посчитан по CRLF,
   тогда как Git blob содержит LF. В A2 все входные SHA дополнительно сверены
   с настоящими Git blobs. Контракт проверяющего механизма не ослаблялся.
2. M40 control checkout сначала отказал из-за отсутствующего `.gitattributes`
   Git object. Импортирован отдельный Git pack с attributes, exact commit и
   чистота checkout проверены. Данные/код не заменялись.
3. M40 canonical A2 остановлен до сборки: в protected runtimes был объявлен
   before-SDK runtime, существующий только на Elder. A3 убирает только этот
   отсутствующий M40 путь; остальные защиты и source subject сохранены.
4. Windows SSH transport из Node-контекста вернул пустой exit255 до подготовки.
   Отдельный запуск того же помощника через рабочий shell доставил Git packs.
5. Windows первоначальная full namespace verification выявила пропущенные
   HardwareLib файлы с кириллицей: sparse JSON был декодирован с неверной
   native encoding. В ещё не использовавшемся SDK перечитаны только sparse
   patterns из того же Git blob с явным UTF-8. До/после hashes patterns:
   `2a6c1f0903959e1e71b325069af6722a13b72ac232ba26752d00d88fed9cf7cd` →
   `fa864f12a998579a29f805e2b715b3d9c2a2aeaaec86d4cbf0baa48a344ac3b6`.
   Затем production `Test-PreparedSdk` подтвердил все 4103 файла; исходные HEAD
   не менялись. Сборка начата только после успешной полной проверки.

## Ограничение результата

На этом снимке все три машины заняты вычислительной проверкой; итогов нового
native29 и новой Windows-сборки ещё нет. Это не три параллельных научных кампании.
Текущая реализация лишь создаёт закрытый допуск завершённого Missing/Ambiguous
Search. Передвижение конечного search cursor, новая версионированная recovery
policy, persisted events и независимый replay ещё требуют реализации и проверки.
Runtime2 остаётся retry-only; новый stock N4 Train с recovery не разрешён.
