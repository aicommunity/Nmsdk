# N1 geometry: переход от численных тестов к полной SDK-проверке

Адресный C++ A/B принят на Elder и M40: исправленная версия проходит 98/98 на каждом сервере; исходная даёт два ожидаемых отказа. [Протокол и границы результата](N1GeometryFairness-20261111.ru.md). Это не результат обучения stock N4 и не завершение этапа 7.

## Проверенное обновление результатов 2026-11-11

Оба Linux SDK-задания завершены: 119/119 объявленных C++ случаев на каждом сервере, 43 gates; errors=[]; все 44 owned groups (outer + 43 children) закрыты, SDK leases released. Сохранённые terminal/readbacks — в тех же ValidationPlans. Компактная публикация всех новых native119 primary и независимое восстановление ещё не выполнены. Старые live-status ниже являются историческими снимками.

M40: свежие восемь stock N4 проб завершены, все observation valid/complete. Все восемь CSV побайтно совпадают с исходными контрольными пробами; это проверка исходного отклика, не обучение или классификация. Elder: аналогичное задание также завершено (54.51 с parent): 8/8 valid/complete, все owned процессы закрыты, lease released. Запуск выполнен после подтверждения закрытия и освобождения lease независимого восстановления старых Train-архивов.

Windows .14: компиляция завершилась returncode=0, но исходный build outcome descendants_remaining сохранён, build_accepted=false. Последующая отдельная проверка закрытого состояния прошла. Набор native100 завершён: expected=observed=100, assertion_status=passed, execution=completed, validity=valid. Это 98 адресных C++ случаев и два model roundtrip, а не 100 научных экспериментов. Scientific worker admission остаётся false. Полная публикация compact primary и контроль полного экспериментального пути Windows остаются открыты.

Новый Classic stock N4/N1 Train на M40 завершился с typed outcome invalid_observation, а не timeout: 613.14 с native, 743.80 с parent, 4 edits, 14 search probes, 18 composite groups / 108 native probes. После роста до L=[54,1,1,1] объявленное окно [1546,1626] кадров не содержит локальной вершины; selection.geometry.validity=missing. Отдельная глобальная omission-диагностика ambiguous не является причиной, возвращённой используемым declared-window измерителем. Требуются визуальный разбор и проверка прогнозирования окон; сертификат null, Test не запускался. Точные readbacks сохранены на ветке codex/timelearner-managed-python-controller, Docs/StructTrain/TimeLearner/ValidationPlans/M40N1AfterClassicTrainA1-20261111. Это отрицательный диагностический результат; научная цель остаётся открытой.

Следующие таблицы и описания активных процессов сохранены как снимок до этого обновления, их нельзя читать как текущее состояние.


