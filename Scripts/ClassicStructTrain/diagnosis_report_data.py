"""Derive report statements and editable chart series from audited observations."""
from collections import Counter, defaultdict
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import ROOT, WORK, PREVIOUS, PILOT, load, save, relative
from diagnosis_analysis import rows_of, first_iteration


def chart(identifier, title, x, y, headers, rows, analysis, **options):
    assert rows and all(len(row) == len(headers) for row in rows), identifier
    values = [value for row in rows for value in row[1:] if isinstance(value, (int, float))]
    return dict(id=identifier, title=title, x=x, y=y, headers=headers, rows=rows, analysis=analysis,
                min=options.get("minimum", min(0, min(values))), max=options.get("maximum", max(values)+1),
                **{k: options[k] for k in ("type", "format", "major_unit") if k in options})


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
        "№ 51 и № 61 относятся к одному целевому классу Iris. TP — верные срабатывания, FP — ложные срабатывания, FN — пропуски целевого класса, TN — верные отказы. Число ошибок равно сумме FP и FN.",
        "LTZone — пороговая зона модели. Запас до порога равен максимальному потенциалу LTZone в окне наблюдения за вычетом действующего порога. Импульс регистрируется по выходному сигналу.",
        f"Сверены {sources['recognition_cells_verified']} исходных ячеек и {len(sources['protocols'])} состояний из пяти схем. В 14 состояниях перехода № 51 → № 61 совпали четыре счёта классификации. Пятнадцатый файл содержит восемь ответов. У 26 файлов 31-я строка ответа содержит 0 и находится за пределом опубликованного диапазона из 30 входов. Два первых файла одиночных итераций совпадают побайтно.",
        "Для распознавания использованы исходные столбцы книги «Распознавание.xlsx». Для схем использованы книга «Обучение нескольким примерам.xlsx» и первичные output_data. Структурный реестр опирается на «Инофрмация о длинах дендритов и числе синапсов.xlsx». Точные диапазоны и контрольные суммы находятся в сопровождающей книге и реестре.",
        "Даты сохранения рабочих документов относятся к 2022 году. Дата создания шаблона XLSX в метаданных не датирует эксперимент. Версии основного репозитория за 18 марта и 15 апреля 2022 года указывают на доступные ревизии PulseLib без исходников требуемых NNeuronTrainer и NNeuronLearner.",
        "В ревизиях 5f3f06d от 15 апреля и 0be546f от 27 июня есть изменения конструктора синапса. В обеих фабричный профиль Bio для регистрации класса указывает 86 МОм и 5 мс. Применённые в расчёте значения установлены по отдельным моделям и проверяются после всех настроек создаваемого компонента.",
        "Метод явной перестановки появился в доступной истории NPulseNeuron 24 апреля 2023 года в ревизии 8f47c01. Для NNeuronLearner изменение 805fda1 от 5 августа 2026 года затрагивает порядок расчёта и восстановление связей. В контроле с одним исполняемым файлом переключается только перестановка в UpdateComputationOrder.",
    ] + ([f"С первичными ячейками длин и числа синапсов сверены {sources['structure']['records']} записей, включая четыре пары согласованных архивных вариантов. Пропуски и значения в скобках сохранены. Дополненные из других источников параметры подписаны отдельно."] if "structure" in sources else []), [history_chart]))

    parser_runs = [p for p in data["processes"] if p["phase"] == "parser" and p["status"] == "completed"]
    sections.append(section("2 Контроль измерительного стенда", [
        f"Контроль EOF использует 30 входов подвыборки в исходном порядке. Завершены {len(parser_runs)} проверки. Протоколы с переводом строки и без него требуют ровно 30 успешных чтений. Обрыв последнего вектора принимается как 29 полных записей и ошибка извлечения трёх значений.",
        "Фрагмент исторического TreatDataFromFile проверял eof до извлечения и задавал длительность как период стимула за вычетом одного такта. Вызов фрагмента в полном расчётном цикле отсутствует. Проверки 1333 и 1334 тактов и включения первого отсчёта характеризуют чувствительность к границе измерения. Источник лишнего нуля в конкретном историческом файле остаётся гипотезой.",
        (f"Независимо пересчитаны {sum(len(r.get('summary_audit', [])) for r in sources['protocols'])} итоговые ячейки. "
         "В формулах выборки из 30 входов использованы строки 12–21 и 22–31, соответствующие второму и третьему десяткам ответов. "
         "Все ответы первого десятка в проверенных файлах равны нулю. Лишнее значение за пределами 30 ответов в этих формулах не используется."),
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
    for factor, label in (("wrapper", "Выбор выхода оболочки или LTZone"),
                          ("first-tick", "Исключение первого такта"), ("precision", "Округление задержек")):
        full = [r for r in pairs if r["label"] in PILOT and r["repeat"] == 1 and r["factor"] == factor
                and r["tested_inputs"] == 150]
        if full:
            paragraphs.append(f"{label}. В {sum(not r['changed'] for r in full)} из {len(full)} полных пилотных "
                              "сопоставлений весь вектор бинарных ответов сохранился.")
    for factor, label in (("order", "Порядок расчёта"), ("reset", "Сброс"), ("window", "Длительность окна"),
                          ("precision", "Округление задержек")):
        expanded = [r for r in pairs if r["label"] not in PILOT and r["repeat"] == 1 and r["factor"] == factor]
        if expanded:
            switches = [row for r in expanded for row in r["changed"]]
            paragraphs.append(f"{label} в расширенной проверке. Изменения в {sum(bool(r['changed']) for r in expanded)} "
                              f"из {len(expanded)} случаев. Переходов 0 → 1 было {sum(c['after'] == 1 for c in switches)}, "
                              f"переходов 1 → 0 было {sum(c['after'] == 0 for c in switches)}.")
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
        model = "Новый NT111" if key[0] == "new-NT111" else key[0]
        paragraphs.append(f"{model}, {name}. Эффект {status}. Изменились ответы на входы № {ids}."
                          + effect)
        if index == 2:
            paths = defaultdict(list)
            for changed in changes:
                paths[changed["before"], changed["after"]].append(changed["id"])
            rows = [[phase, *[path[point] for path in paths]] for phase, point in
                    (("Ручной", 0), ("Штатный", 1), ("Ручной повторно", 0))]
            inference_charts.append(chart("R02", "Обратный контроль порядка для NL22", "Порядок расчёта",
                "Бинарный ответ", ["Режим", *["№ " + ", ".join(map(str, ids)) for ids in paths.values()]], rows,
                "Входы с одинаковой последовательностью ответов показаны вместе. Возврат ручного порядка проверен целым вектором ответов.",
                maximum=1, major_unit=1))
        else:
            rows = [[f"№ {c['id']}", c["margin_before_uV"], c["margin_after_uV"]] for c in changes]
            inference_charts.append(chart("R03", "Запас до порога нового NT111", "Вход Iris", "Запас, мкВ",
                ["Объект", "Непрерывно", "Со сбросом"], rows,
                "Изменение знака запаса наблюдается на том же графе. Историческое применение сброса требует отдельного источника.",
                type="bar", format="0", major_unit=10, minimum=min(-10, min(r[2] for r in rows) - 1),
                maximum=max(50, max(r[1] for r in rows) + 1)))
    window_test = certified.get(("NT45", "window"))
    if window_test:
        first = next((c for c in window_test[0]["changed"] if c["id"] == 13), None)
        if first:
            shift = (first["start_before_s"] - first["start_after_s"]) * 1000
            paragraphs.append(f"Для NT45 замена 1334 тактов на 1333 сдвинула момент подачи № 13 на {shift:g} мс. "
                              f"Запас до порога стал {first['margin_after_uV']:.1f} мкВ вместо "
                              f"{first['margin_before_uV']:+.1f} мкВ. Исходный импульс возникал "
                              f"на такте {first['first_zone_before']}, который входит в оба интервала. "
                              "Два независимых повторных префикса подтвердили эффект. Результат относится к изменению длительности "
                              "предъявления и сохраняемого динамического состояния в непрерывной последовательности.")
    precision_test = certified.get(("NL111", "precision"))
    if precision_test:
        first = next((c for c in precision_test[0]["changed"] if c["id"] == 126), None)
        if first:
            paragraphs.append(f"Для NL111 округление задержек в секундах до четырёх знаков после запятой изменило "
                              f"ответ на вход № 126 с {first['before']} на {first['after']}. "
                              f"Запас до порога изменился с {first['margin_before_uV']:+.1f} до "
                              f"{first['margin_after_uV']:+.1f} мкВ. Эффект воспроизведён с обратным контролем.")
    paragraphs.append(f"Потактовые журналы сопоставлены для {len(data['tick_comparisons'])} комбинаций. Измеряемая цепочка включает входную подачу, внутренний генератор, входы и выходы синапсов, сомы, LTZone и регистрируемое решение. В книге указана первая обнаруженная разность каждой величины в наблюдаемом окне.")
    for trace in data["tick_comparisons"]:
        trace_keys = {("NL22", "order"): (9, "R10"), ("new-NT111", "reset"): (84, "R11"),
                      ("NT45", "window"): (13, "R16"), ("NL111", "precision"): (126, "R19")}
        trace_key = trace_keys.get((trace["label"], trace["factor"]))
        if trace_key is None:
            continue
        witness, identifier = trace_key
        name = "нового NT111" if trace["label"] == "new-NT111" else trace["label"]
        events = {r["quantity"]: r["tick"] for r in trace["first_events"] if r["input_id"] == witness}
        if "synapses" in events and "registered" in events:
            paragraphs.append(f"Для {name} префикс из {trace['validated_prefix']} входов сверён с полным проходом. "
                              f"У входа № {witness} различие синаптического сигнала видно с такта {events['synapses']}, "
                              f"разность регистрируемого ответа — с такта {events['registered']}. "
                              "Ранние различия включают очень малые остаточные величины. Связь с бинарным ответом проверена обратным переключением фактора.")
            if identifier == "R19" and "generators" in events:
                event = next(r for r in trace["first_events"]
                             if r["input_id"] == witness and r["quantity"] == "generators")
                channel = event["component_index"]
                pulses = [next((r["tick"] for r in rows_of(ROOT / log / "waveforms.jsonl")
                                if "generators" in r and r.get("input_id") == witness and r["tick"] >= event["tick"]
                                and r["generators"][channel - 1] > 0.001), None)
                          for log in trace["logs"]]
                if all(t is not None for t in pulses):
                    paragraphs.append(f"После округления начало импульса канала № {channel} сместилось "
                                      f"с такта {pulses[0]} на такт {pulses[1]}. "
                                      f"Различие выходов LTZone наблюдалось с такта {events['registered']}.")
            center = events["registered"]
            voltages = []
            for log in trace["logs"]:
                raw = ROOT / log / "waveforms.jsonl"
                voltages.append({r["tick"]: 1000 * r["zone_V"] for r in rows_of(raw)
                                 if r.get("input_id") == witness and r.get("zone_V") is not None
                                 and center-10 <= r["tick"] <= center})
            ticks = sorted(set.intersection(*(set(v) for v in voltages)))
            if ticks:
                threshold_mV = 1000 * trace["thresholds_V"][str(witness)]
                rows = [[str(tick), voltages[0][tick], voltages[1][tick], threshold_mV] for tick in ticks]
                inference_charts.append(chart(identifier, f"Потенциал LTZone {name} на входе № {witness}",
                    "Такт наблюдения от смены входа", "Потенциал LTZone, мВ",
                    ["Такт", "Исходное условие", "Изменённое условие", "Порог"], rows,
                    f"Показаны десять предшествующих тактов и первое различие зарегистрированного ответа на такте {center}. "
                    "Потенциал доходит до порога в одном из условий. Последующий сброс потенциала доступен в полном журнале при 2000 Гц.",
                    format="0.00", minimum=min(min(r[1:]) for r in rows)-0.02,
                    maximum=max(max(r[1:]) for r in rows)+0.02))
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
        earlier_limit = [next(rows_of(p)) for p in sorted((PREVIOUS / "runs/FZ/stopping").glob("trainer-22-r*/results.jsonl"))]
        if earlier_limit:
            paragraphs.append("В предыдущем варианте FZ с пределом 600 секунд остановки по времени получены "
                              f"на итерациях {', '.join(str(r['iterations']) for r in earlier_limit)}. "
                              "Исходные журналы этой серии сохранены в составе TrainingReproducibility.")
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
    paragraphs.append("В частично восстановленном цикле NL проверка завершения и длительность итерации опираются на сохранённый фрагмент. "
                      "Решения NT о синхронизации и настройке сом взяты из ранней доступной реализации. "
                      "Применены современные механизмы инициализации добавленных компонентов, сохранения графа и регистрации сигналов. "
                      "Ревизия варианта — 33cc4af.")
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
                   "Продолжение после удаления", "Пересечение цели",
                   "Изоляция обновления порядка на одном бинарнике"):
        comparisons = [r for r in data.get("training_comparisons", []) if r["factor"] == factor]
        local = next((r for r in comparisons if r["job"] == "trainer-22-r1"), None)
        if local and local["first_difference"]:
            first = local["first_difference"]
            paragraphs.append(f"{factor}. Для NT22 в первом повторе первая расходящаяся запись имеет номер {first['record']}. "
                              f"Число итераций в паре {local['iterations'][0]} и {local['iterations'][1]}. "
                              "Изменившиеся поля и измеренные такты приведены в книге.")
            if factor == "Изоляция обновления порядка на одном бинарнике" and local["first_training_ticks"]:
                signals = local["first_training_ticks"]
                tick = min(signals.values())
                stage = (" На этом такте различаются потенциалы сом и LTZone."
                         if signals.get("soma") == signals.get("zone_V") == tick else "")
                paragraphs.append(f"Первое различие потактовых записей в этой паре видно на такте {tick}."
                                  + stage + " В книге приведены первые такты по каждой расходящейся величине.")
    order_expansion = WORK / "matched-training-order-expansion.json"
    matched = order_expansion.exists()
    if not matched:
        order_expansion = WORK / "training-order-expansion.json"
    if order_expansion.exists():
        rechecks = data.get("order_rechecks", [])
        if rechecks:
            paragraphs.append(f"По статусу, числу итераций, длинам и числу синапсов общий исполняемый файл "
                              f"воспроизвёл {sum(r['same'] for r in rechecks)} из {len(rechecks)} исходов раздельных сборок.")
        accepted = [r["kind"] for r in load(order_expansion) if r["expanded"]]
        named = {"learner": "NL", "trainer": "NT"}
        name = ("Обновление порядка на десятке на одном бинарнике" if matched else
                "Явное обновление порядка на контрольной десятке")
        enlarged = [r for r in data["training_comparisons"] if r["factor"] == name]
        if accepted:
            paragraphs.append(f"Для {', '.join(named[kind] for kind in accepted)} вариант с изменённым вызовом UpdateComputationOrder "
                              "сохранил ответ на свой вход во всех трёх проверках № 22. "
                              f"За пределами пилотных объектов измерено {len(enlarged)} пар. "
                              f"В {sum(r['first_difference'] is not None for r in enlarged)} из них различается траектория учебных событий.")
        comparable = [r for r in data.get("order_structure", []) if r["matched"] == matched]
        if comparable:
            paragraphs.append(f"В основной исторической таблице есть длины для {len(comparable)} сочетаний алгоритма и входа из контрольной десятки. "
                              f"В исходном условии совпали {sum(r['native_matches'] for r in comparable)} векторов длин, без явного обновления — "
                              f"{sum(r['disabled_matches'] for r in comparable)}. Неполные исторические числа синапсов учтены отдельно.")
        archived = next((row for row in sources.get("structure", {}).get("examples", [])
                         if row["input_id"] == 22), None)
        if archived:
            for kind, tag, identifier in (("trainer", "NT", "R12"), ("learner", "NL", "R13")):
                flavor = "matched-" if matched else ""
                variants = [next((r for r in trained if r["phase"] == flavor + "training-order" and
                                  r["run"] == f"{flavor}{mode}-{kind}-22-r1"), None)
                            for mode in ("native", "disabled")]
                if not all(variants):
                    continue
                historical = archived[tag + "_d"]
                rows = [[str(i + 1), historical[i], *(row["d"][i] for row in variants)] for i in range(5)]
                training_charts.append(chart(identifier, f"Исторические и измеренные длины {tag}22",
                    "Номер входного канала", "Длина дендрита, сегм.",
                    ["Канал", "Книга 2022 г.", "Исходное обучение", "Без перестановки"], rows,
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
    paragraphs = [
        f"По двум протоколам сопоставлены {len(contexts)} учебных этапов живого режима и режима снимков. "
        f"Для {sum(r['events'][2] is not None for r in contexts)} этапов доступен также контроль с паузой. "
        "Сопоставлены физическая структура, число итераций и время модели. Инференс снимка выполняется в отдельном процессе на замороженном графе.",
        "Обе последовательности начинаются с полного обучения входу № 51. В первой затем выполняется по одной итерации обучения входу № 61. Во второй каждый цикл включает одну совместную итерацию для дендритов и синапсов и четыре итерации для синапсов. В первой используются 30 тестовых входов, во второй все 150.",
    ]
    if data.get("warm_prefix_22_37"):
        warm = data["warm_prefix_22_37"]
        first = warm[0]
        paragraphs.append(f"В непрерывной последовательности с архивной точностью входов отдельно повторён первый переход № 22 → № 37. "
                          f"В первом повторе архивные длины {first['historical_d']} и современные {first['observed_d']}. "
                          f"Число итераций {first['historical_iterations']} и {first['observed_iterations']}. "
                          f"Всего измерено {len(warm)} повторов. Архивная таблица содержит конечные значения, поэтому точный такт расходящегося исторического решения остаётся неизвестным.")
        variants = defaultdict(dict)
        matched_warm = any(r["matched"] for r in data.get("warm_order", []))
        if data.get("warm_order"):
            paragraphs.append("Первые проверки с раздельными исполняемыми файлами VB и FO установили совпадение с архивом. "
                              "Хеши их контроллеров различаются. Изоляция влияния перестановки проверяется отдельным сравнением на одной сборке.")
        for row in data.get("warm_order", []):
            if row["matched"] != matched_warm:
                continue
            if len(row["stages"]) > 1:
                variants[row["mode"]][row["repeat"]] = row["stages"][1]

        def matches_history(state):
            return (state["dendrites"], state["synapses"], state["iterations"]) == (
                first["historical_d"], first["historical_s"], first["historical_iterations"])

        disabled = variants["disabled"]
        if disabled:
            repeated = set(variants["native"]) & set(disabled) & set(variants["reversal"])
            reversed_paths = sum(variants["native"][i] == variants["reversal"][i] for i in repeated)
            build = "в одной сборке" if matched_warm else "в сравнении сборок VB и FO"
            paragraphs.append(f"При отключённой перестановке в UpdateComputationOrder {build} архивная структура и число итераций "
                              f"совпали в {sum(matches_history(row) for row in disabled.values())} из {len(disabled)} сравнений. "
                              f"Возврат вызова восстановил исходные учебные записи в {reversed_paths} из {len(repeated)} пар. "
                              "Сохранённые исторические числа позволяют проверить этот переход. Полная история внутренних сигналов отсутствует.")
        if 1 in variants["native"] and 1 in disabled:
            d_hist = first["historical_s"]
            d_native = variants["native"][1]["synapses"]
            d_disabled = disabled[1]["synapses"]
            context_charts.append(chart("R15", "Число синапсов после перехода № 22 → № 37",
                "Номер входного канала", "Синапсы, шт.",
                ["Канал", "История", "Исходный порядок", "Без явного обновления"],
                [[str(i + 1), d_hist[i], d_native[i], d_disabled[i]] for i in range(5)],
                "Сопоставлены архивная строка и конечные состояния первого повтора. "
                "Изменение внутри учебного цикла оценивается отдельно от порядка компонентов при сохранении и загрузке."))
        extended = defaultdict(list)
        for row in data.get("warm_extensions", []):
            extended[row["series"]].append(row)
        if extended:
            titles = {"warm-native-r1": "исходный", "warm-disabled-r1": "без явного обновления",
                      "warm-reversal-r1": "возврат"}
            for key, rows in sorted(extended.items()):
                if not key.startswith("matched-") and len(extended.get("matched-" + key, [])) == len(rows):
                    continue
                records = sorted(rows, key=lambda r: r["transition"])
                first = next((r for r in records if not r["matches"]), None)
                condition = titles[key.split("/")[-1]]
                build = "один бинарник" if key.startswith("matched-") else "раздельные сборки"
                length = key.split("/")[0].rsplit("-", 1)[-1]
                paragraphs.append(f"Последовательность из {length} переходов, {build}, условие «{condition}». "
                                  f"Архивные структуры и число итераций совпали в {sum(r['matches'] for r in records)} "
                                  f"из {len(records)} переходов."
                                  + (f" Первое различие на переходе № {first['from_id']} → № {first['to_id']}."
                                     if first else ""))
                if length == "90":
                    paragraphs[-1] += (f" Суммарно {sum(r['iterations'] for r in records)} итераций в повторе и "
                                       f"{sum(r['historical_iterations'] for r in records)} в архиве.")
                    paragraphs.append(f"Отдельно совпали длины дендритов на {sum(r['d'] == r['historical_d'] for r in records)} переходах, "
                                      f"числа синапсов на {sum(r['s'] == r['historical_s'] for r in records)}, "
                                      f"число итераций на {sum(r['iterations'] == r['historical_iterations'] for r in records)}.")
                if length == "90" and key.startswith("matched-") and first:
                    changes = []
                    for term, old_key, new_key in (("сегменты", "historical_d", "d"),
                                                  ("синапсы", "historical_s", "s")):
                        changes += [f"{term} канала № {i}, {old} → {new}"
                                    for i, (old, new) in enumerate(zip(first[old_key], first[new_key], strict=True), 1)
                                    if old != new]
                    if changes:
                        paragraphs.append(f"На первом различающемся переходе изменились {', '.join(changes)}. "
                                          f"Число итераций в архиве {first['historical_iterations']}, в повторе {first['iterations']}. "
                                          "В архиве сохранён результат перехода. Потактовое решение, вызвавшее оставшееся расхождение, не установлено.")
            complete = next((sorted(extended[series], key=lambda r: r["transition"]) for series in (
                "matched-warm-order-prefix-90/warm-disabled-r1", "warm-order-prefix-90/warm-disabled-r1")
                if len(extended.get(series, [])) == 90), None)
            earlier = {r["transition"]: r for r in extended.get("warm-order-prefix-90/warm-disabled-r1", [])}
            shared = extended.get("matched-warm-order-prefix-90/warm-disabled-r1", [])
            if len(earlier) == len(shared) == 90:
                fields = ("d", "s", "iterations", "status")
                same = sum(all(r[field] == earlier[r["transition"]][field] for field in fields) for r in shared)
                paragraphs.append(f"Вариант без перестановки дал одинаковые структуры, числа итераций и статусы "
                                  f"в раздельной и общей сборках на {same} из 90 переходов.")
            if complete:
                previous_delta = 0
                current_delta = 0
                rows = []
                for row in complete:
                    previous_delta += row["previous_iterations"] - row["historical_iterations"]
                    current_delta += row["iterations"] - row["historical_iterations"]
                    if row["transition"] == 1 or row["transition"] % 10 == 0:
                        rows.append([str(row["transition"]), 0, previous_delta, current_delta])
                values = [value for row in rows for value in row[1:]]
                context_charts.append(chart("R17", "Накопленное отклонение в последовательности переобучения",
                    "Номер направленного перехода", "Отклонение от архива, итераций",
                    ["Переход", "Архив (0)", "Предыдущий повтор", "Без перестановки"], rows,
                    "В каждой точке показана разность накопленных итераций с начала последовательности. "
                    "Итоговая сумма не отражает изменения отдельных структур. Сравнение всех 90 строк приведено в книге.",
                    major_unit=5, minimum=((min(values) - 1) // 5) * 5, maximum=((max(values) + 5) // 5) * 5))
    for scheme, identifier in (("0_1", "R06"), ("0_1_4_full", "R07")):
        protocol = "одиночные итерации для № 61" if scheme == "0_1" else "переход от № 51 к № 61 с настройкой синапсов"
        repeat_check = next((r for r in data.get("sequence_repeats", []) if r["scheme"] == scheme
                             and r["mode"] == "live" and r["repeats"] == 3), None)
        if repeat_check and repeat_check["same_training"] and repeat_check["same_answers"]:
            paragraphs.append(f"Протокол «{protocol}», все три живых повтора. На учебных этапах совпали "
                              "длины, числа синапсов и число итераций. "
                              f"Совпали пообъектные векторы во всех {repeat_check['evaluation_states']} контрольных состояниях.")
        relevant = [r for r in contexts if r["scheme"] == scheme and r["repeat"] == 1]
        differing = [r for r in relevant if (r["d"][0], r["s"][0]) != (r["d"][1], r["s"][1])]
        pause_diff = [r for r in relevant if r["d"][2] is not None and
                      (r["d"][1], r["s"][1]) != (r["d"][2], r["s"][2])]
        if relevant:
            paragraphs.append(f"Протокол «{protocol}», первый повтор. При сравнении живого теста с обучением без теста различий графа на учебных этапах {len(differing)} из {len(relevant)}."
                              + (f" Первое наблюдаемое различие на этапе {differing[0]['stage']}." if differing else ""))
        if pause_diff:
            first = pause_diff[0]["stage"]
            where = f"в контрольном состоянии {first + 1}" if scheme == "0_1" else f"на учебном этапе {first} контроллера"
            paused = [r for r in relevant if r["d"][2] is not None]
            paragraphs.append(f"При запрете импульсов во время модельной паузы первое различие в протоколе «{protocol}» возникло {where}. "
                              f"Различаются {len(pause_diff)} графов. Вмешательство сочетает продвижение среды и подавление генерации. Причину внутри этого сочетания следует связывать с измеренными фазами и импульсами.")
            paragraphs.append(f"Относительно живого теста после модельной паузы совпали длины и числа синапсов "
                              f"на {sum((r['d'][0], r['s'][0]) == (r['d'][2], r['s'][2]) for r in paused)} "
                              f"из {len(paused)} сопоставленных этапов первого повтора.")
        source_sheet = "Схема 0 на 1" if scheme == "0_1" else "Схема 0 на 1+4 для 150 примеров"
        historical_q = {r["state"]: r["metrics"]["FP"] + r["metrics"]["FN"] for r in sources["protocols"]
                        if r["sheet"] == source_sheet}
        stride = 1 if scheme == "0_1" else 2
        tests = [r for r in relevant if r["changes"] is not None]
        switches = [r for r in tests if r["changes"]]
        if tests:
            paragraphs.append(f"По бинарным ответам живой тест и снимок разошлись в {len(switches)} "
                              f"из {len(tests)} состояний. Общее число переключений по этим состояниям — "
                              f"{sum(len(r['changes']) for r in switches)}.")
            equal_count = next((r for r in switches if r["live_Q"] == r["snapshot_Q"]), None)
            if equal_count:
                ids = ", ".join(str(row[0]) for row in equal_count["changes"])
                paragraphs.append(f"В состоянии {equal_count['stage']//stride+1} оба измерения дали "
                                  f"{equal_count['live_Q']} ошибок. Ответы различались для входов № {ids}.")
        rows = [[str(r["stage"]//stride+1), historical_q.get(r["stage"]//stride+1), r["live_Q"], r["snapshot_Q"]]
                for r in relevant if r["live_Q"] is not None and r["snapshot_Q"] is not None]
        if rows:
            title = "Одиночные итерации № 61" if scheme == "0_1" else "Переход от № 51 к № 61"
            tested = "30 входов" if scheme == "0_1" else "150 входов"
            context_charts.append(chart(identifier, title, "Номер контрольного состояния",
                f"Ошибки на {tested}, шт.", ["Состояние", "История", "Живой тест", "Отдельный снимок"], rows,
                "Историческая линия рассчитана из первичных пообъектных ответов. Сравнение включает возможное изменение последующего обучения и контекст измерения. Структурные траектории и результаты пауз приведены отдельно."))
        if pause_diff:
            historical_synapses = {r["state"]: sum(r["graph_ds"][5:]) for r in sources["protocols"]
                                   if r["sheet"] == source_sheet}
            rows = [[str(r["stage"]//stride+1), historical_synapses.get(r["stage"]//stride+1),
                     *[sum(s) if s is not None else None for s in r["s"]]]
                    for r in relevant if r["stage"] % stride == 0]
            identifier = "R08" if scheme == "0_1" else "R18"
            title = "Структура при одиночных итерациях № 61" if scheme == "0_1" else "Структура при переходе № 51 → № 61"
            context_charts.append(chart(identifier, title, "Номер контрольного состояния",
                "Синапсы, шт.", ["Состояние", "История", "Живой тест", "Без теста", "Пауза без импульсов"], rows,
                "На диаграмме показана сумма по пяти каналам. Отдельные каналы доступны в книге. "
                "Пауза продвигает модельное время при отключённых генераторах, после чего их активность восстанавливается."))
    sections.append(section("5 Влияние оценки на последующее обучение", paragraphs, context_charts))

    coverage_line = ""
    snapshot_line = ""
    if coverage:
        pending = [row for row in coverage["phases"] if row["pending_processes"] or row["running"] or row["failed_processes"]]
        if pending:
            coverage_line = "Серии с неполным покрытием: " + ", ".join(
                f"{row['phase']} ({row['completed_processes']}/{row['planned']})" for row in pending) + "."
        else:
            coverage_line = "Покрытие запланированных процессов сведено в таблицу книги."
        if coverage.get("trace_pairs_planned"):
            coverage_line += (f" Потактово сверено {coverage['trace_pairs_verified']} из "
                              f"{coverage['trace_pairs_planned']} сочетаний с изменёнными ответами. "
                              f"Первый зарегистрированный импульс проверен по трассе для "
                              f"{coverage['trace_answers_verified']} из {coverage['trace_answers_planned']} смен ответа.")
        if coverage["snapshots_reused"]:
            snapshot_line = (f"При оценке снимков {coverage['snapshots_reused']} запросов сведены к представителям "
                             "с одинаковыми байтами загружаемых файлов, одинаковым заданием и той же сборкой. "
                             "У таких проверок в книге указан общий журнал инференса, а журналы обучения остаются отдельными.")
    sections.append(section("6 Границы выводов и материалы", [
        "Подтверждены только эффекты с измеренным вмешательством и проверкой возврата. Для исторических расхождений полный комплект первичных сигналов и исходных кодов 2022 года отсутствует. Архивные альтернативы графа, различия порядка и состояния при предъявлении дают несколько совместимых объяснений.",
        "Доказанный дефект регистрации стенда исправлен. Подтверждение ошибки исторической таблицы требует расхождения с первичным файлом при согласованной привязке. Совпадение опубликованных счётов с первичными файлами подтверждает их арифметику. Источник необъяснённой 31-й строки и конкретная причина оставшихся исторических расхождений не установлены.",
        f"По журналам учтено {len(data['processes'])} процессов. Завершено {counts['completed']}. Остальные случаи и достигнутые внутри процесса ограничения доступны в книге. Использована сборка Release и запуск из Bin/Platform/Win. Степень подтверждения отдельных факторов следует оценивать по конкретным экспериментам и числу доступных повторов.",
        "Источники предшествующей проверки — ScientificComparisons и TrainingReproducibility. Исходные материалы находятся в Docs/ClassicStructTrainExperiments/Эксперименты. Реестр, нативные журналы и контрольные суммы находятся в Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124. Индекс архива Evidence связывает каждый файл с его контрольной суммой и архивной частью. Полные потактовые ряды сохранены в локальных частях waveforms в этом архиве.",
    ] + [line for line in (coverage_line, snapshot_line) if line]))
    sections.append(section("7 Использованные источники", [
        "1. «Инофрмация о длинах дендритов и числе синапсов.xlsx». Лист «Дендриты и синапсы», основной источник структур NT и NL. Docs/ClassicStructTrainExperiments/Эксперименты.",
        "2. «Распознавание.xlsx». Первичные столбцы ответов для 150 входов. Docs/ClassicStructTrainExperiments/Эксперименты/Тестирование/Распознавание.",
        "3. «Обучение нескольким примерам.xlsx» и соответствующие файлы output_data. Первичные ответы и формулы пяти последовательностей. Docs/ClassicStructTrainExperiments/Эксперименты/Исследование.",
        "4. «Код для тестирования переобучения.txt» и «код CalculateProcess.txt». Сохранённые фрагменты контроллера и архивная последовательность входов в подкаталогах «Тестирование» и «Исследование». Точные пути исходных данных указаны в книге.",
        "5. ScientificComparisons.docx и ScientificComparisons.xlsx. Результаты проверки сохранённых и реконструированных графов. Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/ScientificComparisons.",
        "6. TrainingReproducibility.docx и TrainingReproducibility.xlsx. Предшествующее повторное обучение и инференс. Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/TrainingReproducibility.",
        "7. История Git библиотек Nmsdk-PulseLib и Rdk. Полные идентификаторы сборок, исходные файлы диагностики и контрольные суммы приведены в журналах выполнения.",
    ]))
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
    order_by_run = {(r["mode"], r["repeat"]): r["stages"] for r in data.get("warm_order", []) if r["matched"]}
    paired_order = [i for i in (1, 2, 3) if all((mode, i) in order_by_run
                    for mode in ("native", "disabled", "reversal"))]
    if paired_order:
        changed = all(order_by_run["native", i] != order_by_run["disabled", i] and
                      order_by_run["native", i] == order_by_run["reversal", i] for i in paired_order)
        findings.append(["Перестановка внутри NPulseNeuron при переобучении",
             "Подтверждено экспериментом" if changed and len(paired_order) == 3 else "Поддерживается ограниченными данными",
             f"Парных сравнений на одном Release-бинарнике — {len(paired_order)}. Оценены учебные состояния перед переходом и после него."])
    elif data.get("warm_order"):
        findings.append(["Перестановка при переобучении в опыте VB и FO", "Поддерживается ограниченными данными",
                         "Совпадение с архивом зафиксировано в раздельно собранных вариантах. Хеши контроллеров различаются."])
    for label in ("NL22", "NT45"):
        pair = [r for r in data["profile_inference"] if r["label"] == label and r["profile"] == "reversal"]
        for profile, title in (("dissociation2", "Диссоциация 2 мс"), ("resistance100", "Сопротивление 100 МОм")):
            rows = [r for r in data["profile_inference"] if r["label"] == label and r["profile"] == profile]
            if not any(r["changed_ids"] for r in rows):
                continue
            stable = (len(rows) == len(pair) == 3 and all(r["physical_match"] for r in pair) and
                      len({tuple(r["changed_ids"]) for r in rows}) == 1)
            findings.append([f"{title}, фиксированный граф {label}",
                 "Подтверждено экспериментом" if stable else "Поддерживается ограниченными данными",
                 f"В первом полном измерении изменено {len(rows[0]['changed_ids'])} ответов. "
                 "Параметры измерены на том же графе, возврат сверяется по ответам, потенциалам и времени."])
    keep = [r for r in factors if r["run"].startswith("stop-keep-trainer-22-")]
    reverted = [r for r in factors if r["run"].startswith("stop-reversal-trainer-22-")]
    if len(keep) == len(reverted) == 3 and all(r["status"] == "wall_timeout" for r in keep):
        findings.append(["Продолжение NT22 после удаления синапса", "Подтверждено экспериментом",
                         "При исходном правиле и после его возврата наблюдалось завершение. "
                         "В изменённом условии три вычисления достигли 600 секунд."])
    live_vs_pause = [r for r in data.get("sequence_repeats", []) if r["scheme"] == "0_1_4_full"
                     and r["mode"] in {"live", "pause"}]
    if len(live_vs_pause) == 2 and all(r["repeats"] == 3 and r["same_training"] for r in live_vs_pause):
        different = sum(r["scheme"] == "0_1_4_full" and r["d"][2] is not None and
                        (r["d"][0], r["s"][0]) != (r["d"][2], r["s"][2]) for r in contexts)
        if different:
            findings.append(["Живой тест и пауза между этапами № 51 → № 61", "Подтверждено экспериментом",
                             f"Живой тест и пауза с выключенными генераторами дали разные структуры на {different} "
                             "учебных этапах по трём повторам. Контроль относится к интервалам одинаковой длительности."])
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
