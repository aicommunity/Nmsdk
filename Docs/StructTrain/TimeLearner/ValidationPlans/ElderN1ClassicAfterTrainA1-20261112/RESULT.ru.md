# A1 остановлен до native-модели: недостаточный резерв места

Controller вернул `owned_job_capacity_preflight` до создания owned-unit binding и до native Train. Это не модельный прогон и не отрицательный результат обучения. Исходные launch log и ранние request/context сохранены в `preflight-failure`.

После предыдущего before timeout свободно было около2.01GB, чего не хватило для суммы minimum-free1GiB и output-reserve1GiB. Удалён только неиспользуемый `.o` кэш завершённых двух SDK builds, освобождено292795440 bytes; оба executable/CMakeCache и все данные сохранены. Новый [A2](../ElderN1ClassicAfterTrainA2-20261112/PLAN.ru.md) имеет отдельные job/control/output names. Математические условия, native SDK, controller, search/finalization budgets и resource limits не меняются.
