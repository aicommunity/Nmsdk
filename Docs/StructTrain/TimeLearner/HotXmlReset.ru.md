# Native XML прогретого learner: проверка границы Load/Init/Reset

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
