# Elder: повтор 36 checks

Все 36 объявленных regression/provenance checks повторяются на Elder-1. Source и controller закреплены на `557decacf65bb5f13af43cb5195093e890360411`; opt-in actual-data tests этого файла в suite не включены. Это проверки Python логики, без C++ сборки и расчёта моделей.

Перед подготовкой подтверждены 2.8 GiB доступного диска, около 27 GiB available RAM и отсутствие процессов NeuroModeler. Перед запуском guard требует не менее 2 GiB free; output ограничен 512 MiB. Новый source checkout и декларация занимают десятки MiB, исходные пользовательские копии не меняются. Полные N4 данные и графики остаются на диске M40.