Дополнение source review: Pulse362c6653778de61df8a2d81fdf512a8fcd2a09f8 меняет только две строки комментария CandidateCursor в BoundedTraining.h: N1 interleaving теперь не зависит от invalid recovery policy. Алгоритм и runtime не менялись; source SHA выполненных SDK/probe/Train проверок остаётся Pulse5f1a4ac. Эта правка не расширяет runtime-приёмку. Независимый DATA replay нового Classic подтвердил: группа12 valid в recorded/full окнах, группы14/18 missing→ambiguous. Scalar AdvanceUnassignedBurst не поддержан composite/candidate-window runtime2; требуется новый типизированный контракт. [Replay и конкретная постановка реализации](https://github.com/aicommunity/Nmsdk/blob/codex/timelearner-managed-python-controller/Docs/StructTrain/TimeLearner/CandidateWindowRecoveryImplementation-20261111.ru.md).

Контрольный SDK до исправления на Elder завершён: root5ba0a2e81759a28f378117757aa3a5b91f1c57ab / Pulsec10206d5e338792d42b58ab28e48e7364b07e481; полная сборка SDK/Console, выбранные native roundtrip проверки2/2 passed, один leaf gate, source/capture errors=[]; original kernel Result=success/ExecMainStatus=0, outer+child closed. Это не повтор119 и не сравнение качества обучения. [Фактические terminal records](ValidationPlans/ElderN1GeometryBeforeFullSDKA1-20261111/native-sdk-actual-terminal.json). Before runtime готов к дальнейшему matched Console A/B; сама физическая серия ещё открыта.

## Новый неизменяемый SDK subject

- Root `fcfd8bdff149c14cbe67149e996945d122bf954d`.
- PulseLib `5f1a4ac6f9aff208ada7f8bcf62645c9d79a6615`: Core соответствует уже проверенному `5398a5a563d3e358165fa855cd70236032f5b542`; следующий commit обновляет только документацию.
- Остальные шесть gitlinks сохранены из исходной согласованной комбинации. Полные SHA и Git blob/SHA256 каждого файла находятся в `namespace.json` и исходной Git closure.
- На каждом сервере материализованы и проверены 4096 файлов восьми репозиториев. У каждого отдельные source/build/runtime/output; исходники ранее выполненных экспериментов не обновлялись.

## Фактически запущенная проверка

| Worker | Задание | Последнее подтверждение |
|---|---|---|
| Elder-1 | `s07-n1-geometry-full-sdk-elder-a1` | Полный SDK и Console собраны; первый gate принят, native119 продолжается |
| M40 | `s07-n1-geometry-full-sdk-m40-a1` | Полный SDK и Console собраны; первый gate принят, native119 продолжается |

Контроллер собирает реальные `Test_PulseLib_StorageComponents` и `NeuroModelerConsole`, затем исполняет прежний selected native119 cohort с 43 gates и 310 artifact rules. Это проверяет интеграцию нового production codec и поиска с SDK. Численные 98 случаев приняты отдельно; число 119 не следует трактовать как полный список всех тестов binary или обязательную mode/physics/scientific matrix.

Условия и исходные readbacks: [Elder](ValidationPlans/ElderN1GeometryFullSDKA1-20261111), [M40](ValidationPlans/M40N1GeometryFullSDKA1-20261111). `native-live-status.json` — снимок живого задания, не terminal PASS. Сборки не перезапускать без проверки этих же supervisors/owned groups.

У Elder перед запуском свободно 11067531264 B, предыдущие сопоставимые build/runtime/source занимали около 204/162/104 MiB. Новому заданию выделена disk reservation 4 GiB при сохранении physical free floor 2 GiB; оценка выходов 2 GiB. На M40 Data свободно 295793610752 B; reservation 12 GiB. Память, время, владение процессами и неизменность runtime контролирует существующий production runner.

## Сохранённые ошибки подготовки

1. Elder A1 отклонён до native build: ошибочно объявлено короткое имя `Elder` вместо `Elder-1`. Декларация A2 исправлена, исходный отказ сохранён.
2. На M40 первая canonical-проверка обнаружила восемь отсутствующих HardwareLib JSON с кириллицей в именах. Причина — искажение sparse patterns на локальной границе кодировок при передаче запроса. Не ослабляли полноту namespace и не удаляли эти файлы из ожидаемого состава.
3. В обоих новых неисполнявшихся SDK checkout sparse patterns перечитаны из исходного frozen namespace через UTF-8 stdin. Все 356 файлов HardwareLib сверены по SHA256; commits и байты исходников не менялись. Повторная полная canonical-проверка прошла на обоих workers. Исходные отказ, namespace diff и before/after pattern hashes сохранены.

## Следующие условия приёмки

Нужны terminal native119, закрытие всех owned groups, освобождение leases и compact primary. Только после проверки сборки и регрессий — физический Console A/B исправленного N1, свежая all-input verification и отчёты реакций на паттерны. Прогноз задержки не заменяет измеренный закреплённый пик. Бюджет поиска и timeout не являются Exact или PhysicalInfeasible.

На Windows .14 через Git подготовлен тот же SDK subject: независимо сверены 4096/4096 файлов и восемь чистых repositories без alternates. Запущена отдельная сборка `TimeLearner-windows-n1-geometry-full-sdk-build-a1`. Подтверждены активная задача, owned cmd PID15964/creation FILETIME134388369282676342 и реальные процессы cl/Ninja/CMake. [Декларация и readbacks](ValidationPlans/WindowsN1GeometryFullSDKA1-20261111). Квота Windows Job — 4 GiB, compiler parallelism=1, установка зависимостей выключена. Финального результата сборки ещё нет.

Таким образом, три машины действительно выполняют вычислительную проверку: две — native119 после SDK-сборки, третья — MSVC compile/link. Windows ещё не допущена к полному научному pipeline; пользовательский `C:/Projects/Nmsdk` не менялся. Сохранены ошибки транспортного помощника до checkout/compile: пустой SSH exit255 из Node-контекста, отказ импорта локального модуля при исходной process execution policy и ошибочная замена токена SHA в команде проверки pack. Root/Bin завершены только после проверки уже импортированных packs и fresh/unborn состояния. Использована process-local RemoteSigned; глобальная policy не менялась. Итоговый полный namespace-проверяющий механизм оставлен без ослаблений.

Полностью принят по-прежнему только этап 0 исходного плана; этапы 1–12 остаются частичными. Ветки опубликованы отдельно; develop merge ожидает соответствующей приёмки, выполняется через `--no-ff`, сначала child, затем root.
