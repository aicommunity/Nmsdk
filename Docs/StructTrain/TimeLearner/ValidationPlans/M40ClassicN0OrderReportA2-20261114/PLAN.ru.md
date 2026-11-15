# Читаемый отчёт фактического контроля порядка

Выполнять только после whole-group closure и принятого результата order A2. Read-only отчёт читает production run manifest,64 полных diagnostic observations и фактические metrics; нового Train/Test, порога или verdict не создаёт.

Показать первые8 паттернов и target во всех8 позициях:15 уникальных trials×4 сомы+LT decision. Для каждого канала полный диапазон с отрицательным reset и отдельно положительный с явным clipping. Общие шкалы вычисляются по всем64 observations. Фактические входные импульсы и LT events обязательны. Отдельные сомы не получают чужой LT threshold.

Полные временные overview без прореживания; дополнительные native sample детали вокруг максимума полного Test-отклика, если требуется local Y. Эти maxima только для отображения и не являются assigned-impulse измерением Train. Не считать отсутствие нужного local Y основанием создавать фиктивную peak-метрику. Тысячи равномерных tiles повторно не производятся; выбранная gallery не выдаётся за64×4 plots или их сплошную ручную приёмку.

Production render_soma используется без копирования реализации. PNG1920×960,не менее8px/native tick для увеличений. Fixture/source до и после неизменны; модель source не модифицируется. Сохранить manifest/metrics и выбранные оригинальные PNG вGit, полные SVG/PDF/PNG как воспроизводимый M40 cache. После unit1/1 отдельно просмотреть публикуемые originals и указать точную область просмотра.

## Повтор A2: проверенное plot environment

A1 ошибочно запущен через /usr/bin/python3 без matplotlib;832.163с source audit выполнены до отказа render. Научный64-trial опыт и его метрики этим не затронуты, новых моделей в A1 не запускалось.

A2 использует существующий /media/user/Data/TimeLearnerRefactor/plot-python-owned-copy-a1/bin/python, ранее принятый в positive-response A2 и N0 focus: Python3.12.3/matplotlib3.9.4/Pillow13.0.0. plotting_runtime проверяется перед большим source audit, его environment записывается в manifest. Системные пакеты не устанавливаются, ресурсные пределы/научные условия прежние. Отдельные immutable source/request/output; первоначальный отказ сохраняется.
