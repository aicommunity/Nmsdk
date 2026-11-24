"""Explain source provenance and experimental notation without new simulations."""
from pathlib import Path
import json,re,zipfile,hashlib
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[2]
WORK=ROOT/'Reports/StructTrainClassic/LegacyChecks-20261123'
PRIMARY='Эксперименты/Инофрмация о длинах дендритов и числе синапсов.xlsx'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def enrich(data,plan,assessment):
    path=ROOT/'Docs/ClassicStructTrainExperiments'/PRIMARY
    ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(path) as z:
        shared=[''.join(s.itertext()) for s in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        cells={}
        for c in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//m:sheetData/m:row/m:c',ns):
            v=c.findtext('m:v',namespaces=ns)
            if v is not None:cells[c.get('r')]=shared[int(v)] if c.get('t')=='s' else float(v)
    mapping={r['row']:r for r in load(WORK/'recovered-mapping.json')}
    recovered={r['id']:r for r in load(ROOT/'Bin/Configs/StructTrainClassic/LegacyInference/recovered-jobs.json')}
    rows=[]
    for r in plan['restoration_rows']:
        if PRIMARY not in r['source']:continue
        m=mapping[r['id']];line=int(re.search(r'строка (\d+)',r['source'])[1]);nt=r['kind']=='trainer'
        raw_s=[cells.get(f'{c}{line}') for c in (['R','S','T','U','V'] if nt else ['W','X','Y','Z','AA'])]
        job=m.get('job');physical=recovered.get(job,{})
        rows.append({'record':r['id'],'input_id':r['target'],'algorithm':'NT' if nt else 'NL','label':r['label'],
            'row':line,'length_range':f'G{line}:K{line}' if nt else f'L{line}:P{line}',
            'synapse_range':f'R{line}:V{line}' if nt else f'W{line}:AA{line}',
            'dendrites':r['dendrites'],'original_synapses':raw_s,'effective_synapses':physical.get('synapses'),
            'job':job,'status':m['status'],'donors':m.get('completion_donors',[]),
            'directory':assessment['first_by_job'].get(job,{}).get('directory')})
    source_examples=[]
    for ident in [1,22,51,61]:
        line=ident+1
        source_examples.append({'input_id':ident,'row':line,'NT_d':[cells.get(f'{c}{line}') for c in 'GHIJK'],
            'NL_d':[cells.get(f'{c}{line}') for c in 'LMNOP'],
            'NT_s':[cells.get(f'{c}{line}') for c in 'RSTUV'],
            'NL_s':[cells.get(f'{c}{line}') for c in ['W','X','Y','Z','AA']]})
    data['primary_source']={'path':str(path),'relative':PRIMARY,'sheet':'Дендриты и синапсы','sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'records':len(rows),'complete':sum(r['status']=='constructed' for r in rows),'unresolved':sum(r['status']!='constructed' for r in rows),
        'completed_with_donors':sum(bool(r['donors']) for r in rows),'rows':rows,'examples':source_examples}
    data['input_examples']=[r for r in plan['dataset'] if r['id'] in [51,61]]
    data['scheme_explanations']={
        'E01':('Обучение примеру № 61 с согласованием числа синапсов','После полного обучения примеру № 51 выполняли циклы: одна итерация изменения дендритов и синапсов на примере № 61, затем четыре итерации изменения только синапсов. Тестировали 14 сохранённых состояний на всех 150 входах. Архивное обозначение — «0/(1+4)».'),
        'E02':('Предварительный вариант перехода к примеру № 61','После обучения примеру № 51 в архиве сохраняли последовательные структуры при переходе к примеру № 61. Лист обозначен «0/(1(2)+4)»; точный порядок одной или двух совместных итераций документирован неоднозначно. Для оценки готовых семи структур порядок обучения не восстанавливался. Подвыборка: № 41–60 и 101–110.'),
        'E03':('Обучение примеру № 61 с дополнительной настройкой синапсов','После полного обучения примеру № 51 один цикл состоял из одной совместной итерации изменения дендритов и синапсов и четырёх итераций только синапсов на примере № 61. Проверены 14 состояний на десяти положительных входах № 51–60. Архивное обозначение — «0/(1+4), верные синапсы».'),
        'E04':('Чередование трёх итераций для примера № 51 и четырёх для № 61','В архивном опыте после полного обучения примеру № 51 выполняли четыре итерации для № 61 и тестирование. Затем повторяли три итерации для № 51, четыре для № 61 и тестирование. Проверены семь готовых состояний на входах № 41–60 и 101–110. Архивное обозначение — «3/4».'),
        'E05':('Последовательное обучение примеру № 61 по одной итерации','В архивном опыте сначала полностью обучали нейрон примеру № 51. Затем повторяли одну итерацию обучения примеру № 61 и тестирование, без возврата к обучению № 51. Проверены 18 готовых состояний на входах № 41–60 и 101–110. Ноль в архивном обозначении «0/1» означает отсутствие дополнительных итераций для № 51.'),
        'E06':('Сравнение структур для двух входов и их среднего','Сопоставлены три структуры, исторически обученные входам № 51, № 61 и среднему арифметическому их нормированных векторов. Числа 51 и 61 — номера объектов Iris, а не значения параметров нейрона.'),
        'E07':('Сравнение NT и NL после обучения отдельным входам','NT означает NNeuronTrainer, NL — NNeuronLearner. Число после обозначения — номер обучающего объекта Iris. Число в скобках у NT64 и NL129 — подписанный в архиве вариант структуры, который рассматривается отдельно.')}
    axis={
        'SC01':('Номер состояния в рабочем отчёте','Доля верных ответов, %'),
        'SC02':('Номер состояния в рабочем отчёте','FPR, FNR и их сумма, %'),
        'SC03':('Номер состояния в ВКР','Точность P и полнота R, доля'),
        'SC04':('Номер состояния в ВКР','Число ошибок Q = FP + FN, шт.'),
        'SC05':('Номер сохранённого состояния','Верные ответы TP из 10, шт.'),
        'SC06':('Номер сохранённого состояния','Верные ответы TP из 10, шт.'),
        'SC07':('Номер сохранённого состояния','Верные ответы TP из 10, шт.'),
        'SC08':('Номер сохранённого состояния','Ложные срабатывания FP из 20, шт.'),
        'SC09':('Номер сохранённого состояния','Верные ответы TP из 10, шт.'),
        'SC10':('Номер сохранённого состояния','Ложные срабатывания FP из 20, шт.'),
        'SC11':('Вход, которому обучена структура','Точность P и полнота R, %'),
        'SC12':('Вход, которому обучена структура','Число ошибок Q = FP + FN, шт.'),
        'SC13':('Алгоритм, номер входа и вариант структуры','Сбалансированная точность, %'),
        'SC14':('Алгоритм, номер входа и вариант структуры','Число ошибок Q = FP + FN, шт.'),
        'SC15':('Номер состояния в ВКР','Доля ошибок Q / 150, %')}
    titles={'SC05':'Переход к входу № 61: предварительный вариант','SC06':'Переход к входу № 61: настройка синапсов','SC07':'Чередование обучения № 51 и № 61: верные ответы','SC08':'Чередование обучения № 51 и № 61: ложные ответы','SC09':'По одной итерации для № 61: верные ответы','SC10':'По одной итерации для № 61: ложные ответы'}
    for f in data['figures']:
        f['x_axis'],f['y_axis']=axis.get(f['id'],('Время от первого максимума, с','Сумма потенциалов сом, В'))
        if f['id'] in titles:f['title']=titles[f['id']]
        f['headers']=[h.replace('Исторический результат','Архив').replace('Инференс autoPreset','autoPreset').replace('Повтор','autoPreset') for h in f['headers']]
    for c in data['cases']:
        c['title'],c['explanation']=data['scheme_explanations'][c['id']]
    assert len(rows)==145 and data['primary_source']['complete']==14 and data['primary_source']['unresolved']==131
    return data

if __name__=='__main__':
    d=enrich(load(WORK/'scientific-comparison-data.json'),load(WORK/'execution-plan-data.json'),load(WORK/'assessment.json'))
    (WORK/'scientific-comparison-data.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:v for k,v in d['primary_source'].items() if k not in ['rows']},ensure_ascii=False,indent=2))
