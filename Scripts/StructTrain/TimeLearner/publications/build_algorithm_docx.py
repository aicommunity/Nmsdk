"""Build maintained algorithm descriptions; generated DOCX/PNG stay outside Git.

Run with the configured document runtime (python-docx, Pillow, lxml). Native
OMML keeps equations editable. render_docx.py and page inspection are separate
mandatory publication checks, not inferred from successful file creation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path


def _reviewed_catalog(path):
    """Read the dated evidence review without promoting its provenance role."""
    path=Path(path).resolve(strict=True)
    raw=path.read_bytes();review=json.loads(raw)
    if review.get('kind')!='timelearner_algorithm_document_evidence_review' or review.get('schema_version')!=1:
        raise ValueError('known algorithm evidence review required')
    cases=review['qualifying_examples'];seen=set()
    for case in cases:
        counts=case['counts']
        if (case['id'] in seen or case['topology'] not in ('Classic','Branch') or
            any(type(counts[k]) is not int or counts[k]<0 for k in ('TP','FP','FN','TN')) or
            counts['TP']<1 or counts['TN']<2 or case.get('qualifies_user_tp_tn') is not True):
            raise ValueError('qualified distinct algorithm examples required')
        seen.add(case['id'])
        threshold=case.get('threshold')
        if threshold is not None and (type(threshold) not in (int,float) or not math.isfinite(threshold)):
            raise ValueError('finite actual threshold required')
        source=case['source']
        if any(len(source[k])!=size for k,size in (('commit',40),('blob',40),('sha256',64))):
            raise ValueError('versioned source evidence required')
    return review,dict(path=str(path),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw))


def build(source, output, review=None):
    from docx import Document
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt, RGBColor
    from PIL import Image, ImageDraw, ImageFont

    source=Path(source).resolve(strict=True);output=Path(output).resolve()
    if output.exists():raise ValueError('new output directory required')
    content=json.loads((source/'content.json').read_text(encoding='utf-8'))
    evidence=json.loads((source/'evidence-register.json').read_text(encoding='utf-8'))
    catalog,catalog_ref=_reviewed_catalog(review) if review is not None else (None,None)
    supplement=json.loads((source/'next-edition.json').read_text(encoding='utf-8')) if catalog else None
    edition=supplement['edition'] if supplement else content['edition']
    output.mkdir(parents=True);figures=output/'figures';figures.mkdir()
    common=content['common']
    font_root=Path('C:/Windows/Fonts')
    regular=font_root/'arial.ttf';bold=font_root/'arialbd.ttf'
    if not regular.is_file() or not bold.is_file():raise ValueError('explicit Cyrillic-capable figure fonts required')

    def canvas(width,height):
        image=Image.new('RGB',(width,height),'white');return image,ImageDraw.Draw(image)
    def label(draw,xy,text,size=30,strong=False,anchor='mm'):
        font=ImageFont.truetype(str(bold if strong else regular),size)
        draw.multiline_text(xy,text,font=font,fill='black',anchor=anchor,align='center',spacing=8)
    def arrow(draw,a,b,*,dashed=False):
        import math
        if dashed:
            distance=math.dist(a,b);segments=max(1,int(distance/18))
            for i in range(0,segments,2):
                f=i/segments;g=min(1.,(i+1)/segments)
                draw.line((a[0]+f*(b[0]-a[0]),a[1]+f*(b[1]-a[1]),
                           a[0]+g*(b[0]-a[0]),a[1]+g*(b[1]-a[1])),fill='#343434',width=3)
        else:draw.line((a,b),fill='#343434',width=3)
        angle=math.atan2(b[1]-a[1],b[0]-a[0]);n=16
        draw.polygon([b,(b[0]-n*math.cos(angle-.45),b[1]-n*math.sin(angle-.45)),
                      (b[0]-n*math.cos(angle+.45),b[1]-n*math.sin(angle+.45))],fill='#343434')
    def box(draw,rect,text,*,strong=False):
        draw.rounded_rectangle(rect,12,fill='#f4f6f8',outline='#555555',width=3)
        label(draw,((rect[0]+rect[2])/2,(rect[1]+rect[3])/2),text,strong=strong)

    def flow():
        im,d=canvas(1400,1560)
        stages=[('Storage и ModelSpec\nШтатное построение и частота',100),
                ('CapturedPerInput\nСобственная исходная амплитуда входа',280),
                ('BoundedTrainingSession\nСледующее допустимое действие',460),
                ('Native probe\nПолная проба и закрытие окна',640),
                ('Проверка данных и revision\nИзмерение либо ограниченное recovery',820),
                ('Обновить поиск\nПри готовности проверить все входы',1000)]
        for text,y in stages:box(d,(210,y,1190,y+120),text)
        for (_,a),(_,b) in zip(stages,stages[1:]):arrow(d,(700,a+120),(700,b))
        arrow(d,(700,1120),(700,1135))
        d.polygon([(700,1135),(890,1215),(700,1295),(510,1215)],fill='#e8eef4',outline='#555555',width=3)
        label(d,(700,1215),'Завершено',28,True)
        arrow(d,(890,1215),(1310,1215));arrow(d,(1310,1215),(1310,520));arrow(d,(1310,520),(1190,520))
        label(d,(1110,1185),'нет',27);label(d,(1245,770),'ещё\nдействия',22)
        arrow(d,(700,1295),(700,1350));label(d,(750,1320),'да',27)
        box(d,(150,1350,1250,1475),'Finished и отдельный результат\nExact   SearchUnresolved   BudgetExhausted   Invalid',strong=True)
        label(d,(700,1520),'Edit и оценка домена выполняются до очередной пробы',27)
        path=figures/'training-flow.png';im.save(path);return path

    def n0_flow():
        im,d=canvas(1400,1400)
        for text,y in [('Допустимый полный кандидат L и Ns',60),
                       ('Native edit и effective readback',240),
                       ('Измерить anchor и активный вход\nСобрать объявленную группу повторов',420),
                       ('Проверить validity и revision\nСохранить измеренные остатки',600)]:
            box(d,(150,y,1120,y+120),text)
        for y in (180,360,540):arrow(d,(635,y),(635,y+60))
        arrow(d,(635,720),(635,760))
        d.polygon([(635,760),(920,850),(635,940),(350,850)],fill='#e8eef4',outline='#555555',width=3)
        label(d,(635,850),'Допуски выполнены',28,True)
        box(d,(800,1100,1350,1240),'Следующий вход\nЗатем финальная\nпроверка всех входов')
        arrow(d,(920,850),(1260,850));arrow(d,(1260,850),(1260,1100));label(d,(1100,815),'да',27)
        box(d,(100,1020,700,1180),'Ограниченная очередь\nсоседей Ns и геометрий')
        arrow(d,(635,940),(635,1020));label(d,(700,975),'нет',27)
        arrow(d,(100,1100),(50,1100));arrow(d,(50,1100),(50,120));arrow(d,(50,120),(150,120))
        label(d,(700,1330),'Invalid → объявленное recovery или terminal outcome\nИсчерпан бюджет → BudgetExhausted',28)
        path=figures/'n0-candidate-flow.png';im.save(path);return path

    def classes(component):
        im,d=canvas(1400,1130)
        nodes=[((50,55,650,325),component,'NativeTrainingControl\nABeforeCalculate   ACalculate'),
               ((750,55,1350,325),'NativeTrainingService','state   search\nStart   BeforeTick   AfterTick'),
               ((50,445,650,715),'NativeTrainingAdapter','readParameters   apply\nqueue   takeResult'),
               ((750,445,1350,715),'BoundedTrainingSession','current   epoch\nNextAction   Consume'),
               ((50,835,650,1075),'NPulseNeuron','Эффективный физический граф\nBuild   Reset   Calculate'),
               ((750,835,1350,1075),'FinalVerificationSession','Свежие измерения всех входов\nСертификат конкретной revision')]
        for rect,title,body in nodes:
            d.rectangle(rect,fill='#f7f8fa',outline='#555555',width=3)
            y=rect[1]+78;d.line((rect[0],y,rect[2],y),fill='#555555',width=2)
            label(d,((rect[0]+rect[2])/2,rect[1]+38),title,29,True)
            label(d,((rect[0]+rect[2])/2,(y+rect[3])/2),body,28)
        # Composition: learner owns the service value. Shared aggregation:
        # service holds a shared_ptr to search. Search owns final verification.
        for y,fill in ((190,'black'),):
            d.polygon([(650,y),(670,y-12),(690,y),(670,y+12)],fill=fill,outline='black')
            arrow(d,(690,y),(750,y))
        d.polygon([(1050,325),(1038,345),(1050,365),(1062,345)],fill='white',outline='black')
        arrow(d,(1050,365),(1050,445))
        d.polygon([(1050,715),(1038,735),(1050,755),(1062,735)],fill='black',outline='black')
        arrow(d,(1050,755),(1050,835))
        arrow(d,(850,325),(600,445),dashed=True)
        arrow(d,(350,715),(350,835),dashed=True)
        path=figures/(component+'-classes.png');im.save(path);return path

    def sequence():
        im,d=canvas(1400,1120);xs=[140,420,700,980,1260]
        names=['Rdk\nscheduler','learner','training\nservice','native\nprobe','native\nchildren']
        for x,name in zip(xs,names):
            box(d,(x-115,35,x+115,155),name)
            for y in range(175,1060,24):d.line((x,y,x,min(y+12,1060)),fill='#777777',width=2)
        messages=[(0,1,'ABeforeCalculate',230),(1,2,'BeforeTick',330),
                  (1,3,'BeforeChildren',430),(0,4,'Calculate once',550),
                  (0,1,'ACalculate',680),(1,3,'AfterChildren',790),
                  (1,2,'AfterTick',900)]
        for a,b,text,y in messages:
            arrow(d,(xs[a],y),(xs[b],y));label(d,((xs[a]+xs[b])/2,y-28),text,29)
        label(d,(700,1090),'Один native tick   Служба не вызывает Calculate модели',28,True)
        path=figures/'native-tick-sequence.png';im.save(path);return path

    shared_flow=flow();shared_sequence=sequence()

    def mathnode(value):
        if isinstance(value,str):
            r=OxmlElement('m:r');t=OxmlElement('m:t');t.set(qn('xml:space'),'preserve');t.text=value;r.append(t);return r
        kind=value[0]
        if kind=='delimited':
            node=OxmlElement('m:d');props=OxmlElement('m:dPr')
            for name,text in [('begChr',value[1]),('endChr',value[2])]:
                char=OxmlElement('m:'+name);char.set(qn('m:val'),text);props.append(char)
            node.append(props);body=OxmlElement('m:e')
            for child in value[3:]:body.append(mathnode(child))
            node.append(body);return node
        if kind=='subsup':
            node=OxmlElement('m:sSubSup')
            for name,item in [('e',value[1]),('sub',value[2]),('sup',value[3])]:
                child=OxmlElement('m:'+name);child.append(mathnode(item));node.append(child)
            return node
        if kind=='row':
            e=OxmlElement('m:e')
            for child in value[1:]:e.append(mathnode(child))
            return e
        if kind in ('sub','sup'):
            node=OxmlElement('m:sSub' if kind=='sub' else 'm:sSup')
            base=OxmlElement('m:e');base.append(mathnode(value[1]));node.append(base)
            script=OxmlElement('m:sub' if kind=='sub' else 'm:sup');script.append(mathnode(value[2]));node.append(script)
            return node
        raise ValueError('unknown native equation node')
    def equation(doc,*nodes):
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        m=OxmlElement('m:oMath')
        for item in nodes:m.append(mathnode(item))
        p._p.append(m);p.paragraph_format.space_after=Pt(9)
    def sub(a,b):return ['sub',a,b]
    def sup(a,b):return ['subsup',a[1],a[2],b] if isinstance(a,list) and a[0]=='sub' else ['sup',a,b]
    def absolute(a):return ['delimited','|','|',a]
    def parentheses(*nodes):return ['delimited','(',')',*nodes]

    def para(doc,text,style=None):return doc.add_paragraph(text,style=style)
    def heading(doc,text):doc.add_heading(text,level=1)
    def page(doc,title):doc.add_page_break();heading(doc,title)
    def figure(doc,path,caption,width=6.35):
        p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(path),width=Inches(width))
        p.paragraph_format.keep_with_next=True
        p=doc.add_paragraph(caption,style='Caption');p.paragraph_format.keep_together=True
    def table(doc,headers,rows,widths):
        t=doc.add_table(rows=1,cols=len(headers));t.alignment=WD_TABLE_ALIGNMENT.CENTER;t.autofit=False
        for cell,w in zip(t.columns,widths):cell.width=Inches(w)
        for c,text in zip(t.rows[0].cells,headers):c.text=str(text)
        repeat=OxmlElement('w:tblHeader');t.rows[0]._tr.get_or_add_trPr().append(repeat)
        for row in rows:
            for c,text in zip(t.add_row().cells,row):c.text=str(text)
        borders=OxmlElement('w:tblBorders')
        for name in ('top','left','bottom','right','insideH','insideV'):
            edge=OxmlElement('w:'+name);edge.set(qn('w:val'),'single');edge.set(qn('w:sz'),'4');edge.set(qn('w:color'),'D9D9D9');borders.append(edge)
        t._tbl.tblPr.append(borders)
        for ri,row in enumerate(t.rows):
            for ci,cell in enumerate(row.cells):
                cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
                tc=cell._tc.get_or_add_tcPr();margins=OxmlElement('w:tcMar')
                for side in ('top','left','bottom','right'):
                    el=OxmlElement('w:'+side);el.set(qn('w:w'),'100');el.set(qn('w:type'),'dxa');margins.append(el)
                tc.append(margins)
                if ri==0 or ri%2==0:
                    shade=OxmlElement('w:shd');shade.set(qn('w:fill'),'E8EEF4' if ri==0 else 'F7F8FA');tc.append(shade)
                for p in cell.paragraphs:
                    p.alignment=WD_ALIGN_PARAGRAPH.LEFT if ci==0 else WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_after=Pt(3)
                    for r in p.runs:r.font.size=Pt(10);r.bold=(ri==0)
        doc.add_paragraph().paragraph_format.space_after=Pt(3)
        return t

    manifests=[]
    for topology,filename in [('classic','TimeLearnerClassicAlgorithms.ru.docx'),('branch','TimeLearnerBranchAlgorithms.ru.docx')]:
        specific=content[topology];component=specific['component']
        cases=[c for c in evidence['native_n2_cases'] if c['model_spec']['branch']==(topology=='branch')]
        if len(cases)!=1:raise ValueError('one qualified native N2 case required per topology')
        case=cases[0]
        if not (case['counts']['TP']>=1 and case['counts']['TN']>=2):raise ValueError('user working criterion not met')
        doc=Document();sec=doc.sections[0]
        sec.page_width=Inches(8.5);sec.page_height=Inches(11)
        sec.top_margin=sec.bottom_margin=Inches(.75);sec.left_margin=sec.right_margin=Inches(1.)
        sec.header_distance=sec.footer_distance=Inches(.3)
        for name in ('Normal','Title','Subtitle','Heading 1','Heading 2','Caption'):
            st=doc.styles[name];st.font.name='Arial';st.font.color.rgb=RGBColor(0,0,0)
            st.font.underline=False
            st.element.get_or_add_rPr().find(qn('w:color')).attrib.pop(qn('w:themeColor'),None)
            fonts=st.element.get_or_add_rPr().get_or_add_rFonts()
            for attr in ('asciiTheme','hAnsiTheme','eastAsiaTheme','cstheme'):fonts.attrib.pop(qn('w:'+attr),None)
            fonts.set(qn('w:ascii'),'Arial');fonts.set(qn('w:hAnsi'),'Arial')
            props=st.element.find(qn('w:pPr'))
            if props is not None:
                for border in list(props.findall(qn('w:pBdr'))):props.remove(border)
        normal=doc.styles['Normal'];normal.font.size=Pt(11);normal.paragraph_format.space_after=Pt(7)
        normal.paragraph_format.line_spacing=1.12
        doc.styles['Title'].font.size=Pt(22);doc.styles['Heading 1'].font.size=Pt(16)
        doc.styles['Caption'].font.size=Pt(9.5)
        hp=sec.header.paragraphs[0];hp.text=component+'   '+edition
        for r in hp.runs:r.font.size=Pt(9)
        fp=sec.footer.paragraphs[0];fp.alignment=WD_ALIGN_PARAGRAPH.CENTER;fp.add_run('Страница ')
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');fp._p.append(field)
        doc.add_paragraph(specific['title'],style='Title')
        para(doc,edition,style='Subtitle');para(doc,supplement[topology]['lead'] if supplement else specific['lead']);para(doc,common['intro'])
        heading(doc,'Критерий включения и семейство')
        para(doc,common['qualification']);equation(doc,'Рабочий вариант  ⇔  TP ≥ 1  ∧  TN ≥ 2')
        if catalog:
            labels=supplement['case_labels']
            rows=[(labels[c['id']],*[c['counts'][k] for k in ('TP','FP','FN','TN')],
                   '1 foil в 2 режимах' if c['unique_foil_patterns']==1 else '7 разных foil')
                  for c in catalog['qualifying_examples'] if c['topology'].lower()==topology]
        else:
            rows=[('N1 калиброванный N2',2,0,0,2,'1 foil в 2 режимах')]
            if topology=='branch':rows += [('N1 Fast terminal7200',1,3,0,4,'Исходные 8 паттернов'),('N1 Fast terminal21600',1,1,0,6,'8 положений target')]
        table(doc,['Вариант','TP','FP','FN','TN','Область'],rows,[2.05,.45,.45,.45,.45,2.65])
        para(doc,supplement['family'] if supplement else common['family']);para(doc,specific['topology'])

        page(doc,'Математическая постановка')
        para(doc,common['math_intro'])
        equation(doc,sub('e','A,i'),' = ',sub('A','i'),' − ',sup(sub('A','i'),'(0)'))
        equation(doc,sub('δ','A,i'),' = ',sub('a','tol'),' + ',sub('r','tol'),' · ',absolute(sup(sub('A','i'),'(0)')))
        equation(doc,absolute(sub('e','A,i')),' ≤ ',sub('δ','A,i'))
        equation(doc,sub('e','t,i,lo'),' = ',sub('t','i,start'),' − ',sub('t','r,end'))
        equation(doc,sub('e','t,i,hi'),' = ',sub('t','i,end'),' − ',sub('t','r,start'))
        equation(doc,'max',parentheses(absolute(sub('e','t,i,lo')),', ',absolute(sub('e','t,i,hi'))),' ≤ ',sub('δ','t'))
        para(doc,common['math_gate']);para(doc,common['peaks'])
        equation(doc,sub('L','min,i'),' ≤ ',sub('L','i'),' ≤ ',sub('L','max,i'),';   ',sub('L','i'),' ∈ ℕ')
        equation(doc,sub('R','min,i'),' ≤ ',sub('R','s,i'),' ≤ ',sub('R','max,i'),';   ',sub('R','s,i'),' > 0')
        equation(doc,sub('N','min,i'),' ≤ ',sub('N','s,i'),' ≤ ',sub('N','max,i'),';   ',sub('N','s,i'),' ∈ ℕ')
        para(doc,specific['differences'])

        if supplement:
            page(doc,'Назначение пика обучающему импульсу')
            for text in supplement['measurement_detail']:para(doc,text)
            equation(doc,'N = 4  ⇒  N + 2 = 6 native проб')
            equation(doc,sub('S','b'),' = множество необходимых импульсов вершины b')
            equation(doc,'b ∈ ',sub('K','i'),'  ⇒  ',sub('S','b'),' = {i}')
            equation(doc,'Выбранная амплитуда = max',parentheses('A(b), b ∈ ',sub('K','i')))
            para(doc,'Последняя запись действует только после проверок неоднозначности, clipping и повторяемости. Она не разрешает выбирать общий максимум без установленной принадлежности.')

        page(doc,'Общий ход обучения')
        figure(doc,shared_flow,'Блок схема общего контура. Повтор распределён по native ticks; полный расчёт не вызывается из контроллера.',6.15)
        para(doc,'Остановка по бюджету или invalid observation сохраняет собственную причину. Свежая финальная проверка не обходится флагом готовности активного входа.')

        page(doc,'Детальный ход и варианты нормализации')
        for line in common['pseudocode']:
            p=para(doc,line);p.paragraph_format.space_after=Pt(3)
            for run in p.runs:run.font.name='Courier New';run.font.size=Pt(9.5)
        para(doc,common['n1']);para(doc,supplement['n0_intro'] if supplement else common['n0']);para(doc,common['statuses'])

        if supplement and topology=='classic':
            page(doc,'Целочисленная нормализация N0')
            for text in supplement['n0_detail']:para(doc,text)
            equation(doc,sub('A','i'),' = A',parentheses(sub('L','i'),', ',sub('N','s,i'),'; эффективная модель'))
            equation(doc,sub('N','s,i'),' ∈ ℕ;   ',sub('N','min,i'),' ≤ ',sub('N','s,i'),' ≤ ',sub('N','max,i'))
            equation(doc,'max',parentheses(sub('A','i,1'),', …, ',sub('A','i,k')),' − min',parentheses(sub('A','i,1'),', …, ',sub('A','i,k')),
                     ' = разброс повторов')
            para(doc,'Разброс — дополнительная характеристика. Допуски должны выполняться для каждого объявленного повтора; усреднение не заменяет валидность отдельных измерений.')
            page(doc,'Поиск кандидата N0')
            figure(doc,n0_flow(),'Вложенная блок схема раскрывает узел поиска общего контура. Переход к следующему кандидату не подтверждает сходимость.',6.15)
            para(doc,'UML общей службы ниже применима к N0 и N1: меняются нормализуемая переменная и политика кандидатов, а владение физикой и порядок scheduler остаются общими.')

        page(doc,'Структура компонентов')
        figure(doc,classes(component),'UML классов. Чёрный ромб обозначает композицию; белый ромб соответствует shared ownership поиска. Пунктир показывает зависимость адаптера.',6.35)
        para(doc,common['ownership'])
        para(doc,'Обе топологии используют NPulseNeuron с разной структурной конфигурацией. Режим learner StructureBuildMode 0/1 не смешивается с режимами 0/1/2 вложенного нейрона.')

        page(doc,'Один шаг расчёта Rdk')
        figure(doc,shared_sequence,'UML последовательности. learner — соответствующий TimeLearner; service — NativeTrainingService; probe — NativeProbeExecutor. Показан поддержанный native вычислительный порядок.',6.35)
        para(doc,common['lifecycle']);para(doc,'Reset физического поддерева не равен Reset всего learner. Контрольный Reset и retarget имеют разные назначения; Copy и Alloc не используются как полный динамический checkpoint.')

        page(doc,'Подтверждённый пример работы')
        para(doc,content['classic']['example'])
        para(doc,'Далее приведены четыре наблюдения N2 для '+component+'. Их нельзя смешивать с восьмипаттерновой матрицей N4.')
        rows=[]
        for observation in case['observations']:
            spikes=observation['spike_times'];stimuli=observation['stimulus_times']
            rows.append((observation['trial_id'],observation['label'],
                         f'{1000*(stimuli[-1]-stimuli[0]):.1f}',len(spikes),
                         'нет' if not spikes else f'{1000*(spikes[0]-stimuli[-1]):.1f}'))
        table(doc,['Проба','Метка','Между входами мс','Спайков','От последнего входа мс'],rows,[.8,.85,1.35,.85,2.15])
        para(doc,'Target имеет интервалы [0.01, 0.03] с, то есть второй импульс через 30 мс после первого. Foil_dispersed имеет разнесение 240 мс. В примере target вызвал native spike через 8.0–8.5 мс после последнего входа; оба отрицательных наблюдения молчат.')
        para(doc,'Два TN — два предъявления одного уникального foil. Использованы reset_per_trial и preserve_neuron_dynamics. Раздельные полные окна не являются проверкой непрерывного потока без пропусков.')
        para(doc,common['test'])
        if topology=='branch':
            page(doc,'Сравнение вариантов N4')
            para(doc,specific['example'])
            table(doc,['Вариант','Порог','TP','FP','TN','Время target с'],[
                ('Fast terminal7200','0.05600905',1,3,4,'0.2535'),
                ('Fast terminal21600','0.05435379',1,1,6,'0.4930')
            ],[2.05,1.05,.5,.5,.5,1.4])
            para(doc,'Последний вход целевого паттерна приходится на 0.4900 с. В terminal7200 спайк раньше последнего входа: этот результат включён по историческому окну ответа, но показывает чувствительность к префиксу. В terminal21600 целевой спайк появляется после последнего входа. Молчание foil проверяется на полном окне, а не только вблизи предполагаемой вершины.')
            para(doc,'Во frozen-проверке 64 предъявлений модель и порог terminal21600 сохранены. В каждой из восьми перестановок получены TP=1 FP=1 FN=0 TN=6; ложный ответ сохраняется на phasea-row-4. Это восемь порядков одной модели, а не восемь независимых обучений. Базовые восемь записанных волн Elder совпали с M40 с максимальной абсолютной разностью 0.0; равенство всех последующих волн этим не утверждается.')
        para(doc,supplement[topology]['conclusion'] if supplement else specific['conclusion'])

        if supplement:
            for section in supplement[topology]['sections']:
                page(doc,section['title'])
                for text in section['paragraphs']:para(doc,text)
                if 'table' in section:
                    spec=section['table'];table(doc,spec['headers'],spec['rows'],spec['widths'])
                for text in section.get('after_table',[]):para(doc,text)

        page(doc,'Границы вывода и обновление')
        para(doc,supplement['limits'] if supplement else common['limits']);para(doc,common['history']);para(doc,common['update'])
        page(doc,'Источники этой редакции')
        for text in [
            'PulseLib '+evidence['algorithm_code']['PulseLib'],
            'Rdk '+evidence['algorithm_code']['Rdk'],
            'Runtime научных данных использует PulseLib '+evidence['algorithm_code']['science_runtime_PulseLib'],
            'Эквивалентность Core runtime и принятого PulseLib проверена для исходного N2 контроля; исторические варианты имеют собственные версии.' if catalog else 'Core runtime и принятого PulseLib равны по проверенной source closure.',
            'Формулы: Core/TimeLearner/BoundedTraining.cpp и FinalVerification.cpp.',
            'Управление: NativeTrainingService и NativeLearnerLifecycle; наблюдения: NativeProbeExecutor.',
            'Рабочий N2 model revision '+case['model_revision'],
            'N2 source — прошедший NativeCalibratedState control. Полный исходный 14-case suite имеет 8 исключённых legacy threshold precondition failures; выбранный случай и его frozen observations проверены отдельно.',
            'Полные идентификаторы, hashes, scope и ссылки на primary находятся в evidence-register.json рядом с поддерживаемыми источниками.',
            'N4 источники: FastN1RecognitionScientificReport, FastN1FullTrainingRecognitionScientificReport и FastN1FrozenOrderScientificReport от16 ноября2026.' if topology=='branch' else
            'Результаты N2 не следует сравнивать по доле правильных ответов с N4 как равные научные дизайны.'
        ]:
            p=para(doc,text)
            for r in p.runs:r.font.size=Pt(9.5)
        if catalog:
            para(doc,'Дополнения основаны на датированной сверке опубликованных отчётов и receipts. Она не заменяет независимый повторный анализ всех исторических первичных данных.')
            for c in catalog['qualifying_examples']:
                if c['topology'].lower()!=topology:continue
                text=supplement['case_labels'][c['id']]+': '+c['source']['path']+'; root '+c['source']['commit']
                p=para(doc,text)
                for r in p.runs:r.font.size=Pt(9)
            for text in supplement.get('additional_sources',[]):
                p=para(doc,text)
                for r in p.runs:r.font.size=Pt(9.5)
        path=output/filename;doc.save(path)
        manifests.append(dict(topology=topology,file=filename,bytes=path.stat().st_size,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),equation_format='native_OMML',
            render_and_visual_review_complete=False,scope='reviewed N0/N1 family and distinct legacy evidence' if catalog else 'first maintained V2 N1 edition'))
    metadata=dict(kind='timelearner_algorithm_docx_build',schema_version=1,documents=manifests,
        inputs={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in source.glob('*.json')},
        generated_binary_in_root_git=False,visual_acceptance_complete=False)
    if catalog_ref:metadata['dated_evidence_review']=catalog_ref
    (output/'build.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--review',type=Path,help='Dated reviewed example catalog for the next edition')
    args=parser.parse_args();print(json.dumps(build(args.source,args.output,args.review),ensure_ascii=False))
