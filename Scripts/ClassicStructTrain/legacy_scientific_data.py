"""Scientific comparison figures, preserving the source series, scales and numbering."""
from pathlib import Path
import json,re,sys,math
sys.path.insert(0,str(Path(__file__).resolve().parent))
from legacy_execute import ROOT,OUT,save
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def rates(m):
    tp,fp,fn,tn=(m[k] for k in ['TP','FP','FN','TN'])
    return {'TP':tp,'FP':fp,'FN':fn,'TN':tn,'TPR':tp/(tp+fn),'TNR':tn/(tn+fp),'FPR':fp/(fp+tn),'FNR':fn/(fn+tp),
            'BAcc':.5*(tp/(tp+fn)+tn/(tn+fp)),'precision':tp/(tp+fp) if tp+fp else None,'recall':tp/(tp+fn),'Q':fp+fn,
            'sum_rates':fp/(fp+tn)+fn/(fn+tp)}
def pc(v):return f'{100*v:.1f}%'.replace('.',',')
def main():
    a=load(OUT/'assessment.json');plan=load(OUT/'execution-plan-data.json');sources=load(OUT/'scientific-source-charts.json')
    points=load(OUT/'scientific-source-points.json');extra={r['case']:r for r in a.get('scientific_extra',[])}
    measured={r['case']:r for r in a['protocols'] if r['repeat']==1};measured.update(extra)
    assert load(OUT/'final-audit.json')['passed']
    figures=[];cases=[]
    asset=lambda prefix:next(x['preview'] for x in plan['figures'] if x['asset'].startswith(prefix))
    def add(case,sheet,title,headers,rows,source,description,analysis,image=None,fmt='0.0%',maximum=None,kind='line_sparse',secondary=False):
        item={'id':f'SC{len(figures)+1:02}','case':case,'sheet':sheet,'title':title,'headers':headers,'rows':rows,'source':source,
              'description':description,'analysis':analysis,'source_image':image,'format':fmt,'maximum':maximum,'kind':kind,'secondary':secondary}
        figures.append(item);return item
    epochs=[{'source_epoch':e['epoch']+1,'thesis_epoch':e['epoch'],'job':e['job'],'old':rates(e['archived']),'new':rates(e['measured'])} for e in a['epochs']]
    assert len(epochs)==14
    # Source chart values are checked against the matching archived confusion counts.
    for i,e in enumerate(epochs):
        assert math.isclose(e['old']['precision'],sources['E021']['cached_series'][0]['cache'][str(i)],abs_tol=1e-12)
        assert math.isclose(e['old']['recall'],sources['E021']['cached_series'][1]['cache'][str(i)],abs_tol=1e-12)
        assert e['old']['Q']==sources['E022']['cached_series'][0]['cache'][str(i)]
    stopping=[]
    for metric,direction in [('TPR','max'),('precision','max'),('BAcc','max'),('FPR','min'),('Q','min')]:
        row={'metric':metric,'direction':direction}
        for version in ['old','new']:
            values=[e[version][metric] for e in epochs];best=(min if direction=='min' else max)(values)
            row[version+'_value']=best;row[version+'_epochs']=[e['source_epoch'] for e in epochs if abs(e[version][metric]-best)<1e-12]
        stopping.append(row)
    cases.append({'id':'E01','title':'Переход 51→61 по схеме 0/(1+4), весь Iris','sources':['Эксперименты/Исследование/Обучение по двум примерам.docx','Эксперименты/Исследование/Средние нейроны.docx','Эксперименты/Исследование/Обучение нескольким примерам.xlsx — «Схема 0 на 1+4 для 150 примеров»','ВКР — рисунки 20 и 21'],
        'protocol':'Полное обучение 51; затем одна совместная итерация дендритов и синапсов на 61 и четыре итерации только синапсов. В текущей проверке повторена оценка 14 архивных состояний на входах 1–150, а не сам процесс обучения.',
        'status':'Переоценка архивных состояний выполнена; повторение траектории обучения не заявляется.'})
    paired=lambda fields:[[e['source_epoch'],*[e[v][f] for f in fields for v in ['old','new']]] for e in epochs]
    description='Те же три ряда, что в исходном рисунке: TP%=TP/50, TN%=TN/100 и их полусумма. Эпохи рабочего отчёта 1–14; новые точки относятся к тем же архивным структурам.'
    add('E01','51-61 TP TN','51→61: TP, TN и их полусумма',['Эпоха отчёта','Архив TP%','Повтор TP%','Архив TN%','Повтор TN%','Архив (TP+TN)/2','Повтор (TP+TN)/2'],paired(['TPR','TNR','BAcc']),
        '«Обучение по двум примерам.docx», первый рисунок; «Средние нейроны.docx», попытка 5.',description,
        'Зависимость лучшего состояния от метрики сохраняется. В архиве максимум TP достигается на эпохе 8, а максимум полусуммы — на 6. В новых оценках максимум TP приходится на эпохи 7–8, максимум полусуммы — на 7. Сравниваются точки оценки, не непрерывная кривая нового обучения.',asset('4b14ad75'),maximum=1)
    add('E01','51-61 FP FN','51→61: FP, FN и сумма долей',['Эпоха отчёта','Архив FP%','Повтор FP%','Архив FN%','Повтор FN%','Архив FP%+FN%','Повтор FP%+FN%'],paired(['FPR','FNR','sum_rates']),
        '«Обучение по двум примерам.docx», второй рисунок; «Средние нейроны.docx», попытка 5.',
        'Повторены исходные определения: FP%=FP/100, FN%=FN/50; серая кривая источника равна сумме этих долей. Она не заменена числом ошибок Q.',
        'На первой точке архивная сумма долей равна 51%, новая — 65%. Снижение пропусков сопровождается ростом ложных срабатываний в поздних состояниях. Разные знаменатели FP и FN сохранены, поэтому сумму долей нельзя читать как Q/150.',asset('2e49be6b'),maximum=.8)
    mean=next(b for b in a['baselines'] if str(b['label']).startswith('Среднее'))
    mean_old=rates(mean['archived']);mean_old['precision']=mean['archived']['precision_source'];mean_new=rates(mean['measured'])
    rows=[]
    for e in epochs:rows.append([e['thesis_epoch'],e['old']['precision'],e['new']['precision'],e['old']['recall'],e['new']['recall'],mean_old['precision'],mean_new['precision'],mean_old['recall'],mean_new['recall']])
    add('E01','51-61 и среднее','51→61 и средний нейрон: precision и recall',
        ['Эпоха ВКР','Архив P','Повтор P','Архив R','Повтор R','Архив P сред.','Повтор P сред.','Архив R сред.','Повтор R сред.'],rows,
        'ВКР, рисунок 20; таблицы 6–8 и приложение В. Числовая последовательность совпадает с листом «Схема 0 на 1+4 для 150 примеров», AG2:AH15.',
        'Восстановлен именно исходный состав рядов: precision/recall переходных состояний и оба горизонтальных ориентира среднего нейрона. Нумерация ВКР 0–13 соответствует эпохам 1–14 рабочего отчёта. Ориентиры среднего — одна оценка модели, а не 14 независимых опытов.',
        f'Полнота среднего нейрона сохраняется: {pc(mean_old["recall"])} и {pc(mean_new["recall"])}. Его precision меняется с опубликованных {pc(mean_old["precision"])} до {pc(mean_new["precision"])}. Среднее выигрывает по полноте, но не является лучшим по всем критериям. Опубликованный precision среднего округлён до трёх знаков.',asset('8a1de4ef'),maximum=1)
    add('E01','51-61 риск','51→61 и средний нейрон: эмпирический риск',
        ['Эпоха ВКР','Архив Q перехода','Повтор Q перехода','Архив Q среднего','Повтор Q среднего'],
        [[e['thesis_epoch'],e['old']['Q'],e['new']['Q'],mean_old['Q'],mean_new['Q']] for e in epochs],
        'ВКР, рисунок 21; «Обучение нескольким примерам.xlsx», AI2:AI15; среднее — таблицы 6–8 ВКР.',
        'Те же два типа рядов, что в рисунке 21: Q переходных состояний и горизонтальный уровень среднего нейрона. В этом источнике Q — FP+FN, количество ошибок, без деления на 150.',
        f'Минимум Q архива равен 8 на эпохе ВКР 5. Новый минимум 9 достигнут на эпохах ВКР 5 и 6. Для среднего Q меняется с {mean_old["Q"]} до {mean_new["Q"]}. Вывод о зависимости выбора состояния от критерия подтверждается; точные исторические реакции полностью не совпадают.',asset('e6b4dda9'),fmt='0',maximum=60)
    # These are the actual plotted TP counts, not recomputed replacement curves.
    for source_id,title in [('E019','Предварительная схема 0/(1(2)+4)'),('E020','Схема 0/(1+4): верное число синапсов')]:
        rows=[]
        for p in points[source_id]:
            if p['job'] not in measured:raise ValueError('Scientific protocol not completed: '+p['job'])
            result=measured[p['job']];assert result['input_ids']==p['input_ids']
            p['new_tp']=sum(v for ident,v in zip(result['input_ids'],result['answers']) if 51<=ident<=100)
            p['measured_directory']=result['directory'];rows.append([p['state'],p['old_plot'],p['new_tp']])
        old_peaks=[r[0] for r in rows if r[1]==max(x[1] for x in rows)];new_peaks=[r[0] for r in rows if r[2]==max(x[2] for x in rows)]
        source=sources[source_id];case='E02' if source_id=='E019' else 'E03'
        cases.append({'id':case,'title':title,'sources':[source['source']+' — '+source['sheet']],
            'protocol':f'Архивная последовательность из {len(rows)} структур; TP из десяти примеров своего класса. '+('Предъявлены отдельные 30 входов 41–60, 101–110.' if source_id=='E019' else 'Предъявлены отдельные 10 входов 51–60.'),
            'status':'Сопоставлены все точки исходного графика; новая оценка восстановленных состояний.'})
        add(case,source_id+' TP',title+': TP из 10',['Эпоха источника','Архив TP из 10','Повтор TP из 10'],rows,
            source['source']+'; лист «'+source['sheet']+'»; '+source['cached_series'][0]['formula'],
            f'Исторический ряд взят из кэша исходной диаграммы и сверен с её ячейками; сохранены {len(rows)} точек и единица «число из 10». Новые TP посчитаны по тем же десяти целевым входам внутри собственного протокола.',
            f'Максимум архивного ряда достигается на точках {old_peaks}, нового — на {new_peaks}. Совпали {sum(x==y for _,x,y in rows)} из {len(rows)} значений TP. '+('Седьмая точка имеет неполный архивный столбец ответов, но сохранённые структуру и итог TP=9; для неё выполнен отдельный 30-входовый прогон. Полное совпадение бинарных ответов этой точки не проверяется.' if source_id=='E019' else 'До первого максимума сравнивается отсутствие ухудшений распознавания, а не число заново выполненных итераций обучения.'),source['preview'],fmt='0',maximum=11)
    for scheme,case in [('Схема 3 на 4','E04'),('Схема 0 на 1','E05')]:
        comparisons=sorted([c for c in a['protocol_comparisons'] if c['reference']['sheet']==scheme],key=lambda c:c['reference']['state'])
        cases.append({'id':case,'title':scheme,'sources':['«Средние нейроны.docx», попытка '+('2' if case=='E04' else '3'),'«Обучение нескольким примерам.xlsx», лист «'+scheme+'»'],
            'protocol':f'{len(comparisons)} архивных состояний; отдельная оценка на 30 входах 41–60, 101–110.',
            'status':'Повторена оценка исторических состояний; компенсация структуры между учебными итерациями не проверялась.'})
        for metric,maximum in [('TP',10),('FP',20)]:
            rows=[[c['reference']['state'],c['archived_metrics'][metric],c['measured_metrics'][metric]] for c in comparisons]
            add(case,scheme.replace('Схема ','')+' '+metric,scheme+': '+metric,
                ['Состояние источника','Архив '+metric,'Повтор '+metric],rows,
                '«Средние нейроны.docx»; «Обучение нескольким примерам.xlsx», лист «'+scheme+'», сохранённые ответы по состояниям.',
                f'Сравнение исходных табличных результатов научного опыта: {metric} в каждом состоянии на одной и той же 30-входовой подвыборке. В источнике для этой схемы использованы таблицы, поэтому парный график построен из них.',
                f'Совпали {sum(x==y for _,x,y in rows)} из {len(rows)} значений {metric}; максимальная разность {max(abs(x-y) for _,x,y in rows)}. Изменение качества по состояниям не доказывает воспроизведение самого обучения.',fmt='0',maximum=maximum)
    bases=[{'label':'Среднее' if str(b['label']).startswith('Среднее') else str(b['label']),'job':b['job'],'old':rates(b['archived']),'new':rates(b['measured'])} for b in a['baselines']]
    cases.append({'id':'E06','title':'Примеры 51, 61 и арифметическое среднее','sources':['«Средние нейроны.docx», начальная таблица','ВКР, таблицы 6–8'],
        'protocol':'Три зафиксированные структуры NL; входы 1–150. Эти оценки повторно используются как ориентиры E01 без дополнительных одинаковых прогонов.',
        'status':'Выполнено прямое сравнение опубликованных показателей и новой оценки тех же структур.'})
    add('E06','Средний P R','51, 61 и средний: precision и recall',['Модель','Архив P','Повтор P','Архив R','Повтор R'],
        [[b['label'],b['old']['precision'],b['new']['precision'],b['old']['recall'],b['new']['recall']] for b in bases],
        '«Средние нейроны.docx», начальная таблица; ВКР, таблицы 6–8.',
        'Табличные результаты исходного научного сравнения преобразованы в парные столбцы. Средняя структура задана целыми архивными d/s, а не усреднением реакций моделей 51 и 61.',
        'Преимущество среднего по полноте сохраняется (98%). Его precision снижается из-за роста FP с 19 до 23. Это не универсальное превосходство над промежуточными состояниями E01.',kind='bar',maximum=1)
    add('E06','Средний Q','51, 61 и средний: число ошибок',['Модель','Архив Q','Повтор Q'],[[b['label'],b['old']['Q'],b['new']['Q']] for b in bases],
        'ВКР, таблицы 6–8; Q=FP+FN.',
        'Прямое сравнение количества ошибок трёх исторически обученных структур на одинаковых 150 входах.',
        'Q модели 51: 28→37; модели 61: 43→41; среднего: 20→24. Среднее остаётся лучшим из этих трёх по Q, однако лучший переходный архивный снимок E01 даёт меньше ошибок.',fmt='0',kind='bar',maximum=50)
    recognition=[]
    for c in a['recognition_comparisons']:
        ref=c['reference'];variant=re.search(r'\(\d+\)',str(ref['variant']))
        label=('NT' if ref['kind']=='trainer' else 'NL')+str(ref['id'])+(variant[0] if variant else '')
        recognition.append({'label':label,'old':c['archived_metrics'],'new':c['measured_metrics'],'job':c['job'],'range':ref['source_range'],'mismatch_ids':c['mismatch_ids']})
    cases.append({'id':'E07','title':'Распознавание после обучения одному примеру: NT и NL','sources':['Эксперименты/Тестирование/Распознавание/Распознавание.xlsx','Эксперименты/Тестирование/Распознавание/Исследование - Распознавание.docx'],
        'protocol':'22 исходных столбца результатов, каждый на 150 входах; соблюдены подписанные структурные варианты NT64 и NL129.',
        'status':'Прямое сравнение исторических реакций с текущей оценкой соответствующей структуры.'})
    for metric,title,fmt,maximum in [('balanced_accuracy','сбалансированная точность','0.0%',1),('Q','число ошибок','0',70)]:
        add('E07','Распознавание '+('BAcc' if metric=='balanced_accuracy' else 'Q'),'NT и NL: '+title,
            ['Структура источника','Архив','Повтор'],[[r['label'],r['old'][metric],r['new'][metric]] for r in recognition],
            '«Распознавание.xlsx», исходные столбцы NT/NL; точные диапазоны и соответствующие d/s приведены в реестре сравнений.',
            'Сопоставлены результаты исходного опыта после обучения одному примеру. Архивный вариант закреплён до запуска; совпадающие состояния и повторные ссылки не считаются дополнительными экспериментами.',
            'Физические структуры сохраняются; бинарные реакции каждого столбца расходятся на 2–11 входах из 150. График показывает научный показатель качества, а не техническое число несовпадающих битов.',fmt=fmt,maximum=maximum,kind='bar')
    # The presentation uses a distinct error-rate plot with three baseline levels.
    risk_source=next(c for c in plan['charts'] if c['id']=='C011')
    for i,e in enumerate(epochs):
        expected=[e['old']['Q'],bases[2]['old']['Q'],bases[0]['old']['Q'],bases[1]['old']['Q']]
        for series,value in zip(risk_source['series'],expected):
            assert math.isclose(float(series['values'][i]),100*value/150,abs_tol=1e-10)
    add('E01','Доля ошибок','51→61: доля ошибок и три базовых состояния',
        ['Эпоха ВКР','Архив переход','Повтор переход','Архив среднее','Повтор среднее','Архив 51','Повтор 51','Архив 61','Повтор 61'],
        [[e['thesis_epoch'],e['old']['Q']/150,e['new']['Q']/150,bases[2]['old']['Q']/150,bases[2]['new']['Q']/150,bases[0]['old']['Q']/150,bases[0]['new']['Q']/150,bases[1]['old']['Q']/150,bases[1]['new']['Q']/150] for e in epochs],
        '«черновик для таблиц.xlsx», «Обучение двум примерам», S2:V15; защита ВКР, график «Процент ошибок при распознавании».',
        'Повторены четыре исходных ряда: доля ошибок переходных состояний и постоянные уровни 51, 61 и среднего. В отличие от Q на рисунке 21 здесь показано 100×(FP+FN)/150 процентов. Уровни — повторное использование трёх оценок, без новых одинаковых прогонов.',
        'Лучший переходный снимок даёт 5,33% ошибок в архиве и 6,00% при повторной оценке. У среднего доля ошибок меняется с 13,33% до 16,00%. Сравнение сохраняет отдельные уровни двух исходных примеров и не смешивает долю ошибок с суммой FPR+FNR.',asset('d9d7f70b'),maximum=.4)
    # Non-equivalent waveform controls remain explicitly outside the direct results.
    for o in load(OUT/'overlays.json'):
        prefix='f57e7053' if o['id']=='O111' else '4ed6e8b5' if o['id']=='O129' else 'f6b043a3'
        add('A01','Контроль '+o['id'],o['title'],o['headers'],o['rows'],
            'ВКР, рисунки '+('15 и 16' if o['id']=='O111' else '17' if o['id']=='O129' else '18')+'.',
            'НЕ ПРЯМОЕ ПОВТОРЕНИЕ: архивная кривая относится к обучению, новые — к фиксированным структурам. Они вынесены в приложение. Окно 0–0,09 В; отрицательные фазы сброса сохранены в исходных рядах.',
            'Эти осциллограммы не используются для вывода, что историческая динамика обучения воспроизведена. Промежуточные состояния отсутствуют; возможен только контроль конечных состояний. Время сдвинуто одной константой, амплитуда не подбиралась.',asset(prefix),fmt='0.000',maximum=.09,kind='line_dense',secondary=True)
    saved=[r for r in a['saved'] if r['repeat']==1 and len(r['answers'])==150]
    for figure in figures:figure['minimum']=0
    for index,minimum,maximum in [(0,0,1.2),(2,.4,1),(3,5,55),(4,6,11),(5,3,11)]:
        figures[index].update(minimum=minimum,maximum=maximum)
    figures[2]['format']='0.000'
    figures[2]['description']+=' Метрики показаны долями 0–1, как на рисунке ВКР.'
    for f in figures:
        if f['secondary']:continue
        values=[v for row in f['rows'] for v in row[1:] if isinstance(v,(int,float))]
        assert min(values)>=f['minimum']-1e-12 and max(values)<=f['maximum']+1e-12,('Axis would hide a scientific result',f['id'])
    scientific={'cases':cases,'figures':figures,'epochs':epochs,'stopping':stopping,'baselines':bases,'recognition':recognition,'source_points':points,
        'saved_models':[{'id':r['job']['source_model'],'target':r['job']['target_id'],'dendrites':r['dendrites'],'synapses':r['synapses'],'metrics':r['metrics']} for r in saved],
        'direct_figures':sum(not f['secondary'] for f in figures),'secondary_figures':sum(f['secondary'] for f in figures),
        'scope':'Повторена оценка архивных обученных состояний при инференсе. Новая траектория обучения и число учебных итераций этим не подтверждаются.'}
    from legacy_scientific_context import enrich
    save(OUT/'scientific-comparison-data.json',enrich(scientific,plan,a))
    print(json.dumps({'cases':len(cases),'direct_figures':scientific['direct_figures'],'secondary_figures':scientific['secondary_figures'],'stopping':stopping},ensure_ascii=False))
if __name__=='__main__':main()
