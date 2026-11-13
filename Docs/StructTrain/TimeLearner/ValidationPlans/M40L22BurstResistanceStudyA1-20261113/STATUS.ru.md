# Ограниченный эксперимент L22 запущен

s07-l22-burst-resistance-study-m40-a1 на M40 выполняет [заранее объявленный протокол](../../NativeBurstResistanceStudy.ru.md). Source revision3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c, L=[22,1,1,1], исходный Rs86МОм, N1, frequency2000Hz, threshold100; training=budget_exhausted, certificate=null. Это actual stopped import, не реконструкция из начального template.

Control Git a8b156dda8d8acb6c836beade5a13fec5e01edc5. Python actor Rootda64c4c7e3988289d6fc2fc314645ed3634ff8f1, Console Root49689590c / PulseLibdfb9a9824, runtime381d28bdf1e32674f9ad6698a095be29c89620cbdbf949952e624c72762cd019. Полные request/suite/declaration/runtime находятся в controls. Предварительные6 Console процессов Classic/Branch приняты отдельной A4, затем все их группы закрыты и ресурсы освобождены.

Подтверждённый handle: unit timelearner-65b3c6ee-02d5-4db5-b44d-58218f8c1b11.service, invocation c3967a724ad44138a383b954e3670029, PID3502751/start362909742, boot0340843f-8a05-4b7e-bd66-afeefecdbe55. Каталог /media/user/Data/TimeLearnerRefactor/readbacks/s07-l22-burst-resistance-study-m40-a1. Перед любым повторным запуском требуется установить исход этой попытки и закрытие всей группы.

Пять Console runs: replay86, matched86 и Rs64.5/43/21.5МОм input0. Native domain checks обязательны. Geometry, storage, target, порог и остальные входы сохраняются. Outer Python memory8GiB, native leaf8GiB, whole wall14400s, каждый native probe900s, output budget8GiB/free floor8GiB. Проверка большого исходного архива предшествует пробам; launch/kernel STARTED не означает завершённое наблюдение.

Последующий live readback того же kernel handle подтвердил running. Replay и matched-control при86МОм завершены и прошли production run/manifest audit: полные наблюдения по3601 samples, model revision совпала с исходной3b8a160f.... Resistance-1 (64.5МОм) также прошёл production run/manifest audit:3601 samples, model revision07c0c66a3e42547ce0efa1ef1418a81aa4e3c9d05fbda965768a4b9b73facb0f. Глобальный диагностический максимум Soma1 увеличился с0.005683014493454208 до0.0076080042832809; максимумы остальных трёх каналов остались0.015828572406203167. Эти числа не являются измерениями закреплённого импульса. Свежая kernel-проверка подтвердила тот же живой handle; выполняется resistance-2. Полный межусловный audit и графики ещё ожидаются. Исходный replay job234,679,308 bytes укладывается в штатный256MiB native input limit; увеличивать его не потребовалось.

На текущем снимке итогового результата и графиков серии ещё нет. Training, assigned-peak measurement и classification verdict не заявляются. После завершения требуются проверка actual conditions/полноты, визуальная проверка графиков всех сом и компактная Git-публикация. Большие полные gallery остаются кэшем M40.

## Промежуточная точка43МОм и форма отклика

Resistance-2 прошёл per-run production audit и сохранил complete3601 samples: revision2c6f281823fbf634ac30d5ba46a5117ec261421c71cf0351e9fb034ff99fec2e; global Soma1 maximum0.011492021514233342. Остальные три maxima прежние0.015828572406203167. Resistance-3 ещё ожидается; тот же kernel handle подтверждён живым. Итоговый межусловный audit серии ещё не завершён.

Дополнительный геометрический readback выполнен на M40 штатным matched_omission_evidence._maxima из неизменённого actorRootda64c4c7e; он не определяет принадлежность пика импульсу. Времена ниже относительно фактического trial begin1.8005s. Минимальная амплитуда и baseline взяты из observation specification. Все перечисленные вершины interior, без clipping.

|Rs, МОм|Времена трёх геометрических вершин, s|CSV SHA256|
|---:|---|---|
|86|0.2790;0.4615;0.7035|bdee6afb21c05ce9bf9978d1f957fa7f418ba1377e1de4e3459f644c7f1575e9|
|64.5|0.2790;0.4615;0.7035|e891fdb2464cb685c63506844bdf4035e829d90dcb5788fd71f5c6b97b4e684e|
|43|0.2785;0.4615;0.7030|a5254173b0af3a36073c4df6d8904a8e37e8400ac65118f929421de6290ab085|

Фактические четыре входных события:0.010,0.090,0.250,0.490s. Усиление отклика уменьшением Rs пока не добавило отдельную вершину; изменение времён не больше одного dt0.0005s. Из трёх максимумов на четыре импульса нельзя автоматически вывести однозначное соответствие; нельзя и приписать первую вершину pulse0 только по её высоте. После завершения сетки и визуальной проверки следующий содержательный вопрос — принадлежность вершины через штатные matched-omission witnesses на неизменной модели. Общий максимум не использовать как ошибку N1, новую CapturedPerInput цель не захватывать. Один L22 не доказывает PhysicalInfeasible; увеличение Train budget не назначается автоматически. Полный первичный пакет и графики будут опубликованы после закрытия серии; эта промежуточная таблица не является её итоговой приёмкой.
