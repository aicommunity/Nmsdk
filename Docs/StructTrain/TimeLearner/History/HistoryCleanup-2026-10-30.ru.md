# Очистка производных отчётов из истории корневого Git

Пользователь разрешил замену истории origin и всех корневых копий на локальной
машине, Elder и M40, включая ранее защищённые пользовательские копии.
Сабмодули не переписываются. Из истории удалены только PNG/SVG/PDF под
Reports/StructTrain/TimeLearner, кроме primary-bundle/selected. Все исходники,
конфиги, CSV/JSON, compressed primary archives, модели и gitlinks сохранены.

В отдельной копии проверены все 175 изменившихся commit trees: каждый оставшийся
blob и mode совпадает с оригиналом. Все 3413 commits сохранены; topology parents,
author/committer и messages сохранены. Имена 303 branches и 12 tags сохранены.
Сжатый draft pack около 232 MiB вместо backup bundle 746377684 bytes.
Это не обещание немедленного изменения отображаемого GitHub disk usage.

До замены origin создан полный mirror и verified bundle на M40:
 /media/user/Data/TimeLearnerRefactor/history-cleanup-20261030-a1/origin-before.bundle
Старые пользовательские stash/worktree states имеют отдельные закрытые backups.
Private local commit objects не публикуются в origin. Таблица публичных original
SHA → rewritten SHA находится в RootRevisionMap-2026-10-30.json. Исторические SHA
в scientific archives намеренно не заменяются: это original provenance.

Для replay старого root commit сначала получить его новый адрес из актуального
develop:
 python3 -m Scripts.StructTrain.TimeLearner history resolve OLD_FULL_SHA --root REPOSITORY
Затем использовать resolved_revision для checkout. Исходный archive/model hash,
recorded runtime/binary identity и критерий опыта остаются историческими.
Оригинальные source blobs и primary data не пересчитывались и не менялись.

Полные graphics — M40 cache, восстанавливаемый из lossless primary bundle
версией renderer после разрешения её original SHA. Выбранные PNG остаются в Git.
Удаление derived files не является пересмотром августовских 4/8–6/8, изменением
физики или заявлением о завершении всего рефакторинга.

Статус: origin и все 14 корневых копий заменены; 253 worktrees и восемь stash сохранены.
Проверены fresh recursive checkout и 25/25 production tests без пропусков.
[Итоговый receipt](../../../../Reports/StructTrain/TimeLearner/s10-root-history-cleanup-a1/README.md).
