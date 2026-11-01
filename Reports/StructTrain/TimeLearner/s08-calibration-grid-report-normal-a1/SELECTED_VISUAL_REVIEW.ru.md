# Выборочная ручная проверка текущих графиков

Renderer 01faa730d4decf7c82ae0ea48c42fa622f41817f, исходные данные
2dc5825fbb76e5a95408507d10b644b0571d3302; подборка обновлена в
387d400eac055d8d8916dc493b523d47386724f6. Ниже проверены четыре
текущих PNG при исходном размере 1920×960, а не вся коллекция.

Видны оба фактических входных импульса, полный поздний максимум Soma1
Classic/Branch и отдельный отклик Soma2 Classic. На увеличении Branch
поздний пик и фактическое LT spike event различимы; линия LT-события
подписана отдельно от потенциала сомы и входного сигнала. Тексты, оси
и трёхстрочная легенда читаемы и не перекрывают область данных.

Начальная last-input-only подборка могла завершаться до позднего пика.
Её дополнили общими видами/peak деталями, затем текущие target панели
заменили полными реакциями. Исходные волны не менялись и обучение не
повторялось ради оформления. Исторические варианты доступны по Git SHA
3c785fec6bd321559608cbb93eac009cfefd6907 и
6a8fa9fb884879298d8ad4e7fbdaa43af5a19e57.

Полный M40 cache включает все завершённые target/foil предъявления и
сомы; проверять только выбранную панель вместо полных окон нельзя.
SI единицы не подтверждены; маркер LT не является пересечением порога
Soma.SumPotential. Калибровочные картинки не доказывают сходимость
исходного обучения, независимый Test или августовское воспроизведение.
`visual_acceptance_complete=false` сохранён.

Проверенные файлы и SHA256:

- `primary-bundle/selected/Branch-fresh-confirmation-target-full-response.png` — `a94a2879091c2480110367bfe97aa9d293e94917fc17cb9c82bedcdd3cbe4e5c`
- `primary-bundle/selected/Branch-fresh-confirmation-target-peak-detail.png` — `098377b4123075b39a2a582d8df54aa88ba280d40946b0933101f0a28c376304`
- `primary-bundle/selected/Classic-fresh-confirmation-target-full-response.png` — `27c76f7797793b42705c81356fe1526e43d82efebff5ca3b3dc5f1ea8f4d9b67`
- `primary-bundle/selected/Classic-fresh-confirmation-soma2-target-full-response.png` — `90dea1f92a40c425c69cf927763da902fd74dc8f0b9f371c49c181f2ce4db9ad`
