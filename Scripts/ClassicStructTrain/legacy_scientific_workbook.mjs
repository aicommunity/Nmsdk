import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
process.on('uncaughtException',e=>{console.error(e.message);console.error(e.stack.split('\n').filter(s=>s.includes('legacy_scientific_workbook')).join('\n'));process.exit(1);});
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..'),work=path.join(root,'Reports/StructTrainClassic/LegacyChecks-20261123');
const out=path.join(root,'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/ScientificComparisons');
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const d=await read(path.join(work,'scientific-comparison-data.json')),a=await read(path.join(work,'assessment.json'));
const plan=await read(path.join(work,'execution-plan-data.json')),mapping=await read(path.join(work,'recovered-mapping.json'));
const wb=Workbook.create(),figures=[],previews=[];
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const palette=['#216483','#C07439','#51816C','#8B6599'];
function frame(name,title,headers,rows,widths){
 const sh=wb.worksheets.add(name);sh.showGridLines=false;const last=Math.max(6,rows.length+5),end=col(headers.length);
 sh.getRange(`A1:${end}${Math.min(last,1000)}`).format.font={name:'Arial',size:10,color:'#203343'};
 sh.getRange(`A2:${col(Math.min(8,headers.length))}2`).merge();sh.getRange('A2').values=[[title]];sh.getRange('A2').format={font:{name:'Arial',size:17,bold:true,color:'#000000'},rowHeight:48,wrapText:true};
 sh.getRange(`A5:${end}5`).values=[headers];sh.getRange(`A5:${end}5`).format={fill:'#273F57',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:48,wrapText:true};
 if(rows.length)sh.getRange(`A6:${end}${last}`).values=rows;
 sh.getRange(`A6:${end}${Math.min(last,1000)}`).format={rowHeight:25,verticalAlignment:'center',wrapText:true};
 widths.forEach((v,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${Math.min(last,1000)}`).format.columnWidth=v);
 sh.freezePanes.freezeRows(5);previews.push({sheet:sh.name,range:`A1:${col(Math.min(8,headers.length))}${Math.min(12,last)}`});return sh;
}
const catalog=frame('Научные сопоставления','Результаты старых научных опытов и их повторная оценка',
 ['Группа','Исходный опыт','Научный источник','Условия сравнения','Что действительно повторено'],
 d.cases.map(c=>[c.id,c.title,c.sources.join('\n'),c.protocol,c.status]),[12,45,70,95,95]);
catalog.getRange('A6:E12').format.rowHeight=105;
catalog.getRange('A3:E3').merge();catalog.getRange('A3').values=[['Главный результат — сравнение научных показателей. '+d.direct_figures+' прямых графиков; 3 условные осциллограммы вынесены в приложение.']];
const glossarySheet=frame('Обозначения и протоколы','Что обозначают номера входов и что с чем сравнивается',
 ['Обозначение','Определение','Применение'],[
 ['№ 51 и № 61','Номера объектов Iris в исходном порядке, оба из второго класса. Это не параметры нейрона.','Пять нормированных задержек входных спайков, с; пятый канал опорный.'],
 ['NT / NL','NNeuronTrainer / NNeuronLearner','Два архивных алгоритма структурного обучения. В этой работе обучение выключено.'],
 ['Архив','Опубликованные ответы или метрики для конкретной архивной структуры','Источник и диапазон ячеек указаны на листе соответствующего графика.'],
 ['autoPreset','Новая оценка сохранённого состояния либо реконструкции при инференсе','Та же структура и набор входов; неизвестные физические параметры взяты из указанного профиля.'],
 ['Номер состояния','Порядок снимков в старом опыте','Это не время и не число заново выполненных учебных итераций.'],
 ...d.cases.map(c=>[c.id,c.title,c.explanation])],[24,100,130]);
glossarySheet.getRange('A11:C17').format.rowHeight=70;
const ps=d.primary_source;
const primarySheet=frame('Основной структурный источник','Основной источник [1]: все 145 структурных записей и результат восстановления',
 ['Запись','ID Iris','Алгоритм','Ячейки d','Ячейки s','Исходные числа сегментов','Исходные числа синапсов','Принятые числа синапсов','Состояние','Дополнения из записей','Результат'],
 ps.rows.map(r=>[r.record,r.input_id,r.algorithm,r.length_range,r.synapse_range,r.dendrites.join(', '),r.original_synapses.map(v=>v??'нет').join(', '),r.effective_synapses?.join(', ')??'нет',r.job??'',r.donors.join(', '),r.status==='constructed'?'Полное состояние для инференса':'Недостаточно синапсов']),[15,13,14,23,23,31,43,34,32,40,38]);
primarySheet.getRange('A3:H3').merge();primarySheet.getRange('A3').values=[[ps.path+'; лист «'+ps.sheet+'». 14 полных записей, включая 5 дополненных; 131 неполная. Это источник структуры, не таблица реакций.']];primarySheet.getRange('A3').format={wrapText:true,rowHeight:45};
primarySheet.getRange('A6:K150').format.rowHeight=38;
const rawHeaders=['Эпоха отчёта','Эпоха ВКР','Арх TP','Арх FP','Арх FN','Арх TN','Повтор TP','Повтор FP','Повтор FN','Повтор TN','Арх TPR','Повтор TPR','Арх TNR','Повтор TNR','Арх BAcc','Повтор BAcc','Арх FPR','Повтор FPR','Арх FNR','Повтор FNR','Арх сумма долей','Повтор сумма долей','Арх precision','Повтор precision','Арх recall','Повтор recall','Арх Q','Повтор Q','Состояние / опубликованный P','Источник'];
const epoch=frame('Данные эпох','Схема 51→61: исходные и новые матрицы ошибок',rawHeaders,
 d.epochs.map(e=>[e.source_epoch,e.thesis_epoch,...['TP','FP','FN','TN'].map(k=>e.old[k]),...['TP','FP','FN','TN'].map(k=>e.new[k]),...Array(18).fill(null),e.job,'AG2:AI15; строка '+(e.source_epoch+1)]),rawHeaders.map((_,i)=>i<2?18:i>=28?45:17));
function metricRow(sh,r){
 sh.getRange(`K${r}:AB${r}`).formulas=[[
 `=C${r}/(C${r}+E${r})`,`=G${r}/(G${r}+I${r})`,`=F${r}/(F${r}+D${r})`,`=J${r}/(J${r}+H${r})`,`=(K${r}+M${r})/2`,`=(L${r}+N${r})/2`,
 `=D${r}/(D${r}+F${r})`,`=H${r}/(H${r}+J${r})`,`=E${r}/(E${r}+C${r})`,`=I${r}/(I${r}+G${r})`,`=Q${r}+S${r}`,`=R${r}+T${r}`,
 `=IFERROR(C${r}/(C${r}+D${r}),"")`,`=IFERROR(G${r}/(G${r}+H${r}),"")`,`=K${r}`,`=L${r}`,`=D${r}+E${r}`,`=H${r}+I${r}`]];
 sh.getRange(`K${r}:Z${r}`).setNumberFormat('0.0%');
}
for(let r=6;r<=19;r++)metricRow(epoch,r);
const base=frame('Данные среднего','51, 61 и арифметическое среднее: числовой источник',rawHeaders,
 d.baselines.map((b,i)=>[b.label,b.job,...['TP','FP','FN','TN'].map(k=>b.old[k]),...['TP','FP','FN','TN'].map(k=>b.new[k]),...Array(18).fill(null),a.baselines[i].archived.precision_source,'ВКР, таблицы 6–8']),rawHeaders.map((_,i)=>i<2?26:i>=28?45:17));
base.getRange('A5:B5').values=[['Модель','Состояние']];base.getRange('AC5').values=[['Опубликованный precision']];
for(let r=6;r<=8;r++)metricRow(base,r);
const rec=frame('Данные распознавания','Те же 22 исторических столбца, без выбора по новому качеству',rawHeaders,
 d.recognition.map(b=>[b.label,b.range,...['TP','FP','FN','TN'].map(k=>b.old[k]),...['TP','FP','FN','TN'].map(k=>b.new[k]),...Array(18).fill(null),b.job,b.mismatch_ids.join(', ')]),rawHeaders.map((_,i)=>i<2?27:i>=28?40:17));
rec.getRange('A5:B5').values=[['Структура источника','Исторический диапазон']];rec.getRange('AC5:AD5').values=[['Состояние','ID различающихся ответов']];
for(let r=6;r<=27;r++)metricRow(rec,r);
const criteria=frame('Критерии выбора','Оптимум зависит от научного критерия, как в исходном отчёте',
 ['Метрика','Экстремум','Архив: значение','Повтор: значение','Архив: первая эпоха','Повтор: первая эпоха'],d.stopping.map(c=>[c.metric,c.direction,null,null,null,null]),[20,18,24,24,28,28]);
const metricCols={TPR:['K','L'],precision:['W','X'],BAcc:['O','P'],FPR:['Q','R'],Q:['AA','AB']};
d.stopping.forEach((v,i)=>{const r=i+6,fn=v.direction.toUpperCase(),[old,fresh]=metricCols[v.metric];
 for(const [c,source] of [['C',old],['D',fresh]])criteria.getRange(`${c}${r}`).formulas=[[`=${fn}('Данные эпох'!${source}6:${source}19)`]];
 for(const [c,source] of [['E',old],['F',fresh]])criteria.getRange(`${c}${r}`).formulas=[[`=INDEX('Данные эпох'!A6:A19,MATCH(${fn}('Данные эпох'!${source}6:${source}19),'Данные эпох'!${source}6:${source}19,0))`]];
 if(v.metric!=='Q')criteria.getRange(`C${r}:D${r}`).setNumberFormat('0.0%');
});
const epochLinks={SC01:['A','K','L','M','N','O','P'],SC02:['A','Q','R','S','T','U','V'],SC03:['B','W','X','Y','Z'],SC04:['B','AA','AB']};
for(const f of d.figures){
 const name=(f.id+' '+f.sheet).slice(0,31),n=f.rows.length,end=col(f.headers.length),dense=f.kind==='line_dense';
 const sh=frame(name,f.title,f.headers,f.rows,f.headers.map((_,i)=>i===0?22:23));
 sh.getRange('A3:O3').merge();sh.getRange('A3').values=[[f.source]];sh.getRange('A3').format={wrapText:true,rowHeight:38,font:{name:'Arial',size:10,italic:true}};
 sh.getRange('A4:O4').merge();sh.getRange('A4').values=[[f.secondary?'ПРИЛОЖЕНИЕ: обучение и инференс не являются одинаковым опытом':'ПРЯМОЕ СОПОСТАВЛЕНИЕ результатов одного архивного опыта']];sh.getRange('A4').format.font={name:'Arial',size:10,bold:true,color:f.secondary?'#9A4F23':'#336D62'};
 if(!dense){
  sh.getRange(`B6:${end}${n+5}`).setNumberFormat(f.format);
  for(let i=0;i<n;i++){
   const row=i+6;
   if(epochLinks[f.id]){
    epochLinks[f.id].forEach((c,j)=>sh.getRange(`${col(j+1)}${row}`).formulas=[[`='Данные эпох'!${c}${i+6}`]]);
    if(f.id==='SC03')for(const [j,c] of [[6,'AC'],[7,'X'],[8,'Y'],[9,'Z']])sh.getRange(`${col(j)}${row}`).formulas=[[`='Данные среднего'!${c}8`]];
    if(f.id==='SC04')for(const [j,c] of [[4,'AA'],[5,'AB']])sh.getRange(`${col(j)}${row}`).formulas=[[`='Данные среднего'!${c}8`]];
   }
   if(['SC11','SC12','SC13','SC14'].includes(f.id)){
    const source=f.id==='SC11'||f.id==='SC12'?'Данные среднего':'Данные распознавания';
    const columns=f.id==='SC11'?['A','W','X','Y','Z']:f.id==='SC12'||f.id==='SC14'?['A','AA','AB']:['A','O','P'];
    columns.forEach((c,j)=>sh.getRange(`${col(j+1)}${row}`).formulas=[[`='${source}'!${c}${i+6}`]]);
   }
   if(f.id==='SC15'){
    sh.getRange(`A${row}:C${row}`).formulas=[[`='Данные эпох'!B${i+6}`,`='Данные эпох'!AA${i+6}/150`,`='Данные эпох'!AB${i+6}/150`]];
    for(const [j,r,c] of [[4,8,'AA'],[5,8,'AB'],[6,6,'AA'],[7,6,'AB'],[8,7,'AA'],[9,7,'AB']])sh.getRange(`${col(j)}${row}`).formulas=[[`='Данные среднего'!${c}${r}/150`]];
   }
  }
 }
 const ranges=f.headers.map((_,i)=>sh.getRange(`${col(i+1)}5:${col(i+1)}${n+5}`));
 const c=sh.charts.add(f.kind==='bar'?'bar':'line',ranges);c.title=f.title;c.displayBlanksAs='gap';
 const plotRow=Math.max(24,n+8),start=dense?'J6':`A${plotRow}`,finish=dense?'X29':`O${plotRow+23}`;c.setPosition(start,finish);
 c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=16;c.legend={position:'top',textStyle:{typeface:'Arial',fontSize:12}};
 c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:12},majorGridlines:null,minorGridlines:null};
 c.yAxis={min:f.minimum??0,max:f.maximum,numberFormatCode:f.format,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:12},majorGridlines:{fill:'#D7DEE5',width:.6,style:'solid'},minorGridlines:null};
 c.xAxis={title:{text:f.x_axis,textStyle:{fontSize:12,typeface:'Arial',bold:false}}};c.yAxis={title:{text:f.y_axis,textStyle:{fontSize:12,typeface:'Arial',bold:false}}};
 if(f.format==='0'&&f.maximum<=11)c.yAxis.majorUnit=1;
 if(dense){sh.getRange(`A6:A${n+5}`).setNumberFormat('0.00');c.xAxis.numberFormatCode='0.00';c.xAxis.tickLabelInterval=Math.max(1,Math.ceil(n/8));}
 c.series.items.forEach((s,i)=>{
  const color=palette[(f.kind==='bar'?i:Math.floor(i/2))%palette.length];s.fill=color;
  if(f.kind==='line_sparse'){
   s.line={fill:color,width:2,style:'dashed'};
   s.marker={symbol:i%2===0?'circle':'diamond',size:i%2===0?10:8,fill:i%2===0?'none':color,line:{fill:color,width:1.3,style:'solid'}};
  }else if(dense){s.line={fill:['#B33B39','#216483','#C07439','#51816C','#8B6599','#766046'][i%6],width:1.8,style:'solid'};s.marker={symbol:'none'};}
 });
 if(f.source_image){const bytes=await fs.readFile(f.source_image),w=bytes.readUInt32BE(16),h=bytes.readUInt32BE(20);
  sh.images.add({dataUrl:'data:image/png;base64,'+bytes.toString('base64'),anchor:{from:{row:dense?35:plotRow,col:16},extent:{widthPx:900,heightPx:900*h/w}}});}
 const foot=dense?31:plotRow+27,footStart=dense?'J':'A',footEnd=dense?'X':'O';
 sh.getRange(`${footStart}${foot}:${footEnd}${foot+2}`).merge();sh.getRange(`${footStart}${foot}`).values=[[f.description]];sh.getRange(`${footStart}${foot}:${footEnd}${foot+2}`).format={wrapText:true,font:{name:'Arial',size:10},verticalAlignment:'top'};
 figures.push({...f,rows:undefined,sheet:sh.name,index:1,range:`${start}:${finish}`,point_count:n});
}
frame('Сохранённые модели','Приложение: девять исходных согласованных моделей',
 ['Модель','ID обучения','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','TP','FP','FN','TN','Граф сохранён'],
 d.saved_models.map(m=>[m.id,m.target,...m.dendrites,...m.synapses,...['TP','FP','FN','TN'].map(k=>m.metrics[k]),true]),[14,18,...Array(14).fill(10),23]);
const recovered=await read(path.join(root,'Bin/Configs/StructTrainClassic/LegacyInference/recovered-jobs.json'));
const executionByJob=new Map([...a.saved,...a.recovered,...a.protocols,...(a.scientific_extra||[])].filter(r=>r.repeat===1).map(r=>[r.case,r]));
const inputLabel=ids=>{const groups=[];for(const id of ids){const g=groups.at(-1);if(g&&id===g[1]+1)g[1]=id;else groups.push([id,id]);}return groups.map(([x,y])=>x===y?String(x):`${x}–${y}`).join(', ');};
const scientificStates=[];
function stateRef(group,state,job,source){
 const result=a.first_by_job[job]||executionByJob.get(job);if(!result?.directory)throw new Error('Scientific state lacks native evidence: '+job);
 const physical=recovered.find(r=>r.id===job.split('-')[0])||executionByJob.get(job)||result;
 scientificStates.push([group,state,source,job,inputLabel(result.input_ids),(physical.dendrites||physical.job?.dendrites||[]).join(', '),(physical.synapses||physical.job?.synapses||[]).join(', '),result.directory]);
}
d.epochs.forEach(e=>stateRef('E01',e.source_epoch,e.job,'Схема 0 на 1+4 для 150 примеров; строка '+(e.source_epoch+1)));
for(const [source,group] of [['E019','E02'],['E020','E03']])for(const p of d.source_points[source])stateRef(group,p.state,p.job,p.source_file+'; '+p.old_cell_address);
for(const c of a.protocol_comparisons)if(['Схема 3 на 4','Схема 0 на 1'].includes(c.reference.sheet))stateRef(c.reference.sheet==='Схема 3 на 4'?'E04':'E05',c.reference.state,c.reference.job,c.reference.sheet+'!'+c.reference.source_range);
d.baselines.forEach(b=>stateRef('E06',b.label,b.job,'ВКР, таблицы 6–8'));
d.recognition.forEach(b=>stateRef('E07',b.label,b.job,'Распознавание.xlsx!'+b.range));
const stateSheet=frame('Научные состояния','Каждая научная точка связана с архивной структурой и нативным расчётом',
 ['Группа','Номер или модель','Исходная запись','Состояние расчёта','Входы','Пять длин d','Пять чисел s','Каталог нативного результата'],scientificStates,[13,23,100,44,35,32,32,110]);
stateSheet.getRange(`A6:H${scientificStates.length+5}`).format.rowHeight=42;
frame('Восстановленные состояния','Приложение: уникальные архивные геометрии, без дублирования опытов',
 ['Состояние','Алгоритм','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Конфигурация'],
 recovered.map(j=>[j.id,j.kind,...j.dendrites,...j.synapses,j.config]),[24,18,...Array(10).fill(9),110]);
const byRow=new Map(mapping.map(r=>[r.row,r]));
frame('Реестр источников','Каждая архивная структурная запись и её соответствие восстановленному состоянию',
 ['Запись','Алгоритм','Случай','Статус','Состояние','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Источник'],
 plan.restoration_rows.map(r=>{const m=byRow.get(r.id),j=recovered.find(j=>j.id===m?.job);return [r.id,r.kind,r.label,m?.status==='constructed'?'Восстановлено':'Недостаточно данных',m?.job??'',...(r.dendrites||Array(5).fill(null)),...(j?.synapses||r.synapses||Array(5).fill(null)),r.source];}),
 [14,18,50,25,25,...Array(10).fill(9),110]);
const coverage={G01:'Проекции входных данных; не результат обучения. В научные сравнения качества не включены.',G02:'Иллюстрации сигналов. Без полного исходного состояния прямое совпадение формы не утверждается.',G03:'Приложение SC16: только условное сравнение с фиксированными состояниями; динамика обучения не повторена.',G04:'Приложение SC17: только условное сравнение конечных состояний.',G05:'Приложение SC18: только условное сравнение конечных состояний.',G06:'Исторический эталон. Число учебных итераций нельзя восстановить инференсом.',G07:'Исторический эталон. Сравнение скорости требует завершённого повторного обучения.',G08:'Исторический эталон. Зависимость затрат обучения не измерена заново.',G09:'SC01: те же TPR, TNR и их полусумма.',G10:'SC02: те же FPR, FNR и сумма долей.',G11:'SC03: precision, recall и уровни среднего.',G12:'SC04: число ошибок Q и уровень среднего.',G13:'SC15: нормированная доля ошибок и три базовых состояния.',G14:'SC05–SC06: все 7 и 14 исходных точек TP из 10.',G15:'SC13–SC14: показатели качества 22 исходных столбцов.',G16:'Проверены целые d/s и полный физический граф; таблицы сохранённых и восстановленных состояний.',G17:'Контроли Reset, смены входа и загрузки выполнены. Старые ошибочные трассы не выдаются за числовой эталон.',G18:'Проверены классы компонентов и связи; иллюстративные схемы не являются числовыми опытами.'};
frame('Охват исходных графиков','Что сопоставлено для каждого семейства исходных графиков',
 ['Семейство','Исходная тема','Где в архиве','Фактически выполнено'],
 plan.families.map(f=>[f.id,f.name,f.sources,coverage[f.id]]),[14,58,85,130]);
frame('Исходные диаграммы XLSX','Все 22 различные исходные диаграммы XLSX и их сопоставление',
 ['Диаграмма','Семейство','Заголовок или оси','Файл источника','Фактически выполнено'],
 plan.charts.map(c=>[c.id,c.family,c.title||c.axis_titles.join('; '),c.source,coverage[c.family]]),[16,14,70,110,130]);
await fs.mkdir(out,{recursive:true});await fs.mkdir(path.join(work,'scientific-xlsx-qa'),{recursive:true});
wb.recalculate();
const originalTP=epoch.getRange('G6').values,originalFN=epoch.getRange('I6').values;
epoch.getRange('G6').values=[[23]];epoch.getRange('I6').values=[[27]];wb.recalculate();
const changed={canonical:epoch.getRange('L6').values,chart:wb.worksheets.getItem('SC01 51-61 TP TN').getRange('C6').values};
epoch.getRange('G6').values=originalTP;epoch.getRange('I6').values=originalFN;wb.recalculate();
await fs.writeFile(path.join(work,'scientific-formula-check.json'),JSON.stringify({changed,restored:epoch.getRange('L6').values},null,2));
const search=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!',options:{useRegex:true,maxResults:10},maxChars:1200});console.log(search.ndjson);
await fs.writeFile(path.join(work,'scientific-figures.json'),JSON.stringify(figures,null,2));
await fs.writeFile(path.join(work,'scientific-previews.json'),JSON.stringify(previews,null,2));
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'ScientificComparisons.xlsx'));console.log('Scientific workbook exported');
for(const p of previews){if(figures.find(f=>f.sheet===p.sheet)?.kind==='line_dense')continue;const blob=await wb.render({sheetName:p.sheet,range:p.range,scale:1.1,format:'png'});await fs.writeFile(path.join(work,'scientific-xlsx-qa',p.sheet.replace(/[^a-zA-Z0-9А-Яа-яЁё-]/g,'_')+'.png'),new Uint8Array(await blob.arrayBuffer()));}
