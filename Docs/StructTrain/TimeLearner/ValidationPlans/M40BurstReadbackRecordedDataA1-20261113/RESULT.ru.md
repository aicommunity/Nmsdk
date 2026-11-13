# Реальные schema6 файлы: пять проверок пройдены

Задание s07-burst-readback-recorded-data-m40-a1 на M40:5/5 passed за1.085s собственно unittest, без failures/errors/skipped; terminal operation_passed=true. Whole group closed, lease released. Python consumer Rootda64c4c7e3988289d6fc2fc314645ed3634ff8f1, внешний Tool7bd3684732e1d3f7a0aa038d659fd52bc95892bf. Замороженные условия — controls, исходные записи — completed-readback.

Использованы только реальные файлы двух завершённых Classic Console процессов попытки A3: replay и matched. Fixture fingerprints охватывают70 JSON и99 CSV, включая native diagnostics. Проверены полный production audit обоих outputs, все три baseline/main observation, отказы для пропусков/дублей/NaN/count/censoring/повреждённых events, неизменная строгость graph/restoration wrapper и общий trace reader. Legacy audit_probe по-прежнему отвергает schema6; отдельный waveform reader не утверждает graph restoration либо peak assignment.

Новые native расчёты здесь не выполнялись, Branch этим набором не проверен. Научного verdict нет. Producer Git59cb6ea765b2444db404780159961f10b692ef8b сохраняет исходные записи вместе с отказом A3; перенос без повторной сериализации.
