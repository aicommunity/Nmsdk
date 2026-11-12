# Plot preflight: 44 checks

Source `153949c67042b8dc99dbecc1a2f10d4996406b01`. Прежние 42 tests повторяются с двумя новыми проверками production report_matrix: missing backend должен завершиться до дорогого DATA audit и до создания output; ошибочное output overlap должно отказать до backend preflight. Малый suite не запускает модели и не рисует actual matrix. После него отдельный gallery A2 использует проверенный owned-copy Python.
