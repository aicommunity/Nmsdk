# Native XML прогретого learner: проверка границы Load/Init/Reset

Адресная приёмка завершена01.11: normal и ASan32/32, readers18/16/16 на
каждом worker,64 byte-identical crossworker CSV,1476 автоматически проверенных
PNG и26 прямо просмотренных selected originals. Разделы ниже сохраняют ход
проверки; их ранние pending-статусы заменяет итоговый раздел приёмки.

Fixture расширяет warm Reset контроль16 случаями: Classic/Branch, N2/4,
2000/20000Гц, Parameters-only либо Parameters+State. Whole-model XML
сохраняется после50ms реального отклика с индивидуальными C=1.23nF/Rs=91MOhm.
Затем исходный граф освобождается, новый создаётся через native LoadComponent,
ModelInit и Reset. Не добавляются принудительный Build, Default, overlays,
ручная замена параметров после Load или вложенный Calculate.

Проверяются физические сомы и public readouts до первого тика после Reset,
морфология и индивидуальные параметры. Load/Init может вызвать неявный Reset;
поэтому сохранено фактическое состояние после Init, но сохранение тёплой
динамики до явного Reset не требуется. Режим Parameters+State не называется
checkpoint продолжения посреди пробы: контракт этого теста — сброс динамики.

После Reset повторяется50ms пачка: каждый входной отсчёт должен совпасть,
сома каждой ветви Classic либо общая Branch сравнивается с исходным откликом
с абсолютным допуском1e-12. Это допуск replay-контроля, не tolerance обучения.
Сохраняются source/loaded effective graphs, hot XML, diagnostics, snapshots и
полные warm/replay CSV. Неизвестные LT events или scientific verdict не
достраиваются. Амплитудный/временной критерий сходимости этим не проверяется.

Сначала выполнить реальную сборку/запуск на Elder; compile errors или native
отказы сохранять отдельно. Текущий код зависит от warm Reset исправления,
которое ещё ожидает полной ASan приёмки. Этот тестовый пакет пока не является
доказательством успешного hot Load либо завершения всего этапа4/5.

Первый numerical snapshot d2e851aeb90aa105c3ded598b26a809d9fcf85fe,
Pulse04b234b/Rdk78e51a9b: после исправления получения gitlinks на Elder
пройдены16/16 native XML cases (attempt a2,25.50s). Attempt a1 остановился
до сборки: fetch старой feature-ветки Rdk не получил точный новый merge,
записанный в root gitlink. Это ошибка подготовки,0 выполненных tests,
не дефект модели. a2 получает и проверяет именно каждый записанный SHA.

Для исходной обязательной размерности финальный test package расширен до
N1/2/4/6:32 XML cases. Для них warm и replay окна составляют100ms, чтобы
полностью предъявить и наблюдать N6 пачку. Schema2 явно записывает sample
count и duration. Прежние8 fresh-warm cases сохраняют50ms и schema1.
32-case snapshot требует отдельного запуска; старые16/16 не выдаются
за его приёмку. Cold/hot snapshots и обе попытки a1/a2 сохраняются отдельно.

Расширенный snapshot f01f27d806a1c2a3885bc1581480c550f9bfe9c3 на Elder
прошёл32/32 native cases (a3,116.95s). Глубокая проверка выявила различие
TimeConstant между source-model (после100ms) и loaded-model (после Reset).
В NPulseChannel TimeConstant объявлен ptPubState; Calculate меняет его,
AReset восстанавливает R*C. Это ожидаемая разница фаз, не доказательство
повреждения физики. Например, source0.009999999993439394 против rest0.01.

Schema3 добавляет source-rest-model.json перед первым Calculate, после
начального native Reset. Он сравнивается с loaded-model в той же фазе.
Прогретый source-model и hot XML сохраняются также; их параметры/связи
нельзя игнорировать, а динамический TimeConstant нужно отражать отдельно.
Не добавляется Reset между warm Save и освобождением исходного графа:
проверка reuse после прогретого экземпляра сохраняется. Новый snapshot
требует повторного32-case прогона. Schema2/a3 остаётся исходным результатом
своего снимка и не подменяет новую проверку фазово согласованных графов.

