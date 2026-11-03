# Подготовка управляемых областей C-trim

Статус: код подготовлен, normal/ASan проверки ещё не выполнены. C-search On
не включён. Полные этапы4/5/7 и план0–12 остаются открытыми.

Pulse Core/TimeLearner/CapacitanceRegion выбирает Classic [1,L_i] или
Branch (L_(i+1),L_i], исключает последний anchor, сохраняет active/dormant
поправки и задаёт абсолютный multiplier каждого собственного C0. Бюджет
области проверяется до разворачивания диапазона. Разрешение новых образов,
графа и численной допустимости остаётся штатному native editor/preview.
Подробный контракт: Pulse Docs/Analysis/TimeLearnerCapacitanceRegions.ru.md.

Адресная native-gate спецификация native-capacitance-region-v1.json содержит
7 production-kernel проверок и8 реальных компонентных Classic/Branch N0/N1
на2000/20000Гц. Полная будущая regression specification содержит224 случая;
число в файле является декларацией, а не числом успешно выполненных тестов.

Для каждого реального fixture до создания экземпляров storage recipe задаёт
разные Exc/Inh C0. После изменения проверяются все дочерние C, в том числе
неизменённые Soma/LT/другие области, полные L/Ns/Rs и состояние C0 registry.
Каждый вход измеряется до и после через штатную native burst пробу: JSON и
недецимированный CSV time/stimulus/soma*. Это4 полных окна на fixture,
32 на весь набор. Для визуальных отчётов данные сохраняют исходный timestep;
публикация картинок и их проверка в читаемом масштабе остаются отдельной
обязательной приёмкой, наличие CSV её не заменяет.

Команда analyze FILE --format capacitance-region проверяет обе подписанные
модели, физику C/C0, геометрию области, неизменность storage/baseline и
полную матрицу первичных проб с проверкой CSV. Основной reader работает
только с настоящими записями; восемь тестов reader используют mutations этих
же записей: schema, region, input banks, duplicate/missing probes, подмена
модели, embedded packet и небезопасные/повторные primary paths.
TIMELEARNER_CAPACITANCE_REGION_DIR указывает каталог actual native evidence.

Ни region helper, ни изменение формы импульса не являются доказательством
сходимости или успешной классификации. После C-edit Branch требуется
инвалидировать затронутые входы и заново измерить всю итоговую модель.
