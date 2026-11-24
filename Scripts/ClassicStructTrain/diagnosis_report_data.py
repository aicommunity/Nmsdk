"""Derive report statements and editable chart series from audited observations."""
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import ROOT, WORK, PREVIOUS, load, save, relative
from diagnosis_analysis import rows_of, first_iteration


def chart(identifier, title, x, y, headers, rows, analysis, **options):
    values = [value for row in rows for value in row[1:] if isinstance(value, (int, float))]
    return dict(id=identifier, title=title, x=x, y=y, headers=headers, rows=rows, analysis=analysis,
                min=options.get("minimum", min(0, min(values))), max=options.get("maximum", max(values)+1),
                **{k: options[k] for k in ("type", "format") if k in options})


def section(title, paragraphs, charts=()):
    return dict(title=title, paragraphs=paragraphs, charts=list(charts))


def run():
    data = load(WORK / "diagnosis-analysis.json")
    sources = load(WORK / "source-audit.json")
    counts = Counter(p["status"] for p in data["processes"])
    sections = []
    pairs = data["inference_comparisons"]
    trained = data["training"]
    observer = data["observer_pairs"]
    references_path = WORK / "reference-reproduction.json"
    reference = load(references_path) if references_path.exists() else []
    by_model = defaultdict(list)
    for row in load(WORK / "archival-answers.json"):
        by_model[row["experiment"]].append(row)
    history_rows = [[model, sum(r["historical"] != r["previous"] for r in rows),
                     sum(r["historical"] != r["trained"] for r in rows)] for model, rows in by_model.items()]
    history_chart = chart("R01", "Различия с историческими ответами", "Архивный столбец модели",
                          "Различия из 150 ответов, шт.", ["Модель", "Проверка архивного графа", "Новое обучение"],
                          history_rows, "Модели с одинаковым номером и разным вариантом структуры имеют разные архивные столбцы. Суммы 111 и 98 характеризуют этот набор сравнений. Индивидуальные расхождения доступны в книге.",
                          type="bar", maximum=12)
    sections.append(section("1 Источники и исходные расхождения", [
        "NT обозначает NNeuronTrainer, NL — NNeuronLearner. Число после букв — номер обучающего объекта Iris. Число в скобках обозначает архивный вариант графа. Средний вход задаётся покомпонентным средним пяти задержек объектов № 51 и № 61.",
        f"Сверены {sources['recognition_cells_verified']} исходных ячеек и {len(sources['protocols'])} состояний из пяти схем. В 14 состояниях перехода № 51 → № 61 совпали четыре счёта классификации. Пятнадцатый файл содержит восемь ответов. У 26 файлов 31-я строка ответа содержит 0 и находится за пределом опубликованного диапазона из 30 входов. Два первых файла одиночных итераций совпадают побайтно.",
        "Для распознавания использованы исходные столбцы книги «Распознавание.xlsx». Для схем использованы книга «Обучение нескольким примерам.xlsx» и первичные output_data. Структурный реестр опирается на «Инофрмация о длинах дендритов и числе синапсов.xlsx». Точные диапазоны и контрольные суммы находятся в сопровождающей книге и реестре.",
    ], [history_chart]))

    parser_runs = [p for p in data["processes"] if p["phase"] == "parser" and p["status"] == "completed"]
    sections.append(section("2 Контроль измерительного стенда", [
        f"Контроль EOF использует 30 входов подвыборки в исходном порядке. Завершены {len(parser_runs)} проверки. Протоколы с переводом строки и без него требуют ровно 30 успешных чтений. Обрыв последнего вектора принимается как 29 полных записей и ошибка извлечения трёх значений.",
        "Фрагмент исторического TreatDataFromFile проверял eof до извлечения и задавал длительность как период стимула за вычетом одного такта. Вызов фрагмента в полном расчётном цикле отсутствует. Проверки 1333 и 1334 тактов и включения первого отсчёта характеризуют чувствительность к границе измерения. Источник лишнего нуля в конкретном историческом файле остаётся гипотезой.",
        "В стенде записывается порядок списков модели, оболочки и нейрона. Причины нативного завершения, запланированного числа итераций, лимитов модельного и машинного времени записываются отдельными полями. Исходный стенд мог обозначать ручное упорядочивание как штатное и присваивать один статус двум разным ограничениям.",
        (f"Сохранённые сборки подтвердили прежние векторы для {sum(r['matches'] for r in reference)} из {len(reference)} проверенных конфигураций. "
         f"Точный SHA256 исходного бинарника найден для {sum(r['binary']['exact_original_binary'] for r in reference)} измерений."
         if reference else "Точный SHA256 бинарника первого отчёта отсутствует среди доступных копий. Сопоставление с журналами ведётся по закреплённым конфигурациям и сохранённой контрольной сборке."),
    ]))

    by_factor = defaultdict(list)
    for row in pairs:
        by_factor[row["label"], row["factor"]].append(row)
    certified = {key: sorted(group, key=lambda r: r["repeat"]) for key, group in by_factor.items()
                 if len(group) == 3 and all(r["reversal"] for r in group)
                 and len({tuple(c["id"] for c in r["changed"]) for r in group}) == 1}
    inference_charts = []
    paragraphs = [
        f"Выполнено {len(pairs)} парных сравнений. Для {len(certified)} сочетаний модели и фактора получены три согласованных повтора с возвратом исходного вектора. Включены также нулевые эффекты. Для каждого ответа книга хранит направление изменения и запас до порога в микровольтах.",
        "Порядок компонентов, сброс, изменение фактической последовательности из-за длительности окна, округление и выбор сигнала оцениваются на одном графе. Изменение раннего сигнала и смена бинарного решения привязываются к своим тактам. При совпадении структуры особое значение сохраняют история входов и фазовое состояние генераторов.",
    ]
    controls = (("NL22", "order"), ("new-NT111", "reset"))
    for index, key in enumerate(controls, 2):
        group = certified.get(key, by_factor.get(key, []))
        if not group or not group[0]["changed"]:
            continue
        row = group[0]
        changes = row["changed"]
        ids = ", ".join(str(c["id"]) for c in changes)
        status = "подтверждено экспериментом" if key in certified else "поддерживается ограниченными данными"
        paragraphs.append(f"{key[0]}, фактор {key[1]}, {status}. Изменились объекты {ids}. Числа исторических различий до и после приведены в книге для случаев с полным историческим вектором.")
        if index == 2:
            rows = [[phase, *[c[field] for c in changes]] for phase, field in
                    (("Ручной", "before"), ("Штатный", "after"), ("Ручной повторно", "before"))]
            inference_charts.append(chart("R02", "Обратный контроль порядка для NL22", "Порядок расчёта",
                "Бинарный ответ", ["Режим", *[f"№ {c['id']}" for c in changes]], rows,
                "Каждый ряд соответствует одному входу. Возврат ручного порядка проверен целым вектором ответов.", maximum=1))
        else:
            rows = [[f"№ {c['id']}", c["margin_before_uV"], c["margin_after_uV"]] for c in changes]
            inference_charts.append(chart("R03", "Влияние сброса на запас до порога", "Вход Iris", "Запас, мкВ",
                ["Объект", "Непрерывно", "Со сбросом"], rows,
                "Изменение знака запаса наблюдается на том же графе. Историческое применение сброса требует отдельного источника.",
                type="bar", format="0.0"))
    paragraphs.append(f"Потактовые журналы сопоставлены для {len(data['tick_comparisons'])} комбинаций. Измеряемая цепочка включает входную подачу, внутренний генератор, входы и выходы синапсов, сомы, LTZone и регистрируемое решение. В книге указана первая обнаруженная разность каждой величины в наблюдаемом окне.")
    sections.append(section("3 Причины расхождений инференса", paragraphs, inference_charts))

    training_charts = []
    nt80 = [row for row in trained if row["phase"] == "limits" and row["run"].startswith("NT80-")]
    strict = [row for row in trained if row["phase"] == "limits" and row["run"].startswith("NT22-strict-")]
    paragraphs = [
        f"Сравнены {len(observer)} пары обучения с трассировкой и без неё. У {sum(row['same_end'] and row['first_difference'] is None for row in observer)} пар совпали завершение, полная последовательность записанных контрольных событий и конечная структура.",
    ]
    if nt80:
        paragraphs.append(f"NT80 при последовательных запусках завершился в {sum(r['status']=='completed' for r in nt80)} из {len(nt80)} попыток. Число итераций по повторам {', '.join(str(r['iterations']) for r in nt80)}. Ранее одна попытка была ограничена по времени после 42 совпавших итераций. Полученные результаты связывают отличие прежней попытки с границей запуска.")
    if strict:
        first = ROOT / strict[0]["directory"]
        prefixes = [first_iteration(first, ROOT / row["directory"]) for row in strict[1:]]
        paragraphs.append(f"Строгий NT22 с пределами 1000 итераций и 1800 секунд завершил наблюдение на итерациях {', '.join(str(r['iterations']) for r in strict)}. "
                          f"Статусы по повторам {', '.join(r['status'] for r in strict)}. Совпадение начальных участков и рост структуры характеризуют обследованную траекторию. Для общего вывода о сходимости необходимы дополнительные сведения о полном состоянии алгоритма.")
        def sample(path):
            return {r["iteration"]: sum(r["synapses"]) for r in rows_of(path / "iterations.jsonl")
                    if r["iteration"] % 25 == 0 or r["iteration"] == 1}
        series = [sample(ROOT / r["directory"]) for r in strict]
        rows = [[str(i), *[s.get(i) for s in series]] for i in sorted(set().union(*(set(s) for s in series)))]
        training_charts.append(chart("R04", "Траектория строгого варианта NT22", "Учебная итерация", "Синапсы, шт.",
            ["Итерация", *[f"Повтор {i+1}" for i in range(len(series))]], rows,
            "Показаны реально измеренные точки через 25 итераций и первая итерация. Предел времени оставляет поздние точки пустыми."))
        save(WORK / "strict-common-prefix.json", prefixes)
    factors = [row for row in trained if row["phase"] == "training-factors"]
    own = sum(row["own_recognized"] is not None for row in factors)
    paragraphs.append(f"По изолированным факторам получено {len(factors)} записей обучения и {own} проверок своего входа после загрузки. Физические параметры взяты из сохранённых графов. Частично восстановленный учебный цикл сочетает архивный фрагмент и решения из Git. Результаты относятся к этой реализации на современном ядре.")
    selections = [(name, [r for r in factors if r["run"].startswith(name + "-trainer-22-r")])
                  for name in ("modern-default", "stop-tolerance", "stop-keep", "stop-strict", "stop-crossing", "stop-reversal")]
    stop = [[name.removeprefix("stop-"), *[next((r["iterations"] for r in rows if r["run"].endswith(f"-r{i}")),
             None) for i in (1, 2, 3)]] for name, rows in selections if rows]
    if stop:
        training_charts.append(chart("R05", "Условия остановки обучения NT22", "Вариант правила", "Итерации, шт.",
            ["Вариант", "Повтор 1", "Повтор 2", "Повтор 3"], stop,
            "Завершения и достижения лимита представлены в исходной таблице. Точно совпавшее число итераций не заменяет проверку флага завершения.",
            type="bar"))
    sections.append(section("4 Первая разность в обучении", paragraphs, training_charts))

    contexts = data["sequence_context"]
    context_charts = []
    paragraphs = [f"По двум схемам получено {len(contexts)} выровненных записей учебных этапов в живом режиме, режиме снимков и режиме пауз. Сопоставлены физическая структура, число итераций и время модели. Инференс снимка выполняется в отдельном процессе на замороженном графе."]
    for scheme, identifier in (("0_1", "R06"), ("0_1_4_full", "R07")):
        relevant = [r for r in contexts if r["scheme"] == scheme and r["repeat"] == 1]
        differing = [r for r in relevant if (r["d"][0], r["s"][0]) != (r["d"][1], r["s"][1])]
        if relevant:
            paragraphs.append(f"Схема {scheme}, первый повтор. При сравнении живого теста с обучением без теста различий графа на учебных этапах {len(differing)} из {len(relevant)}."
                              + (f" Первое наблюдаемое различие на этапе {differing[0]['stage']}." if differing else ""))
        source_sheet = "Схема 0 на 1" if scheme == "0_1" else "Схема 0 на 1+4 для 150 примеров"
        historical_q = {r["state"]: r["metrics"]["FP"] + r["metrics"]["FN"] for r in sources["protocols"]
                        if r["sheet"] == source_sheet}
        stride = 1 if scheme == "0_1" else 2
        rows = [[str(r["stage"]//stride+1), historical_q.get(r["stage"]//stride+1), r["live_Q"], r["snapshot_Q"]]
                for r in relevant if r["live_Q"] is not None and r["snapshot_Q"] is not None]
        if rows:
            title = "Одиночные итерации № 61" if scheme == "0_1" else "Переход от № 51 к № 61"
            tested = "30 входов" if scheme == "0_1" else "150 входов"
            context_charts.append(chart(identifier, title, "Номер контрольного состояния",
                f"Ошибки на {tested}, шт.", ["Состояние", "История", "Живой тест", "Отдельный снимок"], rows,
                "Историческая линия рассчитана из первичных пообъектных ответов. Сравнение включает возможное изменение последующего обучения и контекст измерения. Структурные траектории и результаты пауз приведены отдельно."))
    sections.append(section("5 Влияние оценки на последующее обучение", paragraphs, context_charts))

    sections.append(section("6 Границы выводов и материалы", [
        "Подтверждены только эффекты с измеренным вмешательством и проверкой возврата. Для исторических расхождений полный комплект первичных сигналов и исходных кодов 2022 года отсутствует. Архивные альтернативы графа, различия порядка и состояния при предъявлении дают несколько совместимых объяснений.",
        "Доказанный дефект регистрации стенда исправлен. Подтверждение ошибки исторической таблицы требует расхождения с первичным файлом при согласованной привязке. Совпадение опубликованных счётов с первичными файлами подтверждает их арифметику. Источник необъяснённой 31-й строки и конкретная причина оставшихся исторических расхождений не установлены.",
        f"По журналам учтено {len(data['processes'])} процессов. Завершено {counts['completed']}. Остальные случаи и достигнутые внутри процесса ограничения доступны в книге. Использована сборка Release и запуск из Bin/Platform/Win. Степень подтверждения отдельных факторов следует оценивать по конкретным экспериментам и числу доступных повторов.",
        "Источники предшествующей проверки — ScientificComparisons и TrainingReproducibility. Исходные материалы находятся в Docs/ClassicStructTrainExperiments/Эксперименты. Реестр, нативные журналы и контрольные суммы находятся в Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124.",
    ]))
    overview = [
        ["Архивные ответы", sources["recognition_cells_verified"], "Сверено с ячейками первичной книги"],
        ["Состояния в схемах", len(sources["protocols"]), "Сверены структура и пообъектные ответы"],
        ["Завершённые процессы", counts["completed"], "Технический статус процесса"],
        ["Парные проверки инференса", len(pairs), "Есть база, изменение и обратный контроль"],
        ["Аудит влияния трассировки", len(observer), "Пары фактических попыток обучения"],
        ["Сопоставление контекста", len(contexts), "Выровненные стадии среды обучения"],
    ]
    save(WORK / "diagnosis-report.json", {"lead": "Исследование сопоставляет первичные исторические записи, результаты прежнего инференса и новые контролируемые расчёты. Для каждого выявленного различия учитываются граф, стимул, внутреннее состояние и способ измерения.",
                                         "sections": sections, "overview": overview})


if __name__ == "__main__":
    run()
