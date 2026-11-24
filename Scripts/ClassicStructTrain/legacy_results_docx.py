"""Create a scientific DOCX containing the exported native XLSX charts and analysis."""
from pathlib import Path
import json,sys,collections,subprocess
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_paths import report_path
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'Reports/StructTrainClassic/_work/LegacyChecks-20261123'
OUT=ROOT/'Reports/StructTrainClassic'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pc(x):return '—' if x is None else f'{100*x:.1f}%'.replace('.',',')
def num(x,n=4):return f'{x:.{n}f}'.replace('.',',')
def vector(v):return '['+', '.join(map(str,v))+']'
def wave(directory):
    p=ROOT/directory/'waveforms.jsonl'
    return [json.loads(line) for line in p.read_text(encoding='utf8').splitlines() if line.strip()]

def main():
    a=load(WORK/'assessment.json');data=load(WORK/'execution-plan-data.json')
    recovery=load(WORK/'recovery-summary.json');resolutions=load(WORK/'partial-resolutions.json');figures=load(WORK/'figures.json')
    final_audit=load(WORK/'final-audit.json')
    assert final_audit['passed'],'Final execution/integrity audit must pass before publication'
    assert a['summary']['valid_saved_states']==9 and len(a['epochs'])==14 and len(a['baselines'])==3
    assert len(a['recognition_comparisons'])==22
    for figure in figures:assert (WORK/'excel-charts'/(figure['id']+'.png')).is_file(),figure['id']
    doc=Document();section=doc.sections[0]
    section.page_width=Inches(8.27);section.page_height=Inches(11.69)
    section.left_margin=section.right_margin=Inches(.74);section.top_margin=section.bottom_margin=Inches(.7)
    for name,size in [('Normal',11),('Title',21),('Subtitle',12),('Heading 1',15),('Heading 2',12),('Caption',10)]:
        style=doc.styles[name];style.font.name='Arial';style.font.size=Pt(size);style.font.color.rgb=RGBColor(0,0,0)
        style.paragraph_format.line_spacing=1.06;style.paragraph_format.space_after=Pt(6)
        style.element.get_or_add_rPr().rFonts.set(qn('w:eastAsia'),'Arial')
    for style in doc.styles:
        for border in list(style.element.findall('.//'+qn('w:pBdr'))):border.getparent().remove(border)
    doc.styles['Title'].font.bold=True
    footer=section.footer.paragraphs[0];footer.alignment=2
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    def p(text='',bold=False):
        para=doc.add_paragraph();para.add_run(text).bold=bold;return para
    def h(text,level=1):return doc.add_heading(text,level)
    def page(text):h(text).paragraph_format.page_break_before=True
    def table(headers,rows,widths):
        t=doc.add_table(rows=1,cols=len(headers));t.autofit=False
        for c,w in zip(t.columns,widths):c.width=Inches(w)
        for c,v in zip(t.rows[0].cells,headers):c.text=str(v)
        repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
        for row in rows:
            for c,v in zip(t.add_row().cells,row):c.text=str(v)
        for i,row in enumerate(t.rows):
            row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            for cell in row.cells:
                for para in cell.paragraphs:
                    para.paragraph_format.space_after=Pt(3);para.paragraph_format.space_before=Pt(3);para.paragraph_format.line_spacing=1.02
                    for run in para.runs:run.font.size=Pt(10);run.bold=i==0
        borders=OxmlElement('w:tblBorders')
        for side in ['top','bottom','insideH']:
            node=OxmlElement('w:'+side);node.set(qn('w:val'),'single');node.set(qn('w:sz'),'4');node.set(qn('w:color'),'B8C0C8');borders.append(node)
        t._tbl.tblPr.append(borders);p();return t
    doc.add_paragraph('Проверка архивных обученных моделей',style='Title')
    doc.add_paragraph('Структурное обучение nmsdk • autoPreset • Release',style='Subtitle')
    p('23 ноября 2026 года')
    full_saved=[r for r in a['saved'] if r['repeat']==1 and len(r['answers'])==150]
    unique_primary=len({r['case'] for r in a['saved']+a['recovered'] if len(r['answers'])==150})
    p(f'Проверены 9 согласованных сохранённых состояний и {recovery["unique_physical_states"]} восстановленных физических состояний. '
      f'С учётом шести полных совпадений физических описаний это {unique_primary} различных состояний для основного инференса. '
      'Основной результат — сохранность классов компонентов, длин дендритов, числа синапсов, связей и известных физических параметров после загрузки и расчёта.')
    p('Сравнение бинарных ответов и графиков выполнено отдельно от структурной проверки. Результаты относятся к явно заданным протоколам изолированного инференса; в отчёте указаны изменения активности, способ подачи входов и происхождение восстановленных параметров.')
    differences=[len(c['mismatch_ids']) for c in a['recognition_comparisons']]
    p(f'С архивом полностью совпало {sum(v==0 for v in differences)} из {len(differences)} столбцов распознавания; '
      f'различаются {min(differences)}–{max(differences)} решений на 150 входах. Это различия бинарных реакций на конкретные стимулы. '
      'При этом известные физические структуры сохраняются точно. Совпадение структуры подтверждено независимо от совпадения ответов.')
    table(['Объём проверки','Результат'],[
        ('Сохранённые состояния','9; два полных прохода по 150 входам для каждого'),
        ('Исходная активность','8 выключенных поддеревьев проверены отдельными контрольными прогонами'),
        ('Восстановление',f'{recovery["unique_physical_states"]} уникальных физических состояний; 6 эквивалентных прогонов использованы повторно'),
        ('Неполные строки',f'{len(resolutions)} дополнены однозначными данными; {recovery["unresolved_rows"]} остаются неполными'),
        ('Исторические ответы','22 столбца распознавания и 59 столбцов исследовательских схем'),
        ('Сопровождение',f'XLSX с числовыми рядами и {len(figures)} редактируемыми графиками; все эти графики включены ниже')],[2.0,4.7])
    p('Внешние статьи и книги использованы как теоретические источники. Основные экспериментальные данные взяты из каталога Docs/ClassicStructTrainExperiments/Эксперименты; ВКР и презентации дополняют их.')

    page('Условия и метод проверки')
    table(['Параметр','Значение'],[
        ('Ветка','autoPreset в основном репозитории и Bin'),('Исполнение','Release; бинарник и рабочий каталог Bin/Platform/Win'),
        ('Дискретизация','2000 Гц; шаг 0,0005 с'),('Входной период','1,5 Гц; 1334 расчётных шага на предъявление'),
        ('Основная последовательность','150 Iris-входов в архивном порядке, с полной доступной точностью'),
        ('Подвыборки','Собственные проходы на 30 и 10 входах в исходном порядке'),
        ('Сброс','Основной режим непрерывный; независимый Reset проверен отдельными парными протоколами'),
        ('Порог распознавания','FixedLTZThreshold=0,0115; задан явно до загрузки'),
        ('Обучение','IsNeedToTrain=false; ExperimentMode выключен'),
        ('Наблюдение','Ответ LTZone, пять потенциалов сом и их сумма, пики, время первого спайка, физический граф')],[1.75,4.95])
    method_start=len(doc.paragraphs)
    p('Для сохранённых нейронов запрещена пересборка исходного графа: StructureBuildMode установлен в 0 в подготовленных копиях. Внешний контроллер связывает неперсистентные указатели на существующие генераторы и нейрон, создаёт наблюдательные буферы и восстанавливает нативный порядок расчёта сегментов. Обучающие методы библиотеки не изменялись.')
    p('Восемь сохранённых поддеревьев целиком выключены в XML. Сначала проверена исходная активность, затем включена подготовленная изолированная копия. Для транзитных Source1–Source5 добавлены внешние нативные периодические генераторы. Связи конкуренции с другими нейронами родительского классификатора в изолированный протокол не входят. M018 сохранён активным и использует собственные источники.')
    p('Полный цикл Init/UnInit/Init выполнен после создания всего статического поддерева. Перед измерениями проверены наличие и инициализация входных сегментов, всех ожидаемых синапсов и генераторных связей. Дополнительный обход проверяет IsInit каждого активного объекта; результат этого обхода включён в итоговый аудит.')
    p('При подготовке NL выявлено, что сохранённое значение LTZThreshold=100 может пережить загрузку при уже опущенном флаге обучения. В итоговых реконструкциях восстановлен документированный FixedLTZThreshold=0,0115. Значение 100 применяется только в отдельно отмеченном контроле обратной связи LTZone, при выключенном обучении.')
    p('Предварительные отладочные пробы с неполной инициализацией окружения, отсутствующими внешними транзитными входами или учебным порогом исключены из итоговой выборки. Основные результаты взяты из завершённых серий saved-b, recovered-b и protocols-a. Каждый процесс сохраняет команду, рабочий каталог, SHA256 бинарника и манифеста, код выхода и длительность.')
    p('Дополнительное сравнение полного родительского проекта выполняется на 12 контрольных входах: 1, 22, 45, 51, 60, 64, 84, 90, 110, 129, 132, 134. Во всех трёх сравниваемых режимах порядок одинаков. Незавершённые полные контекстные пробы сохранены отдельно; их частичные результаты в выводах не используются. Основные изолированные проходы девяти сохранённых состояний и реконструкций содержат по 150 входов.')
    p('В дополнительных сериях обнаружена конкуренция штатного сохранения за общий временный файл save.tmp. Внешний контроллер теперь блокирует только участок сериализации между процессами. Все снимки проверены на наличие и читаемость XML; неудачные попытки сохранены отдельно и повторены. Код Rdk и PulseLib не изменялся.')
    for para in doc.paragraphs[method_start:]:
        para.paragraph_format.line_spacing=1.0;para.paragraph_format.space_after=Pt(4)
        for run in para.runs:run.font.size=Pt(10.5)

    page('Девять исходных сохранённых состояний')
    table(['Модель','ID обучения','Дендриты d','Синапсы s','Граф'],[(r['job']['source_model'],r['job']['target_id'],vector(r['dendrites']),vector(r['synapses']),'Сохранён') for r in full_saved],[.7,.85,2.0,2.0,1.15])
    table(['Модель','Precision','Recall','BAcc','Q','Различий с архивом'],[(r['case'].split('-')[0],pc(r['metrics']['precision']),pc(r['metrics']['recall']),pc(r['metrics']['balanced_accuracy']),r['metrics']['Q'],
        str(len(r['references'][0]['mismatch_ids'])) if r['references'] else 'Нет столбца') for r in a['saved_comparisons']],[.7,1.05,1.05,1.05,.45,2.4])
    p('TrainingPattern определяет обучающий пример; InputPattern может быть текущим тестовым входом. Поэтому, например, M001 относится к примеру 45 при сохранённом текущем входе 84. Примеры 110 и 132 не подменяются примерами 111 и 134 из таблицы распознавания.')
    if a['own_checks']:
        h('Распознавание обучающего примера',2).paragraph_format.page_break_before=True
        table(['Модель','Свой ID','Нормированный вход','Буквальный TrainingPattern'],[(c['base'].split('-')[0],c['target'],c['dataset_fresh_answer'],c['literal_answer']) for c in a['own_checks']],[1.0,1.0,2.3,2.4])
        p('Оба собственных входа предъявлены из свежего состояния. Такое сравнение отделяет полную точность нормированного датасета от сохранённых чисел TrainingPattern. Контекст основного 150-входового прохода учитывается отдельно.')
        p('Все девять состояний распознают свой обучающий пример в обоих свежих контролях. У M008 и M018 сбалансированная точность на всём классе равна 49,5%: TP=2, FP=5, FN=48, TN=95. Низкий recall здесь означает пропуск 48 из 50 примеров целевого класса. Сохранённая способность распознать собственный пример и сохранность графа не подтверждают обобщение на весь класс Iris.')
    p('Одинаковые d и s у M008 и M018 не дают основания объединять их автоматически: сравнение учитывает все компоненты, параметры, активность и связи. Для шести других сохранённых состояний построенные реконструкции совпали с полным физическим описанием и протоколом; эти совпадения учтены как ссылки на единый основной прогон.')

    page('Восстановление недостающих состояний')
    p('Источник «Инофрмация о длинах дендритов и числе синапсов.xlsx» включён в реестр. В нём есть полные длины для 31 случая NT и 110 случаев NL; полный числовой вектор синапсов имеется для одного NL. Четыре строки NT со скобками сохранены как два согласованных варианта целого вектора. Отдельные числа из этих вариантов произвольно не комбинировались.')
    p(f'Для восстановления использованы также структурные заголовки output_data, протоколы и опубликованные таблицы. К 497 записям плана добавлены 270 ссылок на строки трёх серий переобучения: все они сопоставлены с уже восстановленными состояниями. Всего зарегистрировано {recovery["source_rows"]} записей. Неполная запись ответов не препятствует восстановлению корректного десятикомпонентного структурного заголовка. Неоднозначный предварительный алгоритм обучения также не препятствует проверке явно сохранённого конечного состояния.')
    rows={r['id']:r for r in data['restoration_rows']}
    table(['Строка','Алгоритм / ID','Восстановленные синапсы','Однозначные доноры'],[(r['row'],rows[r['row']]['kind']+' / '+str(rows[r['row']].get('target')),vector(r['synapses']),', '.join(r['donors'])) for r in resolutions],[.75,1.4,2.15,2.4])
    p('Геометрия восстановлена по пяти длинам дендритов и пяти числам синапсов. Классы сегментов, каналов и синапсов и их физические параметры заимствованы из архивных профилей M001 для NT и M019 для NL. Восстановлены однонаправленные дендритные цепочки, канальные и генераторные связи. Профили и каждое дополнение имеют паспорт происхождения.')
    p('Такие состояния являются реконструкциями для инференса. Их TrainingPattern служит контрольным стимулом и не доказывает существование единственного обучающего примера. Неизвестные числа синапсов в оставшихся 131 строке сохранены как отсутствующие данные. Полный реестр, включая все повторные ссылки на источники, находится в XLSX.')

    page('Числовые критерии и дополнительные контроли')
    p('Для d и s требуется точное поканальное совпадение известных целых значений. Дополнительно сопоставлены классы компонентов, активность, сопротивления, ёмкости, временные постоянные, пороги и соединения. Одного совпадения счётчиков недостаточно для признания физического состояния тем же самым.')
    p('TP, FP, FN и TN вычислены по установленному целевому классу. Precision=TP/(TP+FP), recall=TP/(TP+FN), accuracy=(TP+TN)/N, balanced accuracy=(TPR+TNR)/2. В историческом графике Q сохранено количество ошибок FP+FN; нормированная доля Q/N показана отдельно. Начальные 28 ошибок на 150 входах соответствуют 18,6667%.')
    p('Канонические структуры для 22 столбцов распознавания закреплены манифестом, подготовленным до этих запусков. Для явно подписанных вариантов соблюдён индекс варианта; для столбцов без индекса использована первая документированная структура соответствующего ID. Остальные структурные варианты сохранены и проверены, но не подбирались по лучшему совпадению ответов.')
    p('Четыре красные архивные осциллограммы оцифрованы по пикселям. Для каждой колонки изображения сохранены медиана и диапазон красного штриха. Временная шкала восстановлена линейно по видимым меткам; округление подписей до 0,1 с даёт ±0,05 с на метку. Учтены также толщина линии и точность подписей потенциала. Для наложения применён один постоянный сдвиг начала времени по первому максимуму; растяжение времени и подбор масштаба амплитуд не применяются. Интерполяция на равномерную сетку 0,0005 с служит только отображению и не повышает точность архива.')
    if a.get('context_comparisons'):
        labels={'autonomous_vs_parent_driven_150':'Собственные / родительские источники (150)',
                'autonomous_vs_parent_driven_12':'Собственные / родительские источники (12)',
                'parent_driven_vs_full_context_12':'Без соседей / полный проект (12)'}
        table(['Парное сравнение M018','Различий ответов','Максимальная разность пика, В'],[(labels[c['comparison']],c['answer_differences'],num(c['max_peak_difference'],7)) for c in a['context_comparisons']],[3.0,1.0,2.7])
        p('Дополнительный полный проект сохраняет исходную активность всех классификаторов и боковые связи. Обучение всех 18 тренеров выключено; девять промежуточных состояний соседей не считаются завершённо обученными. Штатная инициализация активного классификатора передаёт его частоту 1,5 Гц пяти источникам каждого из десяти тренеров; эти 50 значений явно учтены в подготовленной копии. Изолированный транзитный контроль M018 использует параметры родительских генераторов и отделяет способ подачи входов от взаимодействия с соседями.')
        p('Замена собственных источников M018 на родительские дала полностью одинаковые ответы и пики на 150 входах. Включение полного родительского контекста на 12 контрольных входах не изменило бинарных ответов, но изменило пики суммы максимум на 0,0046364 В. Влияние соседей на аналоговый сигнал обнаружено; изменения решений на этой контрольной последовательности не обнаружены.')
    page('Повторяемость, точность входов и сброс')
    table(['Контроль','Наблюдение'],[
      ('Повторы',f'{len(a["repeat_checks"])} пар полных прогонов, включая контекстные; расхождений ответов, пиков и структуры: {len(a["summary"]["repeat_differences"])}'),
      ('Повторная загрузка',f'{len(a["reload_checks"])} контрольных проверок сохранённых состояний; одинаковый первый ответ и пик: {sum(c["same_answer"] and c["same_peak"] for c in a["reload_checks"])}'),
      ('Третий повтор',f'{len(a["third_checks"])} представителя; совпадений ответов и пиков: {sum(c["same_answers"] and c["same_peaks"] for c in a["third_checks"])}'),
      ('Сборка реконструкции','Одинаковые ответы, пики и полный физический граф для исходной NT45 и независимо собранной копии'),
      ('Полный обход инициализации',f'{final_audit.get("initialization_states",0)} физических состояний; неинициализированных активных объектов: {final_audit.get("uninitialized_objects",0)}')],[1.85,4.85])
    if a['precision_checks']:
        p('Отдельная проверка четырёх знаков после запятой опирается на формат архивного input_data. Это иной протокол точности входов; он не заменяет основной проход.')
        table(['Модель','Ответов изменилось','BAcc полная точность','BAcc 4 знака'],[(c['base'],c['answer_differences'],pc(c['full_metrics']['balanced_accuracy']),pc(c['rounded_metrics']['balanced_accuracy'])) for c in a['precision_checks']],[2.3,1.1,1.65,1.65])
    if a['reset_checks']:
        p('Независимый Reset сопоставлен с непрерывным режимом на одной и той же короткой последовательности из шести входов. История полного прохода по 150 примерам для этого сравнения не использовалась.')
        table(['Состояние','Изменённых ответов','Макс. разность пика, В'],[(c['base'],c['answer_differences'],num(c['max_peak_difference'],7)) for c in a['reset_checks']],[2.9,1.7,2.1])

    wave_cache={}
    def signal_stats(case,input_id):
        record=a['first_by_job'].get(case)
        if not record:return None
        directory=record['directory']
        if directory not in wave_cache:wave_cache[directory]=wave(directory)
        points=[x for x in wave_cache[directory] if x['input_id']==input_id]
        if not points:return None
        peak=max(points,key=lambda r:r['sum_soma']);channel_peaks=[max(points,key=lambda r:r['soma'][i]) for i in range(5)]
        return peak,len(points),channel_peaks,min(x['sum_soma'] for x in points)
    def analysis(f):
        title=f['title'];sheet=f['sheet']
        if title=='Сохранённые модели: структура до и после инференса':
            return 'Для всех девяти состояний совпали пять длин и пять терминальных чисел синапсов до загрузки и после инференса. Совпадение сумм на рисунке дополнено покомпонентной проверкой классов, параметров и связей. Ни одна структура не была пересобрана обучающим алгоритмом.'
        if sheet=='Сохранённые модели':
            values=[r['metrics']['balanced_accuracy'] for r in a['saved_comparisons']];diffs=[len(r['references'][0]['mismatch_ids']) for r in a['saved_comparisons'] if r['references']]
            return f'Новая сбалансированная точность лежит в диапазоне {pc(min(values))}–{pc(max(values))}. Для шести состояний с соответствующим историческим столбцом различаются {min(diffs)}–{max(diffs)} ответов из 150. При этом физические структуры сохранены; три состояния без исторического столбца оценены как новые измерения.'
        if sheet=='Распознавание':
            diffs=[len(c['mismatch_ids']) for c in a['recognition_comparisons']]
            return f'Сопоставлены 22 структурных варианта. Полностью совпало {sum(x==0 for x in diffs)} столбцов; число различий составляет {min(diffs)}–{max(diffs)} из 150. Варианты NT64 и NL129 сопоставлены по соответствующим d/s, поэтому разные архивные структуры не смешиваются.'
        if sheet=='Эпохи':
            best=min(a['epochs'],key=lambda e:e['measured']['Q']);old=min(a['epochs'],key=lambda e:e['archived']['Q_source'])
            first,last=a['epochs'][0]['measured'],a['epochs'][-1]['measured']
            if title=='TPR и TNR по эпохам':
                return f'В новых измерениях TPR меняется от {pc(first["recall"])} в начале до {pc(last["recall"])} в конце; TNR — от {pc(first["TN"]/(first["TN"]+first["FP"]))} до {pc(last["TN"]/(last["TN"]+last["FP"]))}. Минимум Q достигается раньше, на эпохе {best["epoch"]}. Поздние состояния повышают полноту относительно начального, одновременно теряя специфичность. Здесь сопоставлены готовые структуры, а не выполнено новое обучение.'
            if title=='FPR и FNR по эпохам':
                return f'Для новых состояний FPR меняется от {pc(first["FP"]/(first["FP"]+first["TN"]))} до {pc(last["FP"]/(last["FP"]+last["TN"]))}, а FNR — от {pc(1-first["recall"])} до {pc(1-last["recall"])}. Уменьшение пропусков сопровождается ростом ложных срабатываний; один показатель числа ошибок не раскрывает этот обмен. Пары кривых сравнивают одинаковые знаменатели по классам.'
            return f'Для новых измерений минимум ошибок равен {best["measured"]["Q"]} на эпохе {best["epoch"]}; в архивных состояниях минимум {old["archived"]["Q_source"]} на эпохе {old["epoch"]}. Состояния восстановлены по архивным d/s. Сравниваются их реакции при инференсе, а последовательность нового обучения не измеряется.'
        if sheet=='Подвыборки':
            scheme=title.split(':')[0];cs=[c for c in a['protocol_comparisons'] if c['reference']['sheet']==scheme]
            return f'Для схемы сопоставлено {len(cs)} исторических столбцов; {sum(not c["mismatch_ids"] for c in cs)} совпали полностью. Каждый проход использует собственную исходную подвыборку. Показатели на 10, 30 и 150 входах имеют разные знаменатели и анализируются отдельно.'
        if sheet=='Базовые модели':
            values=[('среднее' if str(b['label']).startswith('Среднее') else str(b['label']),b['measured']['Q']) for b in a['baselines']]
            return 'Число ошибок на полном Iris: '+ '; '.join(f'{label} — {q}' for label,q in values)+'. Средняя структура задана документированными целыми векторами; она не заменена простым усреднением реакций моделей 51 и 61.'
        if sheet=='Сигналы' and 'порог LTZone' in title:
            return 'Все кривые получены на конечных фиксированных структурах, при выключенном обучении. Контроль с учебным порогом 100 отделяет влияние срабатывания LTZone от геометрии. Архивные кривые ниже показывают обучение на итерациях 6–10; их увеличение по итерациям нельзя приписывать этой фиксированной модели.'
        if sheet=='Сигналы':
            if 'NT45' in title:stats=signal_stats('M001-activated',45)
            elif 'NT132' in title:stats=signal_stats('M018-preserved',132)
            else:
                base=next(b for b in a['baselines'] if str(b['label'])=='51');stats=signal_stats(base['job'],51)
            if stats:
                peak,count,channels,minimum=stats;spread=max(c['time'] for c in channels[:4])-min(c['time'] for c in channels[:4])
                return f'Сохранено {count} отсчётов. Максимум суммы равен {num(peak["sum_soma"],6)} В при t={num(peak["time"],4)} с. Разброс времён максимумов сом 1–4 составляет {num(1000*spread,2)} мс; максимум сомы 5 — {num(channels[4]["soma"][4],6)} В. Измеренный минимум суммы {num(minimum,5)} В лежит вне показанного положительного окна; это сохранённая в таблицах отрицательная фаза сброса при действующей LTZone.'
        if sheet=='Сопоставление осциллограмм':
            overlay=next(o for o in load(WORK/'overlays.json') if o['title']==title)
            if overlay['id']=='O111':
                parts=[]
                for old in overlay['historical_statistics']:
                    kind='NL' if old['id'].endswith('NL') else 'NT'
                    reference=next(s for s in overlay['native_statistics'] if s['threshold_control'] and s['label'].startswith(kind))
                    parts.append(f'{kind}111: архивные первый и последний максимумы {num(old["first_peak"],5)} и {num(old["last_peak"],5)} В; фиксированное состояние с порогом 100 — {num(reference["first_peak"],5)} и {num(reference["last_peak"],5)} В.')
                result=' '.join(parts)
            else:
                old=overlay['historical_statistics'][0]
                result=f'Архив: первый и последний максимумы {num(old["first_peak"],5)} и {num(old["last_peak"],5)} В. '
                result+=' '.join(f'{s["label"]}: {num(s["first_peak"],5)} и {num(s["last_peak"],5)} В.' for s in overlay['native_statistics'])
            return result+f' Граница неопределённости времени архива до {num(overlay["time_uncertainty_max"],3)} с. Сравниваются обучение и фиксированные состояния; промежуточные структуры обучения неизвестны.'
        if sheet=='Переходы':return 'Вход меняется после первого периода, затем новый пример предъявляется ещё пять раз. Структура во всём проходе остаётся фиксированной. Начальная структура взята для 22, конечная — из первой серии протоколов соответствующего перехода. Историческая динамика изменения структуры этим контролем не подменяется.'
        if sheet=='Проекции Iris':return 'Все точки взяты из архивного листа «Датасет» с полной доступной точностью. Выделены десять эталонов и примеры 51 и 61. Совпадение проекций проверяет подготовку входов и выбор примеров; поведение нейрона по этим изображениям не оценивается.'
        if sheet=='Контекст проекта':return 'Во всех трёх режимах на 12 входах получены TP=1, FP=1, FN=3, TN=7 и BAcc=56,25%. Собственные и родительские источники дают одинаковые пики. Полный контекст меняет пики максимум на 4,6364 мВ, сохраняя бинарные ответы на этой последовательности. Это реакции M018; показатели на 12 входах не смешиваются с основными показателями на 150.'
        return f['analysis'] or 'Числовые данные и происхождение рядов сохранены в сопровождающем XLSX.'
    page('Графики XLSX: описание и анализ')
    p('Все последующие графики экспортированы из нативных диаграмм итогового XLSX. Изображения в DOCX и редактируемые диаграммы книги используют одни и те же числовые ряды. Дополнительные архивные осциллограммы явно подписаны как источники другого режима.')
    normal_count=1;pending_break=False
    for index,f in enumerate(figures,1):
        special=f['sheet']=='Сопоставление осциллограмм'
        new_page=index>1 and (special or normal_count>=2 or pending_break)
        if new_page:normal_count=0;pending_break=False
        para=doc.add_paragraph();para.paragraph_format.space_after=Pt(2)
        para.paragraph_format.page_break_before=new_page;para.paragraph_format.keep_with_next=True
        para.add_run().add_picture(str(WORK/'excel-charts'/(f['id']+'.png')),width=Inches(6.7))
        caption=doc.add_paragraph(f'Рисунок {index}. {f["title"]}',style='Caption');caption.runs[0].bold=True
        caption.paragraph_format.keep_with_next=True
        description=p(f['description']);description.paragraph_format.keep_with_next=True
        interpretation=p(analysis(f))
        for body in [description,interpretation]:
            body.paragraph_format.line_spacing=1.0;body.paragraph_format.space_after=Pt(3)
            for run in body.runs:run.font.size=Pt(10)
        if special:
            prefixes=['f57e7053','9266ab41'] if '111' in f['title'] else ['4ed6e8b5'] if '129' in f['title'] else ['f6b043a3']
            if len(prefixes)==2:
                for prefix in prefixes:
                    asset=next(x for x in data['figures'] if x['asset'].startswith(prefix));p().add_run().add_picture(str(report_path(asset['preview'])),width=Inches(6.3))
            else:
                asset=next(x for x in data['figures'] if x['asset'].startswith(prefixes[0]));p().add_run().add_picture(str(report_path(asset['preview'])),width=Inches(6.7))
            p('Архивный источник: ВКР, рисунки '+('15 и 16 — обучение на итерациях 6–10.' if len(prefixes)==2 else '17 — обучение при переходе 22→129.' if '129' in f['title'] else '18 — обучение при переходе 22→37.'))
            pending_break=True;normal_count=0
        else:normal_count+=1

    page('Покрытие плана и пределы выводов')
    table(['Семейства','Что установлено'],[
      ('G01','Шесть проекций входных данных построены из архивных координат.'),
      ('G02','Потенциалы отдельных сом, их сумма и LTZone сняты при инференсе сохранённых и восстановленных состояний.'),
      ('G03–G05','Построены фиксированные диагностические реакции и контроль учебного порога. Промежуточных структур итераций 6–10 нет; непрерывное обучение по этим рисункам не объявлено воспроизведённым.'),
      ('G06–G08','Архивные зависимости числа итераций сохранены в плане и источниках. Инференс готовой модели не даёт новых измерений стоимости обучения.'),
      ('G09–G14','Сопоставлены состояния эпох и исходные подвыборки. Q как количество ошибок и нормированная доля показаны отдельно.'),
      ('G15–G16','Ответы на входы и структурные параметры сопоставлены с документированными вариантами; 131 неполная запись отмечена в реестре.'),
      ('G17–G18','Проверены загрузка, порядок расчёта, готовность активных объектов, стабильность графа и сохранение с повторной загрузкой.')],[1.0,5.7])
    p('Сохранность графа подтверждает совместимость подготовленного статического состояния с проверенной веткой и протоколом. Она не устанавливает тождество всех исторических реакций. При расхождениях доступны конкретные входы, пики, временные ряды, физические параметры и парные контроли сброса и точности входов.')
    p('Для восстановленных состояний остаётся неопределённость тех параметров, которых нет в конкретной структурной записи и которые заимствованы из согласованного архивного профиля. Для исходных сохранённых состояний основной исторический инференс выполнен в изолированном контексте; полный замороженный родительский проект и отдельный транзитный контроль исследованы дополнительно.')
    p('Использование этих конфигураций стендом требует восстановления неперсистентных ссылок и нативного порядка расчёта. Подготовленные и подтверждённые состояния находятся в Bin/Configs/StructTrainClassic/LegacyInference; скрипты воспроизведения — в Scripts/ClassicStructTrain. Исходные документы и дословные копии архивных конфигураций сохранены без изменений.')
    p(f'Итоговый аудит: {final_audit.get("archive_files_checked",0)} архивных файлов и {final_audit.get("verbatim_configs_checked",0)} дословных конфигурационных файлов проверены по SHA256. Все основные процессы выполнены из Bin/Platform/Win в Release. Полные журналы, паспорта состояний и манифесты сохранены как внутренние материалы исследования.')
    doc.core_properties.title='Проверка архивных обученных моделей nmsdk';doc.core_properties.author='Codex'
    OUT.mkdir(parents=True,exist_ok=True);doc.save(OUT/'LegacyModelChecks.docx');print(OUT/'LegacyModelChecks.docx')
if __name__=='__main__':main()
