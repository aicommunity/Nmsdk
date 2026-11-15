# Metadata18 A1: неверный ожидаемый тип исключения в тесте

17 checks OK,1 ERROR: actual stock registry корректно отверг file lease с ReservationError(RuntimeError), а test ожидал ValueError. Production directory-tree admission и positive resource guards прошли; тестовый gate целиком failed, не PASS. Outer group closed/lease released, native не запускался. Raw7 files в failed-test-exception-type. Исправление d33af820e меняет только импорт/ожидание штатного типа исключения; алгоритм registry и controller не меняются. Повтор18B1 обязателен. Native2 A2 был лишь объявлен, не запускался.
