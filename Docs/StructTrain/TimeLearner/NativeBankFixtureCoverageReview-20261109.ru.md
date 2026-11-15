# Покрытие test-only исправления bank descriptor — 09.11.2026

Root просмотрел code029c720 и docs95e813, потомков f015. Изменяется один test TU: наблюдаемый public graph descriptor вместо protected getter и разнесение двух EXPECT_THROW. Production Pulsef7 и API/физика не меняются; адресные assertions сохраняются. Исходники подготовлены и опубликованы, но не скомпилированы и не проверены на сервере.

Проверка исходного raw canonical A3 (SHA79d72831) выявила пробел: **ни один из11 затронутых tests не входит в прежние37**. Поэтому следующая проверка обязана сохранить все37 и добавить11 непосредственно затронутых случаев: всего48 уникальных IDs. [Полные списки и metadata-сверка](NativeBankFixtureCoverageReview-20261109.json). Это требование будущей приёмки, не готовый launch manifest.

Дополнительные cases проверяют actual bank readback/routing Classic и Branch сN4/N6, shared bank, неправильный selector descriptor и запрет неквалифицированного final token. Compile-only успех не считается проверкой нового observed descriptor. Descriptor ограничен Ns1/no-inhibition; он не подтверждает private executor list/live authority.

Нужны новый runtime/output A4 и проверенный переход закрытого cache A3. Старый compatibility supervisorc626 жёстко привязан к исходным A3 paths/hashes и не может исполнять новые controls без изменения frozen кода. Вместо очередной TEMP-копии следующая группа использует maintained owned_native_job после его отдельной40-case приёмки. Старые A3 paths/rawcontrols не переписываются. Все эти действия пока pending; научный допуск нового контроллера отсутствует.
