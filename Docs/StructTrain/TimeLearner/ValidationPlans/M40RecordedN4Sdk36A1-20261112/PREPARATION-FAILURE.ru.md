# Canonical A1 отказал до сборки

Полный namespace требовал4148 файлов, materialized4140:8 кириллических HardwareLib catalog names искажены в локальном transport JSON. Windows Python stdin=cp1251, Node передал UTF-8; received helper patterns содержали mojibake. [Исходный stderr](failed-canonical/worker/canonical-child.stderr), [terminal](failed-canonical/worker/terminal.json), [closed/released](failed-canonical/closure-and-reservation.json), [точные hashes](failed-canonical/readback-integrity.json).

После закрытия A1 восстановлены те же Git blobs через ASCII JSON/base64 UTF-8 Git stdin. [Сверены размеры/SHA всех4148 source файлов](source-projection-repair.json). Code/commits не редактировались, namespace не уменьшался. Поле source_bytes_changed=false означает отсутствие изменения Git blob contents; физическая materialization дополнилась8 файлами. Отдельная A2 повторяет проверку. CMake/native не запускались; исходный A1 остаётся failed.