Schema3 numerical source68b802123bcc0ce53c9ce6c4ddef7e38577692da
завершил32/32 native cases на Elder (a4). Независимый production reader
source688e6bb78b7a93d68fb68f53073d8cca1e76c093 проверил все68 case/soma
pairs: полное равенство rest/loaded графов, C/R/всех параметров, связей,
порядка и caches; warm граф отличается только диагностическим TimeConstant,
проверенным как ptPubState, и сохраняется отдельно. Проверены все100ms
warm/replay samples, реальные импульсы, совпадение исходного/replay сигналов,
State flag, размеры и фактическое тёплое значение сохранённой soma matrix.

Пройдены18/18 XML data/corruption tests,16/16 warm compatibility и16/16
loaded compatibility. XML динамическое текстовое представление имеет
ограниченную десятичную точность: при проверке saved warm state учитывается
граница округления максимум6 значащих цифр и шаг записанного токена.
Это не tolerance обучения, не допуск последующего waveform replay и не
обещание точного mid-probe checkpoint. Нельзя переносить этот результат на
произвольные высокоточные индивидуальные параметры без отдельной проверки.
ASan32 и temporal review данного XML пакета ещё требуются; подэтап не принят.

Полный normal primary опубликован commit
59a8e1491b925510299e3c04bed360e000e082d8:
Reports/StructTrain/TimeLearner/s04-hot-xml-current-normal-a1,
536 файлов,501960 bytes сжатого архива. Он содержит schema2/a3 и schema3/a4,
полные native XML/графы/warm+replay CSV и reader18/16/16 receipts. После
получения через Git проверены внешние SHA256 и каждый член архива.
На M40 восстановлен тот же комплект с проверкой536 members и запущен
production renderer для всех68 case/soma pairs. Код экспортирован через
Git archive в отдельный source-hot-xml-report-a1 с200 file hashes;
защищённый источник другого ожидающего reader не переключался. Полный
figure cache остаётся вне Git, выбранные рисунки публикуются после QA.

Ограниченная точность динамического текста native XML не должна автоматически
приписываться versioned ModelArchive: ModelIdentity использует битовое IEEE754
представление F64. Проверка произвольных высокоточных параметров этого другого
пути является отдельным требованием; данный hot XML подэтап её не заменяет.

## Selected temporal evidence review, 2026-11-01

All 1476 PNG files passed automatic coverage, dimensions and checksum checks on M40.
All 26 selected original 1920x960 images were directly inspected: actual input pulses,
response fronts and maxima are readable, and source/replay soma curves visually overlap.
See Reports/StructTrain/TimeLearner/s04-hot-xml-visual-a1/visual-review.json.
The complete cache was not manually inspected. ASan32 and acceptance remain pending.
The earlier pending temporal-review statement above is superseded by this record.

## Итоговая адресная приёмка

M40 ASan source68b802123bcc0ce53c9ce6c4ddef7e38577692da завершил32/32 native
cases за660 wall seconds. Затем immutable200-file reader export root59a8e149
прошёл18 XML +16 warm +16 loaded tests. Полный аудит охватывает68 case/soma
pairs; все64 warm/replay CSV побайтово равны normal. Оба supervisor834822 и
reader838718 завершены, exception отсутствует; final source/runtime guards прошли.

ASan primary8ac617120ab0a58f207f2175ea85ce58b89b2bbd содержит290 членов,
285528 bytes xz. После Git retrieval локально проверены все outer/member
SHA256 и размеры. Normal temporal cache применяется по доказанному тождеству
данных; повторный полный PNG cache в Git не добавляется.

Root acceptance сохраняет PulseLib develop70f467d3b66ea4defdec2f58b84e76b692ab3602
(tree равен tested04b234b/6cfcca0c), Rdk78e51a9b и Bin6304b4a2. Дополнительного
production C++ изменения в этом XML подэтапе нет: добавлены реальные fixtures,
production reader, corruption checks и evidence. Исходная mathematical target
и алгоритм обучения не меняются.

Приёмка относится к перечисленным32 configured legacy графам с100ms
warm fixture и корректно сброшенной динамикой.
Она не доказывает arbitrary-precision матричных параметров, весь storage/growth
контур, mid-probe checkpoint, classification или полные этапы4/5/11.
Отдельный отказ ModelArchive с точной TrainingPattern уже воспроизведён;
исправление общего Rdk matrix writer проходит собственную проверку.
