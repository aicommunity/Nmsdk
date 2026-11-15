# Independent27 A1:26 PASS,1 reader ERROR

Все три корпуса восстановлены. Все16 прежних native32 regressions прошли; из11 новых SDK36 checks10 прошли, включая exact36 IDs/artifact rules,4 validated exports/summary8/mirrors/response,60 trial readback в сумме трёх corpora и corrupted primary negative. Одна проверка archived closure прочитала reservation-final.json (array) через load(), требующий object. Strict reader корректно выдал not_an_object; весь gate failed, не27/27. Unittest636.234s/outer658.347s, group closed/released. Raw7 proof files в failed-array-reader.

Исправлениеc3a4ea891 меняет только использование штатного strict load_json для array плюс явную проверку list/ровно1 lease/released. Duplicate keys/NaN protections сохраняются; исходные модели/архивы/JUnit не меняются. Следующий A2 повторяет все27 checks на новом source, разделив3 независимых corpora на8+8+11 параллельные jobs. Aggregate PASS возможен только после PASS/closure/source-fixtures byte-equal всех трёх.
