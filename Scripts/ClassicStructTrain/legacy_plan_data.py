"""Prepare provenance-preserving inputs for the DOCX and XLSX checking plan."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys
from docx import Document
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0,str(Path(__file__).resolve().parent))
from report_paths import report_path
from prepare import workbook
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'Reports/StructTrainClassic/_work/LegacyInferencePlan-20261123/work'


def load(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def save(name,data): (WORK/name).write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')


FAMILIES=[
 ('G01','Проекции входов Iris','ВКР рисунки 14 и 19; Средние нейроны; черновик для таблиц','Шесть плоскостей d1 d2 d3 d4, с','Три класса и выделенные 10 эталонов либо 51 61 и средний вход','Повторить исходные координаты и разбиение; эти графики проверяют данные, а не работу нейрона','Данные имеются'),
 ('G02','Потенциалы отдельных сом и их сумма','ВКР рисунок 7; защита слайд 7; графики потенциалов.png; слайд 20','Время относительно входного события, с; потенциал, В','Пять Soma.SumPotential, SomaNeuronAmplitude(0,0), входные спайки и LTZone','Проверить сохранённые обученные модели на известном входе; сравнить пики, задержки и форму. Для иллюстративных схем без параметров выполнить качественную сверку','Новые сигналы предстоит снять'),
 ('G03','Сумма потенциалов на итерациях 6 по 10 для примера 111','ВКР рисунки 15 и 16; обучение из исходного состояния.png; защита слайды 8 и 14','Историческое окно около 9.1 до 12.4 с; потенциал, В','NNeuronLearner и NNeuronTrainer отдельными панелями','Исторические кривые относятся к обучению. Финальная замороженная модель даёт отдельный график установившегося инференса. Прямое повторение требует снимков структуры каждой итерации или отдельного воспроизведения обучения','Условно по наличию состояний итераций'),
 ('G04','Переход между классами от примера 22 к 129','ВКР рисунок 17; обучение из произвольного состояния.png','Историческое окно около 23.4 до 27.4 с; потенциал, В','Сумма сом до смены входа и после неё','Для инференса отдельно проверить смену входа на фиксированной структуре и реакции двух архивных конечных состояний. Не приравнивать это к исторической динамике переобучения','Промежуточные состояния обучения не все известны'),
 ('G05','Переход внутри класса от примера 22 к 37','ВКР рисунок 18','Историческое окно около 38.2 до 41.7 с; потенциал, В','Тот же набор сигналов с меткой смены входа','Использовать протокол как G04; совмещение только по одному постоянному временному сдвигу с сохранением исходной шкалы','Промежуточные состояния обучения не все известны'),
 ('G06','Число итераций обучения дендритов и всей модели','Итерации.docx график 1; Итерации.xlsx диаграммы 3 и 4','ID десяти примеров; число итераций','NL и NT, дендриты и полное обучение','Сохранить исторические столбцы. Статический инференс не восстанавливает число затраченных на обучение итераций. Новое обучение и проверку его скорости вынести в отдельный этап','В основном плане только исторический эталон'),
 ('G07','Обучение с нуля и среднее переобучение','Итерации.docx график 2; Итерации.xlsx диаграмма 2','ID десяти примеров; число итераций','NT с нуля, NL с нуля, среднее NL по девяти переходам','Не использовать время инференса вместо времени обучения. Сравнение новых затрат возможно только после корректного обучения','В основном плане только исторический эталон'),
 ('G08','Итерации в зависимости от различия структур','Итерации.docx график 3; Итерации.xlsx диаграмма 1','Различие структур по исходному определению; число итераций','NL переобучение, NL с нуля, NT с нуля','Сохранить разреженные ряды и определение различия из таблицы. Не заменять его произвольной нормой векторов','В основном плане только исторический эталон'),
 ('G09','TPR TNR и сбалансированная точность по эпохам','Обучение по двум примерам.docx первый график; Средние нейроны; таблицы исследования','Эпоха; доля либо процент','Исторические значения и новые реакции каждого восстановленного состояния','Строить по соответствующим состояниям 51 к 61, сначала на исходной подвыборке, затем на 150 входах; не смешивать знаменатели','Структуры и исторические данные имеются'),
 ('G10','FPR FNR и сумма ошибок по эпохам','Обучение по двум примерам.docx второй график','Эпоха; процент либо число ошибок с явной единицей','FPR FNR и число FP плюс FN','Воспроизвести исходные показатели и отдельно стандартную долю ошибок; не складывать проценты с разными знаменателями','Структуры и исторические данные имеются'),
 ('G11','Precision и recall по эпохам и уровень среднего входа','ВКР рисунок 20; черновик диаграмма 1; Обучение нескольким примерам.xlsx диаграмма 3','Канонические эпохи 0 по 13; доля','Precision и recall 14 состояний и постоянные линии среднего 51 и 61','Отдельные линии архив и autoPreset, одинаковая популяция 150. Сохранить исходную нумерацию 1 по 14 как дополнительное поле','Полные структуры имеются'),
 ('G12','Исторический эмпирический риск как число ошибок','ВКР рисунок 21; Обучение нескольким примерам.xlsx диаграмма 4','Эпоха; количество FP плюс FN','Ряд Q и уровень среднего входа','Исторический Q равен числу ошибок, например 28 в начальном состоянии. Сохранить эту шкалу и не подменять долей','Полные структуры и исходные числа имеются'),
 ('G13','Нормированная доля ошибок и три базовых состояния','черновик график Сравнение суммы ошибок распознавания; защита слайд 11','Эпоха; 100 умножить на FP плюс FN делённое на N','Динамика и постоянные уровни 51 61 и среднего входа','Построить отдельно от G12. Для 150 входов 28 ошибок соответствуют 18.6667 процента','Полные структуры и исходные числа имеются'),
 ('G14','Распознавание десяти своих примеров по эпохам','Обучение нескольким примерам.xlsx диаграммы 1 и 2','Номер состояния; TP из 10','Предварительная схема и исправленная схема отдельными рядами','Сохранить точные снимки из output_data. Неоднозначность алгоритма предварительной схемы не мешает инференсу на её известных структурах','Нужна проверка формата записей ответов'),
 ('G15','Реакции на 150 входов и метрики классификации','Распознавание.xlsx; ВКР таблицы 4 и 5; отчёты о распознавании','ID входа 1 по 150; ответ 0 или 1; отдельные метрики','Исходная сохранённая модель, реконструкция и исторический эталон раздельно','Бинарные различия служат диагностикой. Основной критерий модели — сохранность и соответствие структуры. Сводить TP FP FN TN precision recall accuracy balanced accuracy и риск','22 исторических столбца имеются'),
 ('G16','Длины дендритов и числа синапсов','Инофрмация о длинах дендритов и числе синапсов.xlsx; Протоколы экспериментов; ВКР приложения','Входной канал либо номер состояния; целое число','Пять d и пять s, архив до загрузки после загрузки после Reset и после инференса','Точное сравнение известных целых параметров и графа связей. Пропуски не заполнять единицами. Различные документированные варианты не смешивать','Главный структурный критерий'),
 ('G17','Регрессии потери синапсов и часов расчёта','Как выглядят баги; Тестирование флаги','Время, с; потенциал, В; число синапсов','Сигналы и структура при смене входа, Reset и сохранении с загрузкой','Проверить отсутствие самопроизвольного изменения графа при отключённом обучении. Снимать те же каналы, что подписаны на историческом снимке','Нужны новые диагностические трассы'),
 ('G18','Схемы архитектур и алгоритмов','ВКР рисунки 1 по 6 и 8 по 13; защита; дополнительные слайды','Схема компонентов и соединений','Исходное дерево компонентов и фактический граф после загрузки','Схемы не являются временными рядами. Сравнить состав и связи; разместить изображения в DOCX, сведения о связях в XLSX','Документальные схемы для проверки реализации'),
]


def main():
    x=load(WORK/'inventory.json'); evidence=load(ROOT/'Reports/StructTrainClassic/_work/archive-evidence.json')
    docs={d['id']:d for d in x['documents']}
    preferred={}
    for d in sorted(x['documents'],key=lambda d:(not d['path'].startswith('Эксперименты/'), d['role']!='local',d['path'])):
        preferred.setdefault(d['sha256'],d['id'])
    for d in x['documents']:d['canonical_doc']=preferred[d['sha256']]
    charts=[c for c in x['charts'] if preferred[docs[c['doc']]['sha256']]==c['doc']]
    thesis=Document(ROOT/'Docs/ClassicStructTrainExperiments/ВКР_ЕременкоЕА.docx')
    tables=[[[cell.text.strip() for cell in row.cells] for row in table.rows] for table in thesis.tables]
    baseline=[]
    for a,b,c in zip(tables[6][1:],tables[7][1:],tables[8][1:]):
        v=[int(z) for z in b[1:11]]
        baseline.append({'label':b[0],'dendrites':v[:5],'synapses':v[5:],'input_pattern':[float(z.replace(',','.')) for z in a[1:6]],
                         'TP':int(c[1]),'FN':int(c[2]),'FP':int(c[3]),'TN':int(c[4]),'precision_source':float(c[5].replace(',','.')),
                         'recall_source':float(c[6].replace(',','.')),'Q_source':int(c[7]),'source':'ВКР таблицы 6 7 8'})
    epochs=[]
    for a,b in zip(tables[15][1:],tables[16][1:]):
        vals=[int(z) for z in a[1:11]]
        epochs.append({'epoch':int(a[0]),'dendrites':vals[:5],'synapses':vals[5:],
                       'TP':int(b[1]),'FN':int(b[2]),'FP':int(b[3]),'TN':int(b[4]),
                       'precision_source':float(b[5].replace(',','.')),'recall_source':float(b[6].replace(',','.')),
                       'Q_source':int(b[7]),'source':'ВКР приложение В таблицы В1 и В2'})
    primary=workbook(ROOT/'Docs/ClassicStructTrainExperiments/Эксперименты/Исследование/Обучение нескольким примерам.xlsx')['Схема 0 на 1+4 для 150 примеров']
    for i,r in enumerate(epochs,2):
        for key,col in [('TP','AC'),('FP','AD'),('FN','AE'),('TN','AF'),('Q_source','AI')]:
            if primary[f'{col}{i}']['value']!=r[key]:raise ValueError(f'Conflicting epoch source at {col}{i}')
        r['precision_source']=primary[f'AG{i}']['value'];r['recall_source']=primary[f'AH{i}']['value']
        r['source']=f'Эксперименты/Исследование/Обучение нескольким примерам.xlsx лист Схема 0 на 1+4 для 150 примеров строка {i}; ВКР приложение В'
    rows=[]
    def add(group,kind,label,d,s,source,known=True,**extra):
        if d is None and s is None:return
        record={'id':f'R{len(rows)+1:04}','group':group,'kind':kind,'label':str(label),'dendrites':d,'synapses':s,
                'source':source,'complete':d is not None and s is not None,'profile':'NL архив relearning' if kind=='learner' else 'NT архив Autocreate',**extra}
        raw=json.dumps([kind,d,s],sort_keys=True)
        record['structure_group']=hashlib.sha256(raw.encode()).hexdigest()[:12]
        rows.append(record)
    for r in evidence['cold']:
        add('cold','learner' if r['kind']=='learner' else 'trainer',f"ID {r['id']} повтор {r['repeat']}",r['dendrites'],r['synapses'],
            f"Протоколы экспериментов.xlsx {r['source']['sheet']} строка {r['source']['row']}",target=r['id'])
    structural_sheet=[d for d in x['documents'] if 'Инофрмация о длинах' in d['path']][0]
    partial=[]
    for r in evidence['structural']:
        source=f"{structural_sheet['path']} лист Дендриты и синапсы строка {r['source_row']}"
        if r['synapses'] is not None:
            add('150_examples',r['kind'],f"ID {r['id']}",r['dendrites'],r['synapses'],source,target=r['id'])
        elif any(isinstance(v,str) for v in r['raw_synapses']) and r['dendrites'] is not None:
            for variant in (0,1):
                syn=[]
                for v in r['raw_synapses']:
                    if isinstance(v,(float,int)):syn.append(int(v));continue
                    m=re.fullmatch(r'\s*(\d+)\s*\(\s*(\d+)\s*\)\s*',str(v))
                    if not m:break
                    syn.append(int(m[1+variant]))
                if len(syn)==5:
                    add('150_examples_alternative',r['kind'],f"ID {r['id']} {'внешние значения' if variant==0 else 'в скобках'}",r['dendrites'],syn,source,target=r['id'],variant=variant)
        elif r['dendrites'] is not None:
            partial.append({'kind':r['kind'],'id':r['id'],'dendrites':r['dendrites'],'synapses':None,'source':source})
            add('150_examples_partial',r['kind'],f"ID {r['id']} не хватает синапсов",r['dendrites'],None,source,target=r['id'])
    for s in x['snapshots']:
        add(s['kind'],'learner',f"{Path(s['path']).parent.name} {Path(s['path']).name} строка {s['line']}",s['dendrites'],s['synapses'],s['path'],
            answer_count=s['answer_count'],header_extra_fields=s['header_extra_fields'],snapshot=s['id'],source_line=s['line'])
    for r in baseline:
        add('baseline','learner',r['label'],r['dendrites'],r['synapses'],r['source'],target=r['label'])
    for r in epochs:
        add('epoch_1plus4','learner',f"Эпоха {r['epoch']}",r['dendrites'],r['synapses'],r['source'],epoch=r['epoch'])
    for table_index,kind,title in [(9,'learner','ВКР приложение А структура NL'),(10,'trainer','ВКР приложение А структура NT'),(13,'learner','ВКР приложение Б переходы к 129')]:
        for row in tables[table_index][1:]:
            try:vs=[int(v.replace('\u00a0','').strip()) for v in row[1:11]]
            except ValueError:continue
            if len(vs)==10:add('published_table',kind,row[0],vs[:5],vs[5:],title,target=row[0])

    # The signature only groups candidate duplicate structures. A run is shared
    # only after physical parameters, loaded state and inference protocol agree.
    groups={}
    for r in rows:
        if not r['complete']:continue
        groups.setdefault(r['structure_group'],{'id':r['structure_group'],'kind':r['kind'],'dendrites':r['dendrites'],'synapses':r['synapses'],'sources':[]})['sources'].append(r['id'])
    rendered=load(WORK/'source-chart-renders.json')
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
    for offset in range(0,len(rendered),6):
        canvas=Image.new('RGB',(1480,1380),'white'); draw=ImageDraw.Draw(canvas)
        for k,r in enumerate(rendered[offset:offset+6]):
            col,row=k%2,k//2
            with Image.open(report_path(r['preview'])) as im:
                im.thumbnail((720,420));canvas.paste(im,(col*740,row*460+30))
            draw.text((col*740+10,row*460+5),r['id']+' '+r['sheet'][:52],font=font,fill='black')
        canvas.save(WORK/f"charts-contact-{offset//6+1:02}.png")

    # Retain every local illustration occurrence, including non-plot diagrams.
    explicit={'c3a2737b':'G02','cb255eb5':'G01','f57e7053':'G03','9266ab41':'G03','4ed6e8b5':'G04','f6b043a3':'G05','db0f4370':'G01','8a1de4ef':'G11','e6b4dda9':'G12',
              '1114ce3d':'G06','70e30048':'G07','89801e46':'G08','8612e9c2':'G02','d9d7f70b':'G13','26411d59':'G03','a67daebb':'G02','07a7e0e8':'G02',
              'f544b3a1':'G17','3bd1f663':'G17','91c3da80':'G17','d5779488':'G02','896db7a8':'G03','9f25b5a1':'G04',
              '4b14ad75':'G09','2e49be6b':'G10','2b879a4e':'G01','f5854b82':'G01','9dc507c3':'G01'}
    figures=[]
    for a in x['assets']:
        if not a['local']:continue
        family=explicit.get(a['id'][:8],'G18')
        for context in a['contexts']:
            doc=docs[context['doc']]
            if doc['role']!='local':continue
            figures.append({'id':f'F{len(figures)+1:03}','asset':a['id'],'family':family,'source':doc['path'],
                            'doc':doc['id'],'location':context['location'],'context':context['context'],'preview':a.get('preview'),
                            'role':'числовой график' if family!='G18' else 'схема либо оформление','duplicate_source':doc['id']!=doc['canonical_doc']})
    chart_catalog=[]
    for c in charts:
        if 'scatterChart' in c['types']:family='G01'
        elif 'Итерации' in docs[c['doc']]['path']:
            family='G08' if 'chart1.xml' in c['member'] else 'G07' if 'chart2.xml' in c['member'] else 'G06'
        elif 'Обучение нескольким' in docs[c['doc']]['path']:
            family={'chart1.xml':'G14','chart2.xml':'G14','chart3.xml':'G11','chart4.xml':'G12'}[Path(c['member']).name]
        else:family='G11' if 'chart1.xml'==Path(c['member']).name else 'G13'
        chart_catalog.append({**c,'family':family,'source':docs[c['doc']]['path']})
    trained=[m for m in x['models'] if m['training_metadata_matches_graph']]
    data={'documents':x['documents'],'models':x['models'],'snapshots':x['snapshots'],'restoration_rows':rows,'structure_groups':list(groups.values()),
          'families':[dict(zip(['id','name','sources','axes','series','comparison','readiness'],r)) for r in FAMILIES],
          'figures':figures,'charts':chart_catalog,'source_chart_renders':rendered,'baselines':baseline,'epochs':epochs,
          'recognition_reference':evidence['recognition'],'dataset':evidence['dataset'],
          'coverage':{'files':len(x['documents']),'saved_components':len(x['models']),'confirmed_training_metadata':len(trained),
                      'snapshot_rows':len(x['snapshots']),'complete_structure_records':sum(r['complete'] for r in rows),
                      'candidate_structure_groups':len(groups),'native_charts_unique':len(chart_catalog),'figure_occurrences':len(figures),
                      'incomplete_structural_rows':len(partial),
                      'structural_table':{'NT_dendrites':31,'NL_dendrites':110,'NL_complete_numeric':1,'NT_rows_with_parentheses':4}}}
    save('plan-data.json',data)
    save('restoration-manifest.json',{'status':'prepared_specifications_not_executed_models','deduplication':'candidate grouping by class and d/s; physical fingerprint and protocol equality required before sharing a run',
                                     'rows':rows,'candidate_groups':list(groups.values())})
    print(json.dumps(data['coverage'],ensure_ascii=False))


if __name__=='__main__':main()
