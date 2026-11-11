# Независимый replay фактического package7: 9/9

На Elder-1 завершён набор s07-closed-native-package7-audit9-elder-f2.
Все девять объявленных проверок прошли без failures, errors и skips.
Контроллер завершился с returncode0 за39.79s; unittest выполнялся22.20s.
Whole cgroup закрыта, собственный lease released; owner отсутствует.
Два предупреждения Git о выключенной lazy fetch сохранены в stderr и
оставляют operational diagnostics в needs_review, а не clean.

Источник анализатора —7aa4104440b13634630e2dc15b7d2d5a46075bb8.
Первичные данные исходного C++ source export восстановлены из компактного
Git bundle без изменения оригиналов. Проверены package7, summary8, непустой
recovery ledger и48 primary files12 measurement groups. Два recovery delivery
сопоставлены с исходными runtime3 и фактическими наблюдениями.
Отрицательные проверки требуют конкретных причин отказа, поэтому TypeError
из предыдущей ошибки fixture больше не может подменить проверяемый отказ.

Согласованное удаление всех ledger events меняет identity пакета и не позволяет
заявлять полноту истории. DATA reader не удостоверяет полноту service ledger,
не восстанавливает live controller authority и не выдаёт scientific verdict.
Первоначальный C++ roundtrip source3edb22a4 был неуспешным и остаётся таким.
Эта приёмка не доказывает native import, отклик импортированной модели или
классификацию. Их проверяет следующий отдельный native18 набор.

Точные исходные bytes результатов и журналов находятся в completed;
readback-integrity.json содержит размеры и SHA256 каждого сохранённого файла.
