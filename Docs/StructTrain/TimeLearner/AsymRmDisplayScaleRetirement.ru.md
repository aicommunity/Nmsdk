# AsymRm: исторические scale/UWatch patchers

Подготовлен отдельный подэтап9 от develop. Он удаляет ровно два самостоятельных
исторических инструмента Bin, без wrappers/копий на прежних местах:

- patch_pattern_scale.py: canonical4/32 ISI rewrite и автоматическое изменение
  SyncTolerance/peak/agreement margins с floor0.0005. Для новых заданий фактические
  паттерны и допуски задаются явно; прежнее поведение не переносится как default.
- patch_watch_pattern_legend.py: regex правки старого Interface.xml, четыре ISI
  series и обрезаемые0/1 markers на dendrite axis. Новый temporal report читает
  реальные native soma/input samples; эквивалентность старому UWatch не заявляется.

Все конфиги, интерфейсы, измерения и модели сохранены. PARAM_SPAN_COMPARE получил
историческую пометку и точные Git-ссылки вместо удалённых setup/scale entrypoints.
Полные исходники обоих файлов прочитаны, входящих literal imports/calls в
проверенных root/Bin production/config trees не найдено. Это адресный review,
не обещание полной миграции всех24 прежних AsymRm Python или runtime-эквивалентности.
Общие helpers с оставшимися потребителями в этот подэтап не включены.

[Source/retrieval review](AsymRmDisplayScaleRetirementReview.json) и
script_migration.json содержат исходный Bin commit3d5fc67c33f7be9ad3806db0b00b9d92588049bb,
полные пути, blob SHA1, SHA256, размеры, last-change commits и команды Git show.
Всего manifest теперь222 records:220 retired и2 moved; complete=false.
В SelectivityAsymRm/scripts остаются22 Python, весь этап9 не закрыт.

Оба сервера прошли production verify-migration222 и restored-path negative:
17 primary members и286 source hashes каждого запуска сверены.
[Проверка](AsymRmDisplayScaleRetirementVerification.json).
Bin no-ff merge37ff211fa6ba4999fc51802182915022b239a1eb опубликован; его tree
равен проверенному1a8e1d6b. Корневой children-first merge выполняется отдельно.
Исторические скрипты не запускались, Build/Calculate и физика не изменены.
Работающие server source/runtime не обновляются.
