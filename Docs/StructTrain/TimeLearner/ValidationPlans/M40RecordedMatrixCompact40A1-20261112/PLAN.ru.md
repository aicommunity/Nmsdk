# Compact primary: 40 guards

Source `b0ceed67f7729d1ee501a9a5b8644089db7a5354`. Предыдущие 36 regression/provenance checks повторяются после механического выделения общего saved-execution join. Добавлены четыре проверки отказа до распаковки: archive >128 MiB, expanded >768 MiB, несовпадение суммы member sizes, отдельная модель >256 MiB. Новые actual-data tests в эту metadata suite не включены.
