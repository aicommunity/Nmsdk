# Исправленный Console: подготовка принята, новая сборка выполняется

Root49689590cbdc0bbe5abccfb91374ad716f0ff977 / Pulsedfb9a98244f91b4f4029d8470465fd40116436ca. Отдельные source-idle-probe-readback-sdk-a1, build-idle-probe-readback-sdk-a1 и runtime-idle-probe-readback-sdk-a1. Прежний runtime Root1ae882633 не изменяется.

Первая canonical preparation A1 отказала до компиляции: build_profile разрешает parallel1/2, а запрос содержал4. Отказ и исходные условия сохранены в соседнем M40IdleProbeReadbackSdkA1-20261113. В A2 исправлен только профиль на parallel2; исходники и модель не менялись. Не ослаблялись ограничения runner.

A2 принята: [terminal](canonical-completed/worker/terminal.json), [закрытие и released lease](canonical-completed/closure-and-reservation.json). Проверены точные Git bytes4176 materialized files, source closure и две выбранные native N1 roundtrip проверки Classic/Branch. Canonical preparation сама не компилирует и не исполняет модель.

Сборка запущена штатным owned_native_job: controller /media/user/Data/TimeLearnerRefactor/readbacks/s07-idle-probe-readback-sdk-m40-a1-controller, supervisor3373915/start362663073, boot0340843f-8a05-4b7e-bd66-afeefecdbe55. Fresh Release/O3, parallel2, memory8GiB, build wall10800s/whole wall14400s. Последнее подтверждение — build.log с ходом компиляции; завершение пока не принято. Повторный запуск до установления terminal и полного закрытия запрещён.

После сборки и двух roundtrip необходимы отдельные шесть реальных Console probes. Только затем запускать N4 fixed-geometry Rs study. Ни успешная подготовка, ни сборка не дают сертификата обучения либо классификации. Научная цель остаётся диагностикой фактической модели3b8a160f2fe6f5ace6aa377f5d42117bcc922bcdd746358ca8d7c34fc67a6b1c с L=[22,1,1,1], без повторного Train и без подмены закреплённого пика максимумом пачки.
