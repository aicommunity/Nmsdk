# Крупный вид реально измеренных N0 вершин

Статус: подготовлено, серверная проверка/визуальная приёмка ещё не выполнялись. Новой Train/Probe/Test серии не требуется: используются существующие completed/valid A/B primary.

[Исходное сравнение](../../N0GeometryPhysicalScientificReport-20261114.ru.md) оставляет оба исхода budget_exhausted/0 jointly-ready. Before group62 имеет assigned maximum first_sample=last_sample=978, raw0.01608944232254117; after group74 — frame996, raw0.01582675976754666. Эти числа прочитаны из опубликованных selection manifests, не предсказаны по L.

Оба view показывают native frames920..1040 включительно:121 неизменённый отсчёт,0.46..0.52с относительно начала собственной пробы, channel0 единственной Branch сомы. Оба измеренных пика находятся внутри view. Используется существующий production recorded_training_focus.render с полной проверкой package7/summary8 и исходного external CSV, без нового parser, интерполяции, peak selection или tolerance. Default физики/storage/lifecycle не меняется.

Проверить min8px на native tick, PNG2800×800, полноту каждого full-before, исходные frame IDs/selection validity и source hashes. Y local для каждого собственного view; между отдельными моделями сравнивать числовые оси, не одинаковую высоту картинки. Full/omission controls остаются в исходном отчёте: один focused full-before не заменяет причинную проверку принадлежности.

Unit test_n0_geometry_peak_focus проверяет действительный group binding к лучшему measured timing-ready candidate и неизменность отрицательного training outcome. Никакой Exact/classification/infeasibility не выводится из масштаба. После server1/1 отдельно просмотреть оба оригинальных PNG; Git — выбранные PNG, manifests и receipts, full vectors — cache. Empty-window boundary views предыдущего report остаются clock controls и не считаются этими peak views.
