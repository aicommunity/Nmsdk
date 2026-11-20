"""Build both Russian scientific reports from reviewed text and real figures.

Use the configured document runtime. --draft permits missing illustrations for
internal layout review only. A generated document is never a visual acceptance.
The earlier v3 builder remains available in the published v3 package and Git.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

def read(path):return json.loads(Path(path).read_bytes())
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def build(source,output,*,diagrams,figures=None,draft=False):
    from docx import Document
    from docx.shared import Inches,Pt,RGBColor
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
    from PIL import Image
    from .word_math import equation,sub,sup,scripts,absolute,group
    source=Path(source).resolve(strict=True);output=Path(output).resolve()
    if output.exists():raise ValueError('Fresh output directory required')
    content_path=source/'revision4-content.ru.json';content=read(content_path)
    review_path=source/content['review'];review=read(review_path)
    evidence_path=source.parent/'AlgorithmDescriptionEvidenceReview-20261118.json'
    cases={c['id']:c for c in read(evidence_path)['qualifying_examples']}
    if content.get('schema_version')!=1 or len(review['comments'])!=8:
        raise ValueError('Known reviewed scientific description required')
    if any(c['counts']['TP']<1 or c['counts']['TN']<2 for c in cases.values()):
        raise ValueError('Working example criterion not satisfied')
    diagrams=Path(diagrams).resolve(strict=True);dm=read(diagrams);dr=diagrams.parent
    if dm['kind']!='timelearner_scientific_diagram_render':raise ValueError('Graphviz sources required')
    for d in dm['diagrams']:
        if digest(dr/(d['id']+'.png'))!=d['png_sha256']:raise ValueError('Diagram bytes changed')
    fc=read(figures) if figures else {};fr=Path(figures).resolve().parent if figures else None
    if fc and (fc.get('kind')!='timelearner_algorithm_illustration_catalog' or fc.get('schema_version')!=1):
        raise ValueError('Known illustration catalog required')
    trial_figures=fc.get('trials',[]);concepts={c['id']:c for c in fc.get('concepts',[])}
    details=fc.get('case_details',{})
    concept_ids=('assigned-peak','separate-early-peak','merged-peaks','missing-peak',
                 'incomplete-window','n0-measured-search','n1-measured-search')
    missing=['concept:'+i for i in concept_ids if i not in concepts]
    for identity,case in cases.items():
        need={'TP','TN'}|({'FP'} if case['counts']['FP'] else set())
        have={f['response'] for f in trial_figures if f['case_id']==identity}
        missing.extend(identity+':'+v for v in sorted(need-have))
        for key in ('title','explanation','threshold','train_configuration_ref',
                    'test_configuration_ref','source_collection_ref','frequency_hz','measurement_version'):
            if details.get(identity,{}).get(key) is None:missing.append(identity+':'+key)
    if missing and not draft:raise ValueError('Measured figures/details missing: '+', '.join(missing))
    for record in [*trial_figures,*concepts.values()]:
        rel=Path(record['png']['path']);path=(fr/rel).resolve(strict=True)
        if rel.is_absolute() or '..' in rel.parts or not path.is_relative_to(fr):raise ValueError('Local figure required')
        if path.stat().st_size!=record['png']['bytes'] or digest(path)!=record['png']['sha256']:
            raise ValueError('Measured figure bytes changed')
        if not record.get('source_ref'):raise ValueError('Measured figure provenance required')
    output.mkdir(parents=True);results=[]

    def style_font(style,name,size):
        style.font.name=name;style.font.size=Pt(size);style.font.color.rgb=RGBColor(0,0,0)
        style.font.underline=False;rpr=style.element.get_or_add_rPr()
        fonts=rpr.find(qn('w:rFonts'))
        if fonts is None:fonts=OxmlElement('w:rFonts');rpr.insert(0,fonts)
        for key in ('ascii','hAnsi','eastAsia','cs'):fonts.set(qn('w:'+key),name)
        for key in ('asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme'):fonts.attrib.pop(qn('w:'+key),None)

    def table(doc,headers,rows,widths):
        t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
        for c,w in zip(t.columns,widths):c.width=Inches(w)
        for c,text in zip(t.rows[0].cells,headers):c.text=str(text)
        t.rows[0]._tr.get_or_add_trPr().append(OxmlElement('w:tblHeader'))
        for row in rows:
            for c,text in zip(t.add_row().cells,row):c.text=str(text)
        borders=OxmlElement('w:tblBorders')
        for name in ('top','left','bottom','right','insideH','insideV'):
            edge=OxmlElement('w:'+name);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4')
            edge.set(qn('w:color'),'D0D0D0');borders.append(edge)
        t._tbl.tblPr.append(borders)
        for i,row in enumerate(t.rows):
            row._tr.get_or_add_trPr().append(OxmlElement('w:cantSplit'))
            for j,c in enumerate(row.cells):
                c.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                if i==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'EEEEEE');c._tc.get_or_add_tcPr().append(shade)
                for p in c.paragraphs:
                    p.paragraph_format.space_before=Pt(4);p.paragraph_format.space_after=Pt(4)
                    p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 else WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:r.font.size=Pt(10.5);r.bold=i==0

    for topology in ('classic','branch'):
        doc=Document();section=doc.sections[0]
        section.page_width=Inches(8.5);section.page_height=Inches(11)
        section.left_margin=section.right_margin=Inches(1)
        section.top_margin=section.bottom_margin=Inches(.75)
        for name,size in [('Normal',11.5),('Title',17),('Subtitle',11.5),('Heading 1',14),('Heading 2',12),('Caption',10.5)]:
            style_font(doc.styles[name],'Arial',size)
        doc.styles['Caption'].font.bold=False
        doc.styles['Caption'].font.italic=False
        doc.styles['Normal'].paragraph_format.space_after=Pt(6)
        doc.styles['Normal'].paragraph_format.line_spacing=1.12
        code=doc.styles.add_style('Псевдокод',1);style_font(code,'Consolas',10.5)
        code.paragraph_format.space_after=Pt(1);code.paragraph_format.line_spacing=1.05
        code.paragraph_format.keep_with_next=True
        footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
        footer.add_run('Страница ');field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
        common=content['common'];specific=content[topology];used=[]
        def para(text,style=None):return doc.add_paragraph(text,style=style)
        def paras(values):
            for text in values:para(text)
        def head(text,level=1):return doc.add_heading(text,level=level)
        def image(path,caption,source_ref=None):
            path=Path(path)
            with Image.open(path) as im:width,height=im.size
            scale=min(6.35/width,7.8/height)
            p=para('');p.alignment=WD_ALIGN_PARAGRAPH.CENTER;p.paragraph_format.keep_with_next=True
            p.add_run().add_picture(str(path),width=Inches(width*scale),height=Inches(height*scale))
            c=para('Рисунок '+str(len(used)+1)+' '+caption,'Caption');c.paragraph_format.keep_together=True
            if source_ref:para('Источник измерений: '+source_ref,'Caption')
            used.append(dict(file=str(path),sha256=digest(path),caption=caption))
        def diagram(identity,caption):image(dr/(identity+'.png'),caption)
        def concept(identity):
            record=concepts.get(identity)
            if record:image(fr/record['png']['path'],record['caption'],record['source_ref'])
            elif draft:para('Черновик Измеренная иллюстрация '+identity+' подготавливается')
        para(specific['title'],'Title');para(content['edition'],'Subtitle')
        if draft:para('ЧЕРНОВИК Для внутренней проверки текста и верстки')
        paras(common['introduction'])
        head('Сегментная модель и входной паттерн')
        paras(common['model']);paras(specific['topology']);paras(common['stimulus'])
        head('Математическая цель обучения');paras(common['goal'])
        equation(doc,sub('e','A,i'),' = ',sub('A','i'),' − ',scripts('A','i','(0)'))
        equation(doc,sub('ε','A,i'),' = ',sub('ε','abs'),' + ',sub('ε','rel'),absolute(scripts('A','i','(0)')))
        equation(doc,absolute(sub('e','A,i')),' ≤ ',sub('ε','A,i'))
        equation(doc,scripts('e','t,i','−'),' = ',scripts('t','i','−'),' − ',scripts('t','r','+'),',   ',
                 scripts('e','t,i','+'),' = ',scripts('t','i','+'),' − ',scripts('t','r','−'))
        equation(doc,['function','max',group(absolute(scripts('e','t,i','−')),', ',absolute(scripts('e','t,i','+')))],' ≤ ',sub('δ','t'),',   i ≠ r')
        equation(doc,sub('L','min,i'),' ≤ ',sub('L','i'),' ≤ ',sub('L','max,i'),',   ',sub('L','i'),' ∈ ℕ')
        equation(doc,'N0:   ',sub('N','min,i'),' ≤ ',sub('N','s,i'),' ≤ ',sub('N','max,i'),',   ',sub('N','s,i'),' ∈ ℕ')
        equation(doc,'N1:   0 < ',sub('R','min,i'),' ≤ ',sub('R','s,i'),' ≤ ',sub('R','max,i'))
        diagram(specific['diagram'],'Физическая организация модели. Стрелки показывают передачу сигнала, штриховые связи — перезарядку. Геометрический масштаб условный.')
        head('Измерение закреплённого отклика');paras(common['measurement'])
        for identity in concept_ids[:5]:concept(identity)
        head('Последовательность структурной адаптации');paras(common['search'])
        diagram(specific['learning_diagram'],'Основная последовательность обучения. Локальная готовность и свежая проверка всех входов являются разными условиями.')
        for line in ('Задать паттерн, исходную структуру и ограничения','Измерить собственные исходные амплитуды входов',
          'Измерить опорный отклик','Пока остаются допустимые действия и бюджет',
          '  Выбрать вход в порядке, заданном топологией','  Предложить допустимый полный кандидат',
          '  Между пробами применить изменение структуры','  Получить завершённый измеренный отклик',
          '  Если отклик недостоверен','    Продолжить по политике либо явно остановиться',
          '  Иначе вычислить ошибки времени и амплитуды','    Сохранить проверенную точку поиска',
          'Проверить все входы на конечной модели','Зафиксировать исход и фактическое состояние'):
            para(line,'Псевдокод')
        doc.paragraphs[-1].paragraph_format.keep_with_next=False
        for title,key,diagram_id,concept_id in [('Синхронизация','synchronization',None,None),
          ('Нормализация числом синапсов','n0','normalization-n0','n0-measured-search'),
          ('Нормализация сопротивлением','n1','normalization-n1','n1-measured-search')]:
            head(title);paras(common[key])
            if key=='n1':
                equation(doc,'R(q) = exp',group('ln ',sub('R','min'),' + q',group('ln ',sub('R','max'),' − ln ',sub('R','min'))),',   q = ',['fraction','2k − 1',sup('2','j')])
                para('В формуле сетки j — уровень деления, k — номер нечётной точки этого уровня. Используются только ещё не проверенные допустимые значения.')
                ratio=['fraction',absolute(sub('e','A,a')),
                       ['row',absolute(sub('e','A,a')),' + ',absolute(sub('e','A,b'))]]
                clamped=['function','min',group('¾, ',['function','max',group('¼, ',ratio)])]
                equation(doc,'λ = ',clamped)
                equation(doc,sub('R','new'),' = exp',group('ln ',sub('R','a'),
                         ' + λ ln',group(['fraction',sub('R','b'),sub('R','a')])))
                para('Индексы a и b обозначают измеренные концы выбранного интервала с разными знаками амплитудной ошибки. Применимость уточнения проверяется до вычисления нового сопротивления.')
            if diagram_id:diagram(diagram_id,title+' с повторным измерением времени и амплитуды.')
            if concept_id:concept(concept_id)
        head('Завершение обучения и распознавание');paras(common['finalization']);paras(common['recognition'])
        head('Экспериментальные примеры');ids=specific['example_order']
        name=lambda i:details.get(i,{}).get('title','Пример '+str(ids.index(i)+1))
        table(doc,['Пример','Обнаружения','Ложные ответы','Пропуски','Правильные отклонения'],
              [[name(i),*[cases[i]['counts'][k] for k in ('TP','FP','FN','TN')]] for i in ids],[2.4,1.,1.,.85,1.1])
        para('Указаны числа предъявлений, а не число независимых обучений. Число разных отвлекающих паттернов приведено отдельно.')
        for identity in ids:
            case=cases[identity];info=details.get(identity,{})
            head(name(identity),2)
            paras(info.get('explanation',['Черновик Подробные условия сверяются по первичным данным.']))
            para('Разных отвлекающих паттернов: '+str(case['unique_foil_patterns'])+'.')
            threshold=info.get('threshold',case.get('threshold'))
            para('Порог: '+(format(threshold,'.17g') if isinstance(threshold,(int,float)) else 'уточняется по пакету модели в черновике')+'.')
            if case.get('early_target'):para('Ответ на цель возник до последнего входного импульса. Это ограничивает вывод о распознавании полной временной структуры.')
            if case['unique_foil_patterns']==1:para('Отрицательные предъявления относятся к одному паттерну при двух условиях сброса, а не к двум разным отрицательным классам.')
            if case['training_outcome']=='budget_exhausted':para('Остановка по бюджету сохранена. Подбор порога не является доказательством сходимости обучения.')
            for key,label in [('train_configuration_ref','Обучающая конфигурация'),('test_configuration_ref','Проверочная конфигурация')]:
                if info.get(key):para(label+': '+info[key])
            selected=[f for f in trial_figures if f['case_id']==identity]
            for f in selected:image(fr/f['png']['path'],f['caption'],f['source_ref'])
            if not selected and draft:para('Черновик Графики правильных и ложных ответов подготавливаются.')
            para('Источник: '+case['source']['path']+'; версия '+case['source']['commit'])
        head('Реализация вычисления и владение моделью');paras(common['implementation'])
        diagram('logical-classes','Логическая UML диаграмма обязанностей компонентов обучения.')
        table(doc,['Обязанность','Точное имя в программе'],[
          ['Модуль обучения','NNeuronTimeLearner' if topology=='classic' else 'NNeuronTimeLearnerBranch'],
          ['Управление сессией','NativeTrainingService'],['Ограниченный поиск','BoundedTrainingSession'],
          ['Составное измерение','CompositeTrainingMeasurement'],['Общая проверка','FinalVerificationSession'],
          ['Физическая модель','NPulseNeuron']],[3.,3.35])
        diagram('probe-sequence','UML последовательность пробы. Расчёт такта и сбор отсчётов повторяются до закрытия окна. Контроллер не вызывает вложенный расчёт модели.')
        head('Границы подтверждённого результата');paras(common['limitations'])
        head('Источники и происхождение иллюстраций')
        para('Публикации авторов служат образцом стиля и терминологии. Объяснение действующего алгоритма основано на реализации и измерениях.')
        para('Корсаков А. М., Астапова Л. А., Бахшиев А. В. Применение сегментной спайковой модели нейрона со структурной адаптацией для решения задач классификации. Информатика и автоматизация. 2022. Том 21. № 3. DOI 10.15622/ia.21.3.2.')
        para('Бахшиев А. В., Гунделах Ф. В. Математическая модель преобразования импульсов в естественных нейронах для разработки биологически вдохновлённых систем управления. Предоставленная авторами рукопись 2015 года; название приведено в переводе.')
        para('Полные временные отчёты содержат реакции на весь набор паттернов. Выбранные измеренные иллюстрации в этом документе не являются новыми независимыми опытами.')
        filename='TimeLearner'+('Classic' if topology=='classic' else 'Branch')+'Algorithms.ru.docx'
        path=output/filename;doc.core_properties.title=specific['title'];doc.core_properties.language='ru-RU';doc.save(path)
        results.append(dict(topology=topology,file=filename,bytes=path.stat().st_size,sha256=digest(path),
            figures=used,draft=draft,equation_format='native_OMML',render_and_visual_review_complete=False))
    result=dict(kind='timelearner_algorithm_docx_build',schema_version=2,edition='2026-11-19-v4',documents=results,
        inputs={str(p):digest(p) for p in (content_path,review_path,evidence_path,diagrams)},
        illustration_catalog_sha256=digest(figures) if figures else None,missing_illustrations_or_details=missing,
        draft=draft,all_comments_closed=False,visual_acceptance_complete=False,generated_binary_in_root_git=False)
    (output/'build.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='\n')
    return result

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ('source','output','diagrams'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--figures',type=Path);parser.add_argument('--draft',action='store_true')
    args=parser.parse_args(argv);result=build(args.source,args.output,diagrams=args.diagrams,figures=args.figures,draft=args.draft)
    print(json.dumps(dict(documents=[r['file'] for r in result['documents']],draft=args.draft,
        missing_illustrations_or_details=len(result['missing_illustrations_or_details']),visual_acceptance_complete=False)))

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
    from Scripts.StructTrain.TimeLearner.publications.build_algorithm_docx import main as run
    run()
