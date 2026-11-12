# Перенос полных N4 моделей: временные отклики до и после загрузки

Обе модели сохраняют форму отклика после экспорта и повторного импорта в новый native fixture. Это подтверждено actual C++ roundtrip2/2 и [независимым readback5/5](ValidationPlans/M40RecordedN4RoundtripIndependent5A3-20261112/RESULT.ru.md). Рисунки ниже показывают диагностическую пачку при active input0. Это не отчёт о классификации всей матрицы: Classic остановлен с `invalid_observation`, Branch — с `budget_exhausted`, сертификатов обучения нет.

Синяя линия — до экспорта, малиновая пунктирная — после создания нового экземпляра и импорта. Оранжевая линия показывает фактически записанный вход, нижняя панель — разность потенциалов. Показаны все3601 отсчётов за1.8 s при2000 Hz; сглаживания и прореживания нет. Четыре импульса соответствуют onset0.01/0.09/0.25/0.49 s. Полное окно сохраняется; отдельный увеличенный вид позволяет рассмотреть вершины. Единицы потенциала оставлены native, без неподтверждённого преобразования в SI.

На Soma1 обеих моделей видно несколько вершин; совпадение кривых before/after подтверждает перенос динамического отклика. Оно не устанавливает принадлежность каждой вершины конкретному входному импульсу. При обучении остаётся максимум закреплённого импульса, настоящее слияние считается неоднозначным; при оценке полного паттерна используется отдельный протокол. Глобальный максимум этих рисунков не подставляется вместо train assignment.

Classic, Soma1, всё окно:

![Classic Soma1: полное окно](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/classic/soma-1-full.png)

Classic, Soma1, увеличенный отклик:

![Classic Soma1: увеличенный отклик](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/classic/soma-1-response.png)

Остальные записанные Soma channels Classic показаны отдельно; их короткие отклики не скрыты общим масштабом Soma1.

![Classic Soma2](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/classic/soma-2-response.png)

![Classic Soma3](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/classic/soma-3-response.png)

![Classic Soma4](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/classic/soma-4-response.png)

Branch, Soma1, всё окно:

![Branch Soma1: полное окно](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/branch/soma-1-full.png)

Branch, увеличенный отклик:

![Branch Soma1: увеличенный отклик](../../../Reports/StructTrain/TimeLearner/RecordedN4RoundtripGallery-M40-20261112/branch/soma-1-response.png)

В Git сохранены7 выбранных рисунков, original manifest и provenance, около1.14 MB. Полная10-рисуночная галерея — воспроизводимый кэш M40: `/media/user/Data/TimeLearnerRefactor/readbacks/s08-recorded-n4-independent5-m40-a3/worker/tmp/recorded-n4-roundtrip-gallery`. Первичные responses/модели сохранены в compact primary; [исправление ошибочной controller-привязки](RecordedN4CorpusProvenanceCorrection-20261112.ru.md) является обязательной частью provenance. Все7 PNG просмотрены после получения из Git; размеры1920×1200, заголовки/оси/легенды не обрезаны. Отчёты с реакциями на все8 паттернов, independent evaluation и сравнение производительности требуют отдельных запусков.
