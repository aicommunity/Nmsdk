# Точная декларация primary без пересериализации filesystem timestamps

A1: file limit128MiB меньше фактических файлов. A2: изменение через JS JSON потеряло точность link filesystem timestamps; production сравнение отвергло namespace. Исходные файлы не менялись, оба collector jobs закрыты. A3 берёт исходные сырые байты A1 и заменяет единственное текстовое значение maximum_file_bytes128MiB→256MiB; остальная декларация, включая наносекунды, побайтно сохранена. Проверки hash/полного namespace/closure не ослабляются. Архивирование ещё не принято.
