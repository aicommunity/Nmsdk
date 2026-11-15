# Diagnostic loader fix: 32/32

M40 job `s10-recorded-diagnostic32-m40-a2`, source `251dddc6293bfb4bf620b46d25adf2c633cae8fc`, Tool40e28802. Все32 точных IDs прошли без failures/errors/skips; execution completed, whole group closed, lease released, diagnostics clear. Tool/source/fixtures before/after побайтно равны;13 original raw proofs в `completed/`.

Прежние28 guards выполнены повторно вместе с4 новыми `RuntimeLoaderEnvironmentTest`. Проверены замена inherited loader values значениями manifest, временное отсутствие undeclared key, восстановление values/absence после исключения, отказ arbitrary PATH/invalid type/NUL до изменения окружения. Equality guard внутри executor не менялся и не отключался.

Это acceptance адресной Python логики, не новый запуск моделей. Исправленный actual Console N4 diagnostic16 A2 получает отдельную декларацию/controller/output; он должен самостоятельно подтвердить полный16-trial scope, effective runtime, frozen models и closure. Отказ A1 остаётся0/16, а исходные negative Train outcomes не переоцениваются.
