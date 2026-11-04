# Завершённые проверки Elder и состояние дисков04.11

После восстановления VPN повторно опрошены исходные задания; повторные
запуски normal304/managed61/ASan K1 не выполнялись.

- Source8021301e894368aefd045f9d77274fcce9f60245, Pulsecc97149c90ce98ff24ca688452f4a40d54e0e63d:
  joint normal304/304 прошли;3932 архивных файла,11693180B,
  SHA256 e0b4dbc2ba7f34f1f0579b19309240842c7d31c0a1624656f61010d1fae2f94c.
  Дополнительные readers и joint ASan всё ещё pending.
- Source34394c3017d3641377d8ec886eca3a1cfc502b92: managed-unit61/61,
  errors/failures/skips0;291 архивный файл,40136B,
  SHA256 5e8215c8e384488f12163bc8c0a544d9ab0a8c8f6aed915101ddaeb4d4c41225.
  Это kernel/resource controls; neural model tests не выполнялись.
- Parent units закрыты; global leases released. Архивы дважды проверены
  побайтово по member hashes: на worker и локально после передачи Git pack.

[Git evidence](../../../Reports/StructTrain/TimeLearner/s10-elder-completed-gates-20261104/summary.json)
commit25bbda5529caea24e8847973cd603d50b1b45826 имеет принятый parent1b1b571e2b979e2775e52a9a868cc0897d54b700;
непринятые алгоритмы/backend через него не объединены.

На момент проверки df -h: Elder system18GiB free/97% used;
M40 system84GiB free/62% used, Data387GiB free/89% used.
Inodes соответственно20%,19%,4% used. Нехватка диска на Elder является
существенным ограничением; это не доказательство текущего SSH failure.
При отключённом VPN ранее был отдельно подтверждён TCP timeout.

Elder /home/user/timelearner-refactor184GiB, включая readbacks44GiB;
/home/user/Nmsdk/Bin23GiB, Configs19GiB. Каталоги целиком не удалены:
они содержат исходники, модели и первичные результаты. В старых build roots
найдено около409MiB промежуточных object files; удаление в этом срезе не
выполнялось. Новые большие model jobs на Elder не запускались.
Длительный M40 ASan K1 оставался жив; ClassicN1At20000 прошёл,
BranchN0At20000 выполнялся. Полного ASan PASS пока нет.

Этапы1–12 остаются частичными. Ни native304, ни kernel61 не являются
научным PASS классификации или полной приёмкой исходного плана.
