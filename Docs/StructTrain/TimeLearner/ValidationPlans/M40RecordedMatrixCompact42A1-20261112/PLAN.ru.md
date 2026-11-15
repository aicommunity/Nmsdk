# Compact primary: 42 guards

Source `3f5086df45aa2f03e222d4379d39cb231a4bda88`. Предыдущие 36 checks повторяются после выделения общего saved-execution join. Добавлены шесть проверок: отказ archive >128 MiB, expanded >768 MiB, неверной суммы member sizes, модели >256 MiB; нормализация parent segments до проверки пересечения output/source; запрет распаковки внутрь input bundle. Ранняя декларация40 была уточнена до запуска; 40-case job не запускался. Actual-data test не включён в этот metadata gate.
