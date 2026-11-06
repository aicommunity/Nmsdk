# Pending: отчёты фактического changed-threshold rollback

Normal sourcec411 gate4/4 дал16 actual units и полный fresh replay восстановленных моделей. Прежний render test перечислял только measured-grid/silent-nonseparable/fresh-frozen и оставлял четвёртый rollback-frozen вне отчёта. Он корректно описывал исторический12-unit corpus, но не новый16-unit набор.

Новая версия требует точного совпадения объявленных result.phases и фактических native run directories. Для corpus с changed_threshold_rollback обязательно строится rollback-frozen, для исторического corpus сохраняются три фазы. Число ожидаемых frozen trial–soma pairs выводится из объявленных trials и исходного ModelSpec реального run source, без постоянного24. Состав calibration matrices проверяется по каждому фактически выполненному candidate/confirmation, наблюдения в report primary равны native primary.

Во всех видах проверяются полное окно, дополнительные zoom views не менее8px/timestep,1920×960, PNG/SVG/PDF и фактические входные импульсы, отсутствие downsampling и контрольные суммы. Ожидается32 matrices/192 trial–soma pairs нового корпуса; фактические counts/число файлов должны быть получены из rendering gate, а не считаться уже подтверждёнными.

AST проверен локально. Серверный plotting gate, выборочные visual QA и публикация компактной галереи ещё не выполнены. Полный кэш хранится на M40 Data; в Git — первичные compressed data, manifests/metrics и выбранные рисунки, без копирования полного кэша.
