# Default SyncTol fixture: honest terminal budget

Static review: при двух и более входах BoundedTraining всегда выполняет adjustable-input sweep, даже при fixed bounds. Outside-tolerance final после maximumSweeps1 завершает попытку BudgetExhausted; сервис правильно не выдаёт promotable Certificate. Предыдущий fixture ошибочно ожидал его наличия.

Исправлены только две assertions-группы: ожидаются BudgetExhausted и пустой service.Certificate; retained Search()->Certificate исследуется лишь как отрицательная final-математика с исходным SyncTol.02, Exact=false и residual>.02. Исторические criterion/physics/controller/defaults не меняются. IDs179 сохраняются, Pulse661 неизменен, локальных C++/numerical запусков нет; runtime pending.
