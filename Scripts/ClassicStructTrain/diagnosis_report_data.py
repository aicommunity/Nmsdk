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
    coverage_path = WORK / "diagnosis-coverage.json"
    coverage = load(coverage_path) if coverage_path.exists() else None
    sections = []
    pairs = data["inference_comparisons"]
    trained = data["training"]
    observer = data["observer_pairs"]
    reference = data.get("reference_audit", [])
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
        "Даты сохранения рабочих документов относятся к 2022 году. Дата создания шаблона XLSX в метаданных не датирует эксперимент. Версии основного репозитория за 18 марта и 15 апреля 2022 года указывают на доступные ревизии PulseLib без исходников требуемых NNeuronTrainer и NNeuronLearner.",
        "В ревизиях 5f3f06d от 15 апреля и 0be546f от 27 июня есть изменения конструктора синапса. В обеих фабричный профиль Bio для регистрации класса указывает 86 МОм и 5 мс. Применённые в расчёте значения установлены по отдельным моделям и проверяются после всех настроек создаваемого компонента.",
    ] + ([f"С первичными ячейками длин и числа синапсов сверены {sources['structure']['records']} записей, включая четыре пары согласованных архивных вариантов. Пропуски и значения в скобках сохранены. Дополненные из других источников параметры подписаны отдельно."] if "structure" in sources else []), [history_chart]))

    parser_runs = [p for p in data["processes"] if p["phase"] == "parser" and p["status"] == "completed"]
    sections.append(section("2 Контроль измерительного стенда", [
        f"Контроль EOF использует 30 входов подвыборки в исходном порядке. Завершены {len(parser_runs)} проверки. Протоколы с переводом строки и без него требуют ровно 30 успешных чтений. Обрыв последнего вектора принимается как 29 полных записей и ошибка извлечения трёх значений.",
        "Фрагмент исторического TreatDataFromFile проверял eof до извлечения и задавал длительность как период стимула за вычетом одного такта. Вызов фрагмента в полном расчётном цикле отсутствует. Проверки 1333 и 1334 тактов и включения первого отсчёта характеризуют чувствительность к границе измерения. Источник лишнего нуля в конкретном историческом файле остаётся гипотезой.",
        "В стенде записывается порядок списков модели, оболочки и нейрона. Причины нативного завершения, запланированного числа итераций, лимитов модельного и машинного времени записываются отдельными полями. Исходный стенд мог обозначать ручное упорядочивание как штатное и присваивать один статус двум разным ограничениям.",
        (f"Сохранённые сборки подтвердили прежние векторы для {sum(r['matches'] for r in reference)} из {len(reference)} проверенных конфигураций. "
         f"Точный SHA256 исходного бинарника найден для {sum(r['exact_original_binary'] for r in reference)} измерений."
         if reference else "Точный SHA256 бинарника первого отчёта отсутствует среди доступных копий. Сопоставление с журналами ведётся по закреплённым конфигурациям и сохранённой контрольной сборке."),
    ]))

    by_factor = defaultdict(list)
    for row in pairs:
        by_factor[row["label"], row["factor"]].append(row)
    certified = {key: sorted(group, key=lambda r: r["repeat"]) for key, group in by_factor.items()
                 if len(group) == 3 and all(r["physical_reversal"] for r in group)
                 and len({tuple((c["id"], c["before"], c["after"]) for c in r["changed"]) for r in group}) == 1}
    inference_charts = []
    paragraphs = [
        f"Выполнено {len(pairs)} парных сравнений. Для {len(certified)} сочетаний модели и фактора получены три согласованных повтора с возвратом исходного вектора. Включены также нулевые эффекты. Для каждого ответа книга хранит направление изменения и запас до порога в микровольтах.",
        "Порядок компонентов, сброс, изменение фактической последовательности из-за длительности окна, округление и выбор сигнала оцениваются на одном графе. Изменение раннего сигнала и смена бинарного решения привязываются к своим тактам. При совпадении структуры особое значение сохраняют история входов и фазовое состояние генераторов.",
    ]
    if any(r.get("tested_inputs", 150) < 150 or r.get("observation_mode") != "separate_process" for r in pairs):
        paragraphs.append("Первые проходы физических вариантов используют исходную последовательность. Для независимых повторов допустим проверенный префикс, включающий все обнаруженные переключения и наибольшие отклонения потенциала у факторов без смены ответа. Префикс сверяется по времени и пикам. Два выходных сигнала могут читаться в одном проходе. Если в первом такте импульса нет, исключение этого такта не меняет бинарный ответ.")
    controls = (("NL22", "order"), ("new-NT111", "reset"))
    for index, key in enumerate(controls, 2):
        group = certified.get(key, by_factor.get(key, []))
        if not group or not group[0]["changed"]:
            continue
        row = group[0]
        changes = row["changed"]
        ids = ", ".join(str(c["id"]) for c in changes)
        status = "подтверждено экспериментом" if key in certified else "поддерживается ограниченными данными"
        name = "порядок расчёта" if key[1] == "order" else "сброс перед входом"
        effect = (f" В полном проходе число отличий от архивного столбца изменилось с "
                  f"{row['history_diff_before']} до {row['history_diff_after']}."
                  if row["history_diff_before"] is not None and row["tested_inputs"] == 150 else "")
        paragraphs.append(f"{key[0]}, {name}. Эффект {status}. Изменились ответы на входы № {ids}."
                          + effect)
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
    for trace in data["tick_comparisons"]:
        witness = {"NL22": 9, "new-NT111": 84}.get(trace["label"])
        if witness is None or (trace["label"], trace["factor"]) not in controls:
            continue
        events = {r["quantity"]: r["tick"] for r in trace["first_events"] if r["input_id"] == witness}
        if "synapses" in events and "registered" in events:
            paragraphs.append(f"Для {trace['label']} префикс из {trace['validated_prefix']} входов сверён с полным проходом. "
                              f"У входа № {witness} различие синаптического сигнала видно с такта {events['synapses']}, "
                              f"разность регистрируемого ответа — с такта {events['registered']}. "
                              "Ранние различия включают очень малые остаточные величины. Связь с бинарным ответом проверена обратным переключением фактора.")
            center = events["registered"]
            voltages = []
            for log in trace["logs"]:
                raw = ROOT / log / "waveforms.jsonl"
                voltages.append({r["tick"]: 1000 * r["zone_V"] for r in rows_of(raw)
                                 if r.get("input_id") == witness and r.get("zone_V") is not None
                                 and center-10 <= r["tick"] <= center+10})
            ticks = sorted(set.intersection(*(set(v) for v in voltages)))
            if ticks:
                rows = [[str(tick), voltages[0][tick], voltages[1][tick], 11.5] for tick in ticks]
                identifier = "R10" if trace["label"] == "NL22" else "R11"
                inference_charts.append(chart(identifier, f"LTZone перед сменой ответа на вход № {witness}",
                    "Такт наблюдения от смены входа", "Потенциал LTZone, мВ",
                    ["Такт", "Исходное условие", "Изменённое условие", "Порог"], rows,
                    "Показано окно в 21 такт вокруг первого различия зарегистрированного ответа. Потенциалы взяты из потактового журнала при 2000 Гц.",
                    format="0.0", minimum=max(0, min(min(r[1:]) for r in rows)-0.2),
                    maximum=max(max(r[1:]) for r in rows)+0.2))
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
        common = min((diff["record"] - 1 for diff in prefixes if diff), default=strict[0]["iterations"])
        paragraphs.append(f"Строгий NT22 с пределами 1000 итераций и 1800 секунд завершил наблюдение на итерациях {', '.join(str(r['iterations']) for r in strict)}. "
                          f"Общий совпадающий префикс включает {common} зарегистрированных записей. "
                          "Завершение по учебному критерию не наблюдалось. Для общего вывода о сходимости необходимы дополнительные сведения о полном состоянии алгоритма.")
        def sample(path):
            return {r["iteration"]: sum(r["synapses"]) for r in rows_of(path / "iterations.jsonl")}
        series = [sample(ROOT / r["directory"]) for r in strict]
        indices = range(1, max(max(s) for s in series) + 1, 25)
        rows = [[str(i), *[s.get(i) for s in series]] for i in indices]
        training_charts.append(chart("R04", "Траектория строгого варианта NT22", "Учебная итерация", "Синапсы, шт.",
            ["Итерация", *[f"Повтор {i+1}" for i in range(len(series))]], rows,
            "Показаны измеренные точки с шагом 25 итераций, начиная с первой. Последние итерации по каждому повтору приведены в тексте и журнале."))
        save(WORK / "strict-common-prefix.json", prefixes)
    factors = [row for row in trained if row["phase"] == "training-factors"]
    own = sum(row["own_recognized"] is not None for row in factors)
    paragraphs.append(f"По изолированным факторам получено {len(factors)} записей обучения и {own} проверок своего входа после загрузки. Физические параметры взяты из сохранённых графов. Частично восстановленный учебный цикл сочетает архивный фрагмент и решения из Git. Результаты относятся к этой реализации на современном ядре.")
    crossed = [[algorithm, profile, [r for r in factors if r["run"].startswith(f"{algorithm}-{profile}-")]]
               for algorithm in ("modern", "archive") for profile in ("default", "secretion2")]
    if all(rows for _, _, rows in crossed):
        conditions = []
        for algorithm, profile, rows in crossed:
            observed_own = [r for r in rows if r["own_recognized"] is not None]
            name = "современный" if algorithm == "modern" else "частично архивный"
            profile_name = "современный профиль" if profile == "default" else "секреция 2 мс"
            conditions.append(f"{name} цикл, {profile_name} — {sum(r['own_recognized'] for r in observed_own)} "
                              f"из {len(observed_own)} проверок собственного входа")
        paragraphs.append("Скрещивание двух циклов и двух профилей дало следующие функциональные результаты. "
                          + ". ".join(conditions).capitalize() + ".")
    zone_pairs = []
    for profile, name in (("default", "Исходный уровень"), ("secretion2", "Секреция 2 мс"),
                          ("dissociation2", "Диссоциация 2 мс"), ("resistance100", "Сопротивление 100 МОм")):
        selected = {}
        for algorithm in ("modern", "archive"):
            row = next((r for r in factors if r["run"] == f"{algorithm}-{profile}-learner-22-r1"), None)
            selected[algorithm] = row.get("own_zone_mV") if row else None
        if any(value is not None for value in selected.values()):
            zone_pairs.append([name, selected["modern"], selected["archive"], 11.5])
    if zone_pairs:
        training_charts.append(chart("R09", "Пик LTZone после обучения NL22", "Фактический профиль синапса",
            "Потенциал LTZone, мВ", ["Профиль", "Современный цикл", "Частично архивный цикл", "Порог"],
            zone_pairs, "Измерение выполнено на собственном входе после загрузки. Для каждого изменённого параметра проверено его значение в сохранённом графе. Пустые точки соответствуют отсутствующим сочетаниям.",
            format="0.0"))
    fixed = {r["profile"]: r for r in data["profile_inference"] if r["label"] == "NL22" and r["repeat"] == 1}
    if all(profile in fixed for profile in ("default", "dissociation2", "resistance100", "reversal")):
        names = (("default", "Исходный"), ("dissociation2", "Диссоциация 2 мс"),
                 ("resistance100", "Сопротивление 100 МОм"), ("reversal", "Возврат"))
        rows = [[label, *[fixed[profile]["metrics"][metric] for metric in ("TP", "FP", "FN", "TN")]]
                for profile, label in names]
        training_charts.append(chart("R14", "Параметры синапсов на фиксированном графе NL22",
            "Фактический профиль при инференсе", "Количество ответов, шт.",
            ["Профиль", "TP", "FP", "FN", "TN"], rows,
            "Все четыре измерения сделаны на сохранённой конфигурации с прежними связями и порогом. "
            "Ложные срабатывания FP и пропуски FN показывают разные деградации в ответах.",
            type="bar", maximum=100))
        paragraphs.append(f"При фиксированных связях NL22 в первом полном сравнении диссоциация 2 мс изменила "
                          f"{len(fixed['dissociation2']['changed_ids'])} ответов, а сопротивление 100 МОм — "
                          f"{len(fixed['resistance100']['changed_ids'])}. Возврат исходного профиля дал "
                          f"{len(fixed['reversal']['changed_ids'])} различий с исходным вектором. "
                          "Числа относятся к применённым параметрам этого графа.")
    for factor in ("Фактическая диссоциация", "Фактическое сопротивление", "Допуск амплитуды",
                   "Продолжение после удаления", "Пересечение цели", "Явное обновление порядка при обучении"):
        comparisons = [r for r in data.get("training_comparisons", []) if r["factor"] == factor]
        local = next((r for r in comparisons if r["job"] == "trainer-22-r1"), None)
        if local and local["first_difference"]:
            first = local["first_difference"]
            paragraphs.append(f"{factor}. Для NT22 в первом повторе первая расходящаяся запись имеет номер {first['record']}. "
                              f"Число итераций в паре {local['iterations'][0]} и {local['iterations'][1]}. "
                              "Изменившиеся поля и измеренные такты приведены в книге.")
    order_expansion = WORK / "training-order-expansion.json"
    if order_expansion.exists():
        accepted = [r["kind"] for r in load(order_expansion) if r["expanded"]]
        named = {"learner": "NL", "trainer": "NT"}
        enlarged = [r for r in data["training_comparisons"]
                    if r["factor"] == "Явное обновление порядка на контрольной десятке"]
        if accepted:
            paragraphs.append(f"Для {', '.join(named[kind] for kind in accepted)} вариант с изменённым вызовом UpdateComputationOrder "
                              "сохранил ответ на свой вход во всех трёх проверках № 22. "
                              f"За пределами пилотных объектов измерено {len(enlarged)} пар. "
                              f"В {sum(r['first_difference'] is not None for r in enlarged)} из них различается траектория учебных событий.")
        archived = next((row for row in sources.get("structure", {}).get("examples", [])
                         if row["input_id"] == 22), None)
        if archived:
            for kind, tag, identifier in (("trainer", "NT", "R12"), ("learner", "NL", "R13")):
                variants = [next((r for r in trained if r["phase"] == "training-order" and
                                  r["run"] == f"{mode}-{kind}-22-r1"), None)
                            for mode in ("native", "disabled")]
                if not all(variants):
                    continue
                historical = archived[tag + "_d"]
                rows = [[str(i + 1), historical[i], *(row["d"][i] for row in variants)] for i in range(5)]
                training_charts.append(chart(identifier, f"Исторические и измеренные длины {tag}22",
                    "Номер входного канала", "Длина дендрита, сегм.",
                    ["Книга 2022 г.", "Исходное обучение", "Без явного вызова"], rows,
                    "Длины из исходной структурной таблицы сопоставлены с результатом первого повтора. "
                    "Для этого входа источник не содержит полного числа синапсов. Совпадение длин допускает несколько физических графов."))
    decision_path = WORK / "training-expansion-decision.json"
    if decision_path.exists():
        decisions = load(decision_path)
        paragraphs.append(f"В контрольную десятку включены {sum(r['expanded'] for r in decisions)} из {len(decisions)} сочетаний варианта и алгоритма. "
                          "Для включения фиксировалось повторившееся изменение структурного результата или завершения вместе с реакцией на обучающий вход после загрузки.")
    selections = [(name, [r for r in factors if r["run"].startswith(name + "-trainer-22-r")])
                  for name in ("modern-default", "stop-tolerance", "stop-keep", "stop-strict", "stop-crossing", "stop-reversal")]
    stop_names = ("Исходное", "Без допуска", "После удаления", "Оба изменения", "Пересечение", "Возврат")
    stop = [[label, *[next((r["iterations"] for r in rows if r["run"].endswith(f"-r{i}")),
             None) for i in (1, 2, 3)]] for label, (_, rows) in zip(stop_names, selections, strict=True) if rows]
    if stop:
        training_charts.append(chart("R05", "Условия остановки обучения NT22", "Вариант правила", "Итерации, шт.",
            ["Вариант", "Повтор 1", "Повтор 2", "Повтор 3"], stop,
            "Завершения и достижения лимита представлены в исходной таблице. Точно совпавшее число итераций не заменяет проверку флага завершения.",
            type="bar"))
    sections.append(section("4 Первая разность в обучении", paragraphs, training_charts))

    contexts = data["sequence_context"]
    context_charts = []
    paragraphs = [f"По двум схемам получено {len(contexts)} выровненных записей учебных этапов в живом режиме, режиме снимков и режиме пауз. Сопоставлены физическая структура, число итераций и время модели. Инференс снимка выполняется в отдельном процессе на замороженном графе."]
    if data.get("warm_prefix_22_37"):
        warm = data["warm_prefix_22_37"]
        first = warm[0]
        paragraphs.append(f"В непрерывной последовательности с архивной точностью входов отдельно повторён первый переход № 22 → № 37. "
                          f"В первом повторе архивные длины {first['historical_d']} и современные {first['observed_d']}. "
                          f"Число итераций {first['historical_iterations']} и {first['observed_iterations']}. "
                          f"Всего измерено {len(warm)} повторов. Архивная таблица содержит конечные значения, поэтому точный такт расходящегося исторического решения остаётся неизвестным.")
    for scheme, identifier in (("0_1", "R06"), ("0_1_4_full", "R07")):
        relevant = [r for r in contexts if r["scheme"] == scheme and r["repeat"] == 1]
        differing = [r for r in relevant if (r["d"][0], r["s"][0]) != (r["d"][1], r["s"][1])]
        pause_diff = [r for r in relevant if (r["d"][1], r["s"][1]) != (r["d"][2], r["s"][2])]
        if relevant:
            paragraphs.append(f"Схема {scheme}, первый повтор. При сравнении живого теста с обучением без теста различий графа на учебных этапах {len(differing)} из {len(relevant)}."
                              + (f" Первое наблюдаемое различие на этапе {differing[0]['stage']}." if differing else ""))
        if pause_diff:
            first = pause_diff[0]["stage"]
            where = f"в контрольном состоянии {first + 1}" if scheme == "0_1" else f"на учебном этапе {first} контроллера"
            paragraphs.append(f"При запрете импульсов во время модельной паузы первое различие в схеме {scheme} возникло {where}. "
                              f"Различаются {len(pause_diff)} графов. Вмешательство сочетает продвижение среды и подавление генерации. Причину внутри этого сочетания следует связывать с измеренными фазами и импульсами.")
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
        if pause_diff and scheme == "0_1":
            rows = [[str(r["stage"]+1), *[sum(s) for s in r["s"]]] for r in relevant]
            context_charts.append(chart("R08", "Структура при одиночных итерациях № 61", "Номер контрольного состояния",
                "Синапсы, шт.", ["Состояние", "Живой тест", "Без теста", "Пауза без импульсов"], rows,
                "Совпадающие линии перекрываются. Пауза продвигает модельное время при отключённых генераторах, после чего их активность восстанавливается."))
    sections.append(section("5 Влияние оценки на последующее обучение", paragraphs, context_charts))

    coverage_line = ""
    if coverage:
        pending = [row for row in coverage["phases"] if row["pending_processes"] or row["running"] or row["failed_processes"]]
        if pending:
            coverage_line = "Серии с неполным покрытием: " + ", ".join(
                f"{row['phase']} ({row['completed_processes']}/{row['planned']})" for row in pending) + "."
        else:
            coverage_line = "Покрытие запланированных процессов сведено в таблицу книги."
    sections.append(section("6 Границы выводов и материалы", [
        "Подтверждены только эффекты с измеренным вмешательством и проверкой возврата. Для исторических расхождений полный комплект первичных сигналов и исходных кодов 2022 года отсутствует. Архивные альтернативы графа, различия порядка и состояния при предъявлении дают несколько совместимых объяснений.",
        "Доказанный дефект регистрации стенда исправлен. Подтверждение ошибки исторической таблицы требует расхождения с первичным файлом при согласованной привязке. Совпадение опубликованных счётов с первичными файлами подтверждает их арифметику. Источник необъяснённой 31-й строки и конкретная причина оставшихся исторических расхождений не установлены.",
        f"По журналам учтено {len(data['processes'])} процессов. Завершено {counts['completed']}. Остальные случаи и достигнутые внутри процесса ограничения доступны в книге. Использована сборка Release и запуск из Bin/Platform/Win. Степень подтверждения отдельных факторов следует оценивать по конкретным экспериментам и числу доступных повторов.",
        "Источники предшествующей проверки — ScientificComparisons и TrainingReproducibility. Исходные материалы находятся в Docs/ClassicStructTrainExperiments/Эксперименты. Реестр, нативные журналы и контрольные суммы находятся в Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124.",
    ] + ([coverage_line] if coverage_line else [])))
    overview = [
        ["Архивные ответы", sources["recognition_cells_verified"], "Сверено с ячейками первичной книги"],
        ["Состояния в схемах", len(sources["protocols"]), "Сверены структура и пообъектные ответы"],
        ["Завершённые процессы", counts["completed"], "Технический статус процесса"],
        ["Парные проверки инференса", len(pairs), "Есть база, изменение и обратный контроль"],
        ["Аудит влияния трассировки", len(observer), "Пары фактических попыток обучения"],
        ["Сопоставление контекста", len(contexts), "Выровненные стадии среды обучения"],
    ]
    findings = [
        ["Регистрация порядка и границы остановки", "Подтверждено экспериментом",
         "Журналы новых запусков содержат фактический порядок и отдельные причины остановки."],
        ["Происхождение 31-го нуля в архивных файлах", "Гипотеза",
         "Лишняя попытка извлечения при завершающем переводе строки возможна. Полная историческая цепочка вызова отсутствует."],
        ["Ошибка опубликованных исторических счётов", "Не установлено",
         "В пересчитанных 14 состояниях и проверенных ответах исходные записи согласованы."],
        ["Принципиальная несходимость строгого NT22", "Не установлено",
         "Наблюдение до предела времени не доказывает недостижимость условия остановки."],
        ["Точное восстановление исторического исполняемого файла", "Не установлено",
         "Архивный фрагмент и реализации из Git относятся к разным версиям."],
    ]
    for key in sorted(by_factor):
        group = by_factor[key]
        if not any(r["changed"] for r in group):
            continue
        label, factor = key
        stable = key in certified
        finding = "Подтверждено экспериментом" if stable else "Поддерживается ограниченными данными"
        findings.append([f"{label} / {factor}", finding,
                         f"Смены ответов в {len(group)} парных сравнениях. Применимость ограничена данным графом и последовательностью."])
    save(WORK / "diagnosis-report.json", {"lead": "Исследование сопоставляет первичные исторические записи, результаты прежнего инференса и новые контролируемые расчёты. Для каждого выявленного различия учитываются граф, стимул, внутреннее состояние и способ измерения.",
                                         "sections": sections, "overview": overview, "findings": findings})


if __name__ == "__main__":
    run()
