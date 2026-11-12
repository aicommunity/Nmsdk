# Независимое восстановление M40 accepted25 на Elder

Из отдельного Git-пакета b6a994d1603de4c8a2ec9a2fdfe431a21a916879 на Elder-1 восстановлены все1371 members архива SHA7b5c56397436cf9e251a2d1ee0174c074991ba74ca261e6b1e8e757ce7526783. Production portable_primary.restore_native_bundle Root929dbc176a0804910544539aaf79bdc4a02aa82a проверил размеры/SHA каждого файла и полный состав. Оригинальные M40 каталоги не использовались; входной archive/bundle hashes до и после совпали.

2.70699s, memory limit512MiB/CPU180s, free floor2GiB, read/write filesystem lease released. Операция синхронная, без native/model subprocesses; Kernel/native execution attestation не заявляется. [Исходные result](result.json) и [lease](reservation-final.json) импортированы через Git raw bytes. Compatibility adapter не исключил ни одного файла: retained1371.

Этот PASS подтверждает доступность и lossless восстановление опубликованных primary при независимом размещении. Он не пересчитывает JUnit verdicts, source/controller joins, model fingerprints или численные наблюдения и не закрывает semantic DATA replay. Сходимость/классификация этим результатом не заявляются.
