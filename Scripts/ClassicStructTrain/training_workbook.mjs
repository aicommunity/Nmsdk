import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
import {savePublishedWorkbook} from './report_paths.mjs';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const work=path.join(root,'Reports/StructTrainClassic/_work/TrainingReproducibility-20261123');
const out=path.join(root,'Reports/StructTrainClassic');
const rawData=await fs.readFile(path.join(work,'report-data.json'));
const d=JSON.parse(rawData.toString('utf8'));
const evidence=JSON.parse(await fs.readFile(path.join(root,'Reports/StructTrainClassic/_work/archive-evidence.json'),'utf8'));
const wb=Workbook.create(),figures=[];
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const palette=['#777777','#216483','#C07439','#51816C','#8B6599','#B95058'];
function sourceFor(id){
 const old={R06:'SC01',R07:'SC15',R08:'SC07',R09:'SC08',R10:'SC09',R11:'SC10',R12:'SC06',R13:'SC05',R26P:'SC03',R26R:'SC03',R27:'SC04',R28:'SC15',R29:'SC15',R30:'SC02',R31:'SC01',R35:'SC01'};
 if(old[id])return d.scientific_reference.figures.find(f=>f.id===old[id]).source;
 if(id.startsWith('R01')||id.startsWith('R02'))return path.join(root,'Docs/ClassicStructTrainExperiments/Эксперименты/Тестирование/Распознавание/Распознавание.xlsx')+'; исторические столбцы и диапазоны указаны на листе «Различия ответов».';
 if(['R03','R04','R05'].includes(id))return path.join(root,'Docs/ClassicStructTrainExperiments/ВКР_ЕременкоЕА.docx')+'; таблицы 6–8.';
 if(['R14','R15','R16','R24','R25'].some(prefix=>id.startsWith(prefix)))return path.join(root,'Docs/ClassicStructTrainExperiments/Эксперименты/Тестирование/Сравнение времени обучения разными алгоритмами/Итерации.xlsx')+'; листы холодного обучения и «Коррект. обучения НЕ с нуля (1–3)». Исходные записи сохранены в книге.';
 if(['R17','R21','R22','R23'].includes(id))return path.join(root,'Docs/ClassicStructTrainExperiments/ВКР_ЕременкоЕА.docx')+'; рисунки 15–18. Сведения об оцифровке и точности — в отчёте.';
 if(['R33','R34'].includes(id))return path.join(root,'Docs/ClassicStructTrainExperiments/Эксперименты/Исследование/код CalculateProcess.txt')+'; отношение 2/2. Конечные 13 циклов заданы планом; точная историческая числовая кривая не установлена.';
 return path.join(work,'control-analysis.json')+'; нативные журналы контролируемых вариантов.';
}
function sheet(name,title,headers,rows,widths){
 const s=wb.worksheets.add(name);s.showGridLines=false;const end=col(headers.length),last=Math.max(6,rows.length+5);
 s.getRange(`A1:${end}${last}`).format.font={name:'Arial',size:11,color:'#202020'};
 s.getRange(`A2:${col(Math.min(headers.length,8))}2`).merge();s.getRange('A2').values=[[title]];s.getRange('A2').format={font:{name:'Arial',size:17,bold:true,color:'#000000'},rowHeight:50,wrapText:true};
 s.getRange(`A5:${end}5`).values=[headers];s.getRange(`A5:${end}5`).format={fill:'#273F57',font:{name:'Arial',size:11,bold:true,color:'#FFFFFF'},rowHeight:44,wrapText:true};
 if(rows.length)s.getRange(`A6:${end}${rows.length+5}`).values=rows;
 s.getRange(`A6:${end}${last}`).format={rowHeight:27,wrapText:true,verticalAlignment:'center'};
 widths.forEach((w,i)=>s.getRange(`${col(i+1)}:${col(i+1)}`).format.columnWidth=w);s.freezePanes.freezeRows(5);return s;
}
function chart(id,title,headers,rows,{format='0',max,min=0,x='Номер сохранённого состояния',y='Число ответов, шт.',kind='line',description='',links=null,comparison='historical'}={}){
 const s=sheet(id,title,headers,rows,[28,...headers.slice(1).map(()=>20)]);const n=rows.length,end=col(headers.length);
 s.getRange('A3:O3').merge();s.getRange('A3').values=[[sourceFor(id)]];s.getRange('A3').format={wrapText:true,rowHeight:40,font:{name:'Arial',size:10,italic:true}};
 s.getRange(`B6:${end}${n+5}`).setNumberFormat(format);
 if(links)links(s);
 const ranges=headers.map((_,i)=>s.getRange(`${col(i+1)}5:${col(i+1)}${n+5}`));
 const c=s.charts.add(kind==='line_dense'?'line':kind,ranges);c.title=title;c.displayBlanksAs='gap';const row=Math.max(24,n+8);c.setPosition(`A${row}`,`O${row+24}`);
 if(kind==='line_dense')c.setPosition(`${col(headers.length+2)}6`,`${col(headers.length+16)}30`);
 c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=16;c.legend={position:'top',textStyle:{typeface:'Arial',fontSize:11}};
 c.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:11},title:{text:x,textStyle:{typeface:'Arial',fontSize:12}},majorGridlines:null,minorGridlines:null};
 c.yAxis={min,max,numberFormatCode:format,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:11},title:{text:y,textStyle:{typeface:'Arial',fontSize:12}},majorGridlines:{fill:'#D7DEE5',width:.6,style:'solid'},minorGridlines:null};
 if(format==='0'&&max<=20)c.yAxis.majorUnit=1;
 if(kind==='line_dense')c.xAxis.tickLabelInterval=Math.max(1,Math.ceil(n/9));
 c.series.items.forEach((series,i)=>{const color=palette[i%palette.length];series.fill=color;
  if(kind==='line'){series.line={fill:color,width:2,style:'dashed'};series.marker={symbol:i===0?'circle':i===1?'square':'diamond',size:i<2?10:9,fill:i<2?'none':color,line:{fill:color,width:1.3,style:'solid'}};}
  if(kind==='line_dense'){series.line={fill:color,width:1.8,style:'solid'};series.marker={symbol:'none'};}
 });
 figures.push({id,sheet:s.name,title,index:1,x_axis:x,y_axis:y,point_count:n,kind,description,format,min,max,comparison,expected_rows:links?null:rows});return s;
}
sheet('Обзор','Результаты повторной проверки исторического обучения',
 ['Показатель','Получено','Смысл'],[
 ['Новые попытки обучения с нуля',d.summary.cold_attempts,'Включая три реальных повтора и отдельный средний вход'],
 ['План попыток обучения с нуля',903,'NT/NL на 150 объектах и средний вход NL; совпадающие этапы повторно не запускаются'],
 ['Полные инференсы новых состояний',d.summary.full_inferences_available,'Повторное использование только при доказанном совпадении физических условий'],
 ['Контроли собственного входа',d.summary.own_checks_available,'Проверяются отдельно от качества всего класса'],
 ['Проверки между циклами обучения',d.summary.in_protocol_evaluations,'Сохраняют ход времени и состояние исторической процедуры'],
 ['Номера 51 и 61','Объекты Iris','Оба относятся ко второму классу; это не параметры нейрона'],
 ['NT и NL','NNeuronTrainer / NNeuronLearner','Алгоритмы структурного обучения'],
 ['История / предыдущая проверка / новое обучение','Три группы данных','Исторический результат не объявляется единственно верным'],
 ['Совпадение структуры','Отдельная характеристика','Не является обязательным условием подтверждения нового обучения']],[48,30,105]);
const recoRows=d.recognition.map(r=>{const n=r.new?.runs.find(r=>r.metrics);return [r.label,...['TP','FP','FN','TN'].map(k=>r.historical[k]??null),...['TP','FP','FN','TN'].map(k=>r.previous[k]??null),...['TP','FP','FN','TN'].map(k=>n?.metrics[k]??null),r.new?.repeats??0,null,null,null,null,null,null,r.new?.structural_variants??null];});
const reco=sheet('Распознавание','Сопоставимые исторические столбцы на всех 150 входах',
 ['Алгоритм и объект','Ист TP','Ист FP','Ист FN','Ист TN','Прошл TP','Прошл FP','Прошл FN','Прошл TN','Новый TP','Новый FP','Новый FN','Новый TN','Повторов','Ист BAcc','Прошл BAcc','Новый BAcc','Ист Q','Прошл Q','Новый Q','Вариантов структуры'],recoRows,[24,...Array(12).fill(12),12,...Array(6).fill(18),21]);
for(let i=0;i<recoRows.length;i++){const r=i+6;reco.getRange(`O${r}:T${r}`).formulas=[[
 `=(B${r}/(B${r}+D${r})+E${r}/(E${r}+C${r}))/2`,`=(F${r}/(F${r}+H${r})+I${r}/(I${r}+G${r}))/2`,
 `=IF(COUNT(J${r}:M${r})=4,(J${r}/(J${r}+L${r})+M${r}/(M${r}+K${r}))/2,"")`,
 `=C${r}+D${r}`,`=G${r}+H${r}`,`=IF(COUNT(J${r}:M${r})=4,K${r}+L${r},"")`]];}
reco.getRange(`O6:Q${recoRows.length+5}`).setNumberFormat('0.00%');
for(const [prefix,algorithm] of [['NT','NNeuronTrainer'],['NL','NNeuronLearner']]){
 const selected=recoRows.map((r,i)=>({r,i})).filter(({r})=>r[0].startsWith(prefix));
 chart('R01'+prefix,'Распознавание после обучения '+prefix,['Модель','История','Предыдущая проверка','Новое обучение'],selected.map(({r})=>[r[0],null,null,null]),
  {kind:'bar',format:'0%',max:1,x:'Обучающий объект Iris для '+algorithm,y:'Сбалансированная точность, %',description:'Архивные альтернативы NT64 и NL129 имеют собственные подписи. Новая серия для одного ID не считается двумя независимыми опытами.',links:s=>{selected.forEach(({r,i},j)=>s.getRange(`B${j+6}:D${j+6}`).formulas=[[`='Распознавание'!O${i+6}`,`='Распознавание'!P${i+6}`,`='Распознавание'!Q${i+6}`]]);}});
 chart('R02'+prefix,'Ошибки после обучения '+prefix,['Модель','История','Предыдущая проверка','Новое обучение'],selected.map(({r})=>[r[0],null,null,null]),
  {kind:'bar',max:100,x:'Обучающий объект Iris для '+algorithm,y:'Ошибки Q из 150, шт.',description:'Q=FP+FN. Отсутствующий новый инференс остаётся пустым, а не нулевым.',links:s=>{selected.forEach(({r,i},j)=>s.getRange(`B${j+6}:D${j+6}`).formulas=[[`='Распознавание'!R${i+6}`,`='Распознавание'!S${i+6}`,`='Распознавание'!T${i+6}`]]);}});
}
const meanRows=d.scientific_reference.baselines.map(b=>{const target=b.label==='51'?51:b.label==='61'?61:0;const n=d.models.find(r=>r.kind==='learner'&&r.target===target)?.runs.find(r=>r.metrics);return [target?`№ ${target}`:'Средний вход',...['TP','FP','FN','TN'].map(k=>b.old[k]),...['TP','FP','FN','TN'].map(k=>b.new[k]),...['TP','FP','FN','TN'].map(k=>n?.metrics[k]??null)];});
const mean=sheet('Два отдельных входа','Обучение № 51, № 61 и их среднему',['Объект','Ист TP','Ист FP','Ист FN','Ист TN','Прошл TP','Прошл FP','Прошл FN','Прошл TN','Новый TP','Новый FP','Новый FN','Новый TN','Ист P','Прошл P','Новый P','Ист R','Прошл R','Новый R','Ист Q','Прошл Q','Новый Q'],meanRows.map(r=>[...r,...Array(9).fill(null)]),[25,...Array(21).fill(15)]);
meanRows.forEach((v,i)=>{const r=i+6;mean.getRange(`N${r}:V${r}`).formulas=[[
 `=B${r}/(B${r}+C${r})`,`=F${r}/(F${r}+G${r})`,`=IF(COUNT(J${r}:M${r})=4,J${r}/(J${r}+K${r}),"")`,
 `=B${r}/(B${r}+D${r})`,`=F${r}/(F${r}+H${r})`,`=IF(COUNT(J${r}:M${r})=4,J${r}/(J${r}+L${r}),"")`,
 `=C${r}+D${r}`,`=G${r}+H${r}`,`=IF(COUNT(J${r}:M${r})=4,K${r}+L${r},"")`]];});mean.getRange('N6:S8').setNumberFormat('0.00%');
for(const [id,title,columns,max,format,y] of [['R03','Точность положительного ответа',['N','O','P'],1,'0%','Precision, %'],['R04','Полнота распознавания',['Q','R','S'],1,'0%','Recall, %'],['R05','Число ошибок для двух входов и среднего',['T','U','V'],60,'0','Ошибки Q из 150, шт.']])
 chart(id,title,['Объект','История','Предыдущая проверка','Новое обучение'],meanRows.map(r=>[r[0],null,null,null]),{kind:'bar',max,format,x:'Обучающий объект',y,description:'Средний вход — покомпонентное среднее задержек объектов № 51 и № 61.',links:s=>meanRows.forEach((r,i)=>s.getRange(`B${i+6}:D${i+6}`).formulas=[columns.map(c=>`='Два отдельных входа'!${c}${i+6}`)])});
const primary=d.protocol_evaluations.filter(r=>r.repeat===1);
const warm=d.warm_comparisons??[];
if(warm.length){
 const sums=[1,2,3].map(repeat=>{const rs=warm.filter(r=>r.repeat===repeat);return ['Повтор '+repeat,rs.reduce((a,r)=>a+r.old.iterations,0),rs.every(r=>r.new)?rs.reduce((a,r)=>a+r.new.iterations,0):null];});
 chart('R24','90 переходов переобучения: число итераций',['Повтор','История','Новое обучение'],sums,{kind:'bar',max:Math.ceil(Math.max(...sums.flatMap(r=>r.slice(1)).filter(Number.isFinite))/100)*100,x:'Независимый повтор всей последовательности',y:'Сумма учебных итераций 90 переходов, шт.',description:'Сопоставлена одна документированная последовательность с теми же 90 направленными переходами, по три повтора. Начальное холодное обучение сюда не включено.'});
 const ids=[...new Set(warm.map(r=>r.from_id))].sort((a,b)=>a-b),median=xs=>{if(!xs.length)return null;const s=xs.toSorted((a,b)=>a-b),m=Math.floor(s.length/2);return s.length%2?s[m]:(s[m-1]+s[m])/2;};
 const rows=ids.map(id=>{const rs=warm.filter(r=>r.from_id===id);return ['Из № '+id,median(rs.map(r=>r.old.iterations)),rs.every(r=>r.new)?median(rs.map(r=>r.new.iterations)):null];});
 chart('R25','Итерации переобучения по исходному объекту',['Исходный объект','История','Новое обучение'],rows,{kind:'bar',max:Math.ceil(Math.max(...rows.flatMap(r=>r.slice(1)).filter(Number.isFinite))/5)*5,x:'Объект перед направленным переходом',y:'Медиана числа итераций, шт.',description:'Для каждого исходного объекта объединены девять разных целей и три повтора одной документированной последовательности. Медиана характеризует эти переходы; она не является оценкой независимых выборок Iris. Все 270 исходных и новых строк представлены отдельно.'});
}
function newScheme(name,index){return primary.find(r=>r.job.scheme===name&&(r.stage_index===0?1:r.job.stages[r.stage_index-1].source_state_index)===index);}
function rate(r,key){if(!r)return null;const {TP,FP,FN,TN}=r;if(key==='precision')return TP+FP?TP/(TP+FP):null;if(key==='recall')return TP+FN?TP/(TP+FN):null;if(key==='FPR')return TN+FP?FP/(TN+FP):null;if(key==='FNR')return TP+FN?FN/(TP+FN):null;if(key==='BAcc')return TP+FN&&TN+FP?(rate(r,'recall')+TN/(TN+FP))/2:null;return (FP+FN)/(TP+FP+FN+TN);}
const meanBase=d.scientific_reference.baselines.find(b=>!['51','61'].includes(b.label));
const publishedMean=d.scientific_reference.figures.find(f=>f.id==='SC03');
const newBase=target=>d.models.find(m=>m.kind==='learner'&&m.target===target)?.runs.find(r=>r.metrics)?.metrics;
for(const [id,key,label] of [['R26P','precision','Precision'],['R26R','recall','Recall'],['R27','risk','Доля ошибок Q/150']]){
 const rows=d.scientific_reference.epochs.map((e,i)=>[i+1,rate(e.old,key),rate(e.new,key),rate(newScheme('0_1_4_full',i+1),key),key==='precision'?publishedMean.rows[i][5]:meanBase.old[key]??rate(meanBase.old,key),meanBase.new[key]??rate(meanBase.new,key),newBase(0)?.[key]??null]);
 chart(id,label+': переход 51→61 и средний вход',['Состояние','Ист переход','Прошл переход','Новый переход','Ист средний','Прошл средний','Новый средний'],rows,
 {format:'0%',max:key==='risk' ? 0.5 : 1,x:'Номер сохранённого состояния перехода 51→61',y:label+', %',description:'Точки перехода: действительное обучение с живым тестированием между циклами. Горизонтальные ориентиры среднего входа: один отдельный нейрон, испытанный общим механизмом инференса после загрузки; повторение значения не является новым опытом.'+(key==='precision'?' Опубликованный исторический ориентир среднего P=0,721 сохранён с исходным округлением; из его TP/FP получается 49/68.':'')});
}
for(const [id,target] of [['R28',51],['R29',61]]){
 const base=d.scientific_reference.baselines.find(b=>b.label===String(target));
 const rows=d.scientific_reference.epochs.map((e,i)=>[i+1,rate(e.old,'risk'),rate(e.new,'risk'),rate(newScheme('0_1_4_full',i+1),'risk'),rate(base.old,'risk'),rate(base.new,'risk'),newBase(target)?.risk??null]);
 chart(id,'Ошибки перехода и отдельного обучения № '+target,['Состояние','Ист переход','Прошл переход','Новый переход','Ист № '+target,'Прошл № '+target,'Новый № '+target],rows,
 {format:'0%',max:.5,x:'Номер сохранённого состояния перехода 51→61',y:'Доля ошибок Q из 150, %',description:'Один горизонтальный ориентир соответствует одному отдельно обученному состоянию. График разделён по базовым объектам для читаемости; переходные точки используются повторно и не считаются независимыми опытами.'});
}
chart('R30','Ложные ответы и пропуски при переходе 51→61',['Состояние','Ист FPR','Ист FNR','Прошл FPR','Прошл FNR','Новый FPR','Новый FNR'],d.scientific_reference.epochs.map((e,i)=>[i+1,...[e.old,e.new,newScheme('0_1_4_full',i+1)].flatMap(r=>[rate(r,'FPR'),rate(r,'FNR')])]),
 {format:'0%',max:1,x:'Номер состояния перехода 51→61',y:'Ошибка внутри соответствующего класса, %',description:'FPR=FP/100, FNR=FN/50. Их сумма не является долей ошибок Q/150, поскольку знаменатели различаются. Компоненты показаны раздельно, исходные агрегаты доступны в таблице полного перехода.'});
chart('R31','Сбалансированная точность перехода 51→61',['Состояние','История','Предыдущая проверка','Новое обучение'],d.scientific_reference.epochs.map((e,i)=>[i+1,...[e.old,e.new,newScheme('0_1_4_full',i+1)].map(r=>rate(r,'BAcc'))]),
 {format:'0%',max:1,x:'Номер состояния перехода 51→61',y:'BAcc=(TPR+TNR)/2, %',description:'Историческая полусумма долей верных ответов сопоставлена с той же величиной в предыдущем инференсе и новом обучении. Это баланс чувствительности и специфичности, а не общая доля верных ответов.'});
chart('R35','Новые переходные состояния: живой и общий инференс',['Состояние','История','Предыдущая проверка','Новый живой','Новый после загрузки'],d.scientific_reference.epochs.map((e,i)=>{const r=newScheme('0_1_4_full',i+1);return [i+1,rate(e.old,'BAcc'),rate(e.new,'BAcc'),rate(r,'BAcc'),r?.common_reference?.metrics_full.BAcc??null];}),
 {format:'0%',max:1,x:'Номер состояния перехода 51→61',y:'Сбалансированная точность BAcc, %',description:'В обоих новых рядах одни и те же фактически обученные снимки. Живой ряд сохраняет время, остаточную активность и порядок протокола; загруженный ряд измерен общим контрольным механизмом на тех же 150 входах. Контексты различаются несколькими условиями, поэтому это не изолированный эффект сохранения файла.'});
sheet('Переход все показатели','Полные метрики каждой группы на 14 состояниях',['Состояние','Группа','TP','FP','FN','TN','Precision','Recall','BAcc','Q','Q/150','FPR','FNR','FPR+FNR'],d.scientific_reference.epochs.flatMap((e,i)=>[['История',e.old],['Предыдущая проверка',e.new],['Новое обучение',newScheme('0_1_4_full',i+1)]].map(([label,r])=>[i+1,label,...['TP','FP','FN','TN'].map(k=>r?.[k]??null),rate(r,'precision'),rate(r,'recall'),rate(r,'BAcc'),r?r.FP+r.FN:null,rate(r,'risk'),rate(r,'FPR'),rate(r,'FNR'),r?rate(r,'FPR')+rate(r,'FNR'):null])),[20,35,...Array(4).fill(12),20,20,20,12,18,18,18,25]);
for(const [id,key,max] of [['R33','TP',11],['R34','FP',20]]){
 const rows=Array.from({length:14},(_,i)=>[i+1,...[1,2,3].map(repeat=>d.protocol_evaluations.find(r=>r.repeat===repeat&&r.job.scheme==='2_2'&&(r.stage_index===0?1:r.job.stages[r.stage_index-1].source_state_index)===i+1)?.[key]??null)]);
 chart(id,'Последовательность 2/2: '+(key==='TP'?'верные ответы':'ложные ответы'),['Состояние','Повтор 1','Повтор 2','Повтор 3'],rows,{max,x:'Контрольное состояние заданной последовательности',y:key+' из '+(key==='TP'?10:20)+', шт.',comparison:'reconstruction',description:'Новые измерения трёх повторов; историческая числовая кривая не установлена. Выполнены 13 дополнительных циклов по явно указанному плану. Наложенные линии означают совпадение повторов, а не отсутствие измерения.'});
}
sheet('Все последовательности','Каждое измерение между циклами во всех схемах',['Схема','Повтор','Этап','Размер выборки','TP','FP','FN','TN','Precision','Recall','BAcc','Q','Q/N','Обучение выключено','Структура неизменна','Данные'],d.protocol_evaluations.map(r=>[r.job.scheme,r.repeat,r.stage_index,r.TP+r.FP+r.FN+r.TN,r.TP,r.FP,r.FN,r.TN,rate(r,'precision'),rate(r,'recall'),rate(r,'BAcc'),r.FP+r.FN,rate(r,'risk'),r.training_disabled,r.structure_unchanged,r.directory]),[32,12,12,25,...Array(4).fill(12),20,20,20,12,20,30,30,110]);
sheet('Контекст снимков','Живые измерения и инференс тех же снимков после загрузки',['Схема','Повтор','Этап','Живые TP','Живые FP','Живые FN','Живые TN','Загруж TP на тех же ID','Загруж FP на тех же ID','Загруж FN на тех же ID','Загруж TN на тех же ID','Различий ответов','ID различий','Контекст сравнения','Общий инференс'],d.protocol_evaluations.map(r=>[r.job.scheme,r.repeat,r.stage_index,r.TP,r.FP,r.FN,r.TN,...['TP','FP','FN','TN'].map(k=>r.common_reference?.metrics_same_ids[k]??null),r.common_reference?.live_mismatch_ids.length??null,r.common_reference?.live_mismatch_ids.join(', ')??'',r.common_reference?.scope??'нет измерения',r.common_reference?.source??'']),[32,12,12,...Array(4).fill(18),...Array(4).fill(32),24,80,120,110]);
const oldFig=id=>d.scientific_reference.figures.find(f=>f.id===id);
for(const [id,old,name,title,key,max,y] of [
 ['R06','SC01','0_1_4_full','Верные ответы при переходе от № 51 к № 61','rates',1,'Доля верных ответов внутри класса, %'],
 ['R07','SC15','0_1_4_full','Ошибки при переходе от № 51 к № 61','Q',.5,'Ошибки Q из 150, %'],
 ['R08','SC07','3_4','Три итерации для № 51 и четыре для № 61','TP',11,'Верные ответы TP из 10, шт.'],
 ['R09','SC08','3_4','Ложные ответы при чередовании двух входов','FP',20,'Ложные ответы FP из 20, шт.'],
 ['R10','SC09','0_1','Последовательные одиночные итерации для № 61','TP',11,'Верные ответы TP из 10, шт.'],
 ['R11','SC10','0_1','Ложные ответы после одиночных итераций','FP',20,'Ложные ответы FP из 20, шт.'],
 ['R12','SC06','0_1_4_subset','Дополнительная настройка синапсов на № 61','TP',11,'Верные ответы TP из 10, шт.'],
 ['R13','SC05','preliminary_1_4','Предварительная схема и явные реконструкции','TP',11,'Верные ответы TP из 10, шт.']]){
 const source=oldFig(old);let headers=['Состояние','История','Предыдущая проверка','Новое обучение'];
 const rows=source.rows.map((row,i)=>{const state=i+1,n=newScheme(name,state);return [state,row[1],row[2],n?(key==='Q'?(n.FP+n.FN)/150:key==='rates'?n.TP/(n.TP+n.FN):n[key]):null];});
 if(key==='rates'){
  headers=['Состояние','Ист TPR','Ист TNR','Прошл TPR','Прошл TNR','Новое TPR','Новое TNR'];
  for(let i=0;i<rows.length;i++){const e=d.scientific_reference.epochs[i],n=newScheme(name,i+1);rows[i]=[i+1,e.old.TPR,e.old.TNR,e.new.TPR,e.new.TNR,n?n.TP/(n.TP+n.FN):null,n?n.TN/(n.TN+n.FP):null];}
 }
 if(id==='R13'){headers.push('Реконструкция 2+4');rows.forEach((r,i)=>r.push(newScheme('preliminary_2_4',i+1)?.TP??null));}
 chart(id,title,headers,rows,{max,format:key==='rates'||key==='Q'?'0%':'0',x:'Номер состояния в исходном опыте',y,description:id==='R13'?'Порядок исходной предварительной программы не восстановлен однозначно. Две новые линии — отдельно обозначенные реконструкции.':'Новые точки получены в ходе обучения с тестированием между циклами; результаты прежней проверки относятся к архивным состояниям.'});
}
const coldRows=d.models.flatMap(m=>m.runs.map(r=>[r.label,r.kind,r.target,r.repeat,r.status,r.native_stopped,r.initialized,r.own_answer??null,r.iterations,...r.dendrites,...r.synapses,r.metrics?.BAcc??null,r.metrics?.Q??null,r.directory]));
sheet('Новые состояния','Каждая попытка обучения и её проверяемый результат',['Модель','Алгоритм','ID','Повтор','Статус','Штатная остановка','Граф инициализирован','Собственный вход','Итераций','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','BAcc','Q','Нативные данные'],coldRows,[25,17,9,10,36,20,23,22,14,...Array(10).fill(9),15,12,110]);
sheet('Качество по классам','Новые модели; классы обучающих объектов учитываются раздельно',['Алгоритм','Класс обучающего объекта','Моделей измерено','План моделей','Медиана BAcc','Минимум BAcc','Максимум BAcc','Медиана Q'],(d.cohort_performance??[]).map(r=>[r.kind==='trainer'?'NT':'NL',r.target_class,r.models_measured,r.models_planned,r.median_BAcc,r.min_BAcc,r.max_BAcc,r.median_Q]),[22,35,26,25,25,25,25,22]);
wb.worksheets.getItem('Качество по классам').getRange('E6:G11').setNumberFormat('0.00%');
sheet('Все метрики новых состояний','Полный проход 150 входов для каждой завершённой попытки',['Модель','Повтор','Статус обучения','TP','FP','FN','TN','Precision','Recall','BAcc','Q','Доля ошибок','Собственный вход','Источник инференса'],d.models.flatMap(m=>m.runs.map(r=>[r.label,r.repeat,r.status,...['TP','FP','FN','TN','precision','recall','BAcc','Q','risk'].map(k=>r.metrics?.[k]??null),r.own_answer??null,r.inference_source??'Не выполняется для незавершённого обучения / ожидается'])),[28,12,37,...Array(4).fill(12),20,20,20,12,23,25,130]);
wb.worksheets.getItem('Все метрики новых состояний').getRange('H6:J908').setNumberFormat('0.00%');wb.worksheets.getItem('Все метрики новых состояний').getRange('L6:L908').setNumberFormat('0.00%');
sheet('Различия ответов','Какие именно входы дали разные бинарные ответы',['Модель источника','Исходные ячейки','История и новое число','История и новое ID','Прошлая и новое число','Прошлая и новое ID','Прежний нативный журнал ответов и физических сигналов'],
 d.recognition.map(r=>[r.label,r.source_range,r.historical_new_mismatch_ids?.length??null,r.historical_new_mismatch_ids?.join(', ')??'нет измерения',r.previous_new_mismatch_ids?.length??null,r.previous_new_mismatch_ids?.join(', ')??'нет измерения',r.previous_native_source??'нет измерения']),[24,24,28,110,30,110,110]);
sheet('Бинарные ответы','Те же 150 объектов в исходном порядке',['Модель источника','ID тестового объекта','Класс объекта','Исторический ответ','Предыдущая проверка','Новое обучение первый завершённый повтор','Пик сом прошлый мВ','Пик сом новый мВ','Δ пика мВ','Первая реакция прошлая с','Первая реакция новая с'],
 d.recognition.flatMap(r=>Array.from({length:150},(_,i)=>{const a=r.previous_peaks_V?.[i],b=r.new_peaks_V?.[i];return [r.label,i+1,Math.floor(i/50)+1,r.historical_answers?.[i]??null,r.previous_answers?.[i]??null,r.new_answers?.[i]??null,a==null?null:a*1000,b==null?null:b*1000,a==null||b==null?null:(b-a)*1000,r.previous_first_spikes_seconds?.[i]??null,r.new_first_spikes_seconds?.[i]??null];})),[27,25,18,25,27,42,27,27,25,30,30]);
wb.worksheets.getItem('Бинарные ответы').getRange('G6:K3305').setNumberFormat('0.000000');
wb.worksheets.getItem('Бинарные ответы').getRange('A3:K3').merge();wb.worksheets.getItem('Бинарные ответы').getRange('A3').values=[['Физические сигналы сравнивают предыдущую проверку и новое обучение одним механизмом инференса. Исторические 150 ответов не содержат таких амплитуд и времён. Пустое время при ответе 0 означает отсутствие срабатывания. Пик — сумма сом, не LTZone.']];wb.worksheets.getItem('Бинарные ответы').getRange('A3').format={wrapText:true,rowHeight:42};
const totals=[];
for(const m of d.models.filter(m=>[22,37,45,60,64,84,90,111,129,134].includes(m.target))){
 const old=evidence.cold.filter(r=>r.kind===m.kind&&r.id===m.target);const mean=v=>v.length?v.reduce((a,b)=>a+b,0)/v.length:null;
 totals.push([m.label,mean(old.map(r=>r.dendrites.reduce((a,b)=>a+b,0))),mean(m.runs.map(r=>r.dendrites.reduce((a,b)=>a+b,0))),mean(old.map(r=>r.synapses.reduce((a,b)=>a+b,0))),mean(m.runs.map(r=>r.synapses.reduce((a,b)=>a+b,0)))]);
}
for(const prefix of ['NT','NL']){
 const selected=totals.filter(r=>r[0].startsWith(prefix));
 for(const [base,title,cols,y] of [['R14','Длины дендритов',[1,2],'Сумма сегментов пяти дендритов, шт.'],['R15','Числа синапсов',[3,4],'Сумма синапсов пяти каналов, шт.']]){
  const rows=selected.map(r=>[r[0],...cols.map(c=>r[c])]),max=Math.ceil(Math.max(...rows.flatMap(r=>r.slice(1)).filter(v=>v!==null))*1.1/20)*20;
  chart(base+prefix,title+' контрольной десятки '+prefix,['Модель','История','Новое обучение'],rows,{kind:'bar',max,x:'Обучающий объект Iris',y,description:'Средние трёх исторических и трёх новых попыток. Структура учитывается отдельно от завершения и распознавания.'});
 }
}
for(const [prefix,kind] of [['NT','trainer'],['NL','learner']]){
 const selected=d.models.filter(m=>m.kind===kind&&[22,37,45,60,64,84,90,111,129,134].includes(m.target));
 const rows=selected.map(m=>{const old=evidence.cold.filter(r=>r.kind===m.kind&&r.id===m.target);return [m.label,old.length?old.reduce((a,b)=>a+b.iterations,0)/old.length:null,m.mean_iterations];});
 const max=Math.ceil(Math.max(...rows.flatMap(r=>r.slice(1)).filter(v=>v!==null))*1.1/10)*10;
 chart('R16'+prefix,'Итерации обучения контрольной десятки '+prefix,['Модель','История','Новое обучение'],rows,{kind:'bar',max,x:'Обучающий объект Iris',y:'Итерации до завершения, шт.',description:'Средние трёх действительных повторов. Это число учебных итераций, а не время работы на разных компьютерах.'});
}
if(d.waveform){
 const wave=d.waveform;
 const s=chart('R17','Обучение NL111 в итерациях с шестой по десятую',['Относительное время с','Исторический график мВ','Новое обучение мВ'],wave.rows,
 {kind:'line',max:90,x:'Время относительно первого максимума, с',y:'Суммарный потенциал сом, мВ',description:wave.interpretation});
 const c=s.charts.items[0];c.setPosition('E6','S30');c.xAxis.numberFormatCode='0.00';c.xAxis.tickLabelInterval=Math.ceil(wave.rows.length/8);
 c.series.items.forEach((series,i)=>{series.line={fill:palette[i],width:1.8,style:'solid'};series.marker={symbol:'none'};});
 figures.at(-1).kind='line_dense';s.getRange(`A6:A${wave.rows.length+5}`).setNumberFormat('0.00');
}
const controls=d.controls??{};
for(const [prefix,kind] of [['NT','trainer'],['NL','learner']]){
 const rows=['V1C','FS','FD','FR','FO','V2'].map(v=>{const values=(controls.zone_comparison??[]).filter(r=>r.kind===kind&&r.variant===v);return [v,values.length?values.reduce((a,b)=>a+b.potential_mV,0)/values.length:null,11.5];});
 chart('R18'+prefix,'Потенциал зоны низкого порога после обучения '+prefix+'22',['Вариант','Пик LTZone','Фиксированный порог'],rows,
 {max:Math.ceil(Math.max(15,...rows.map(r=>r[1]??0))/5)*5,format:'0.0',x:'Изменённый код конструктора или порядок расчёта',y:'Потенциал LTZone, мВ',comparison:'diagnostic',description:'Среднее трёх повторов. FS — секреция 2 мс; FD/FR — изменены значения по умолчанию диссоциации/сопротивления, но в готовом графе они переопределены; FO — отключено явное обновление порядка; V2 — совместные исторические значения по умолчанию. Фактические значения приведены на листе «Параметры синапсов».'});
}
if(controls.stopping_trajectory){
 const tr=controls.stopping_trajectory;
 chart('R19','Влияние условия остановки NT22',['Итерация',...tr.labels],tr.rows,
 {kind:'line_dense',max:Math.ceil(Math.max(...tr.rows.flatMap(r=>r.slice(1)).filter(v=>v!==null))/50)*50,x:'Номер учебной итерации',y:'Сумма синапсов пяти каналов, шт.',comparison:'diagnostic',description:'Показаны реальные траектории первого повтора. Исходное условие и пересечение цели завершились; строгий амплитудный вариант достиг лимита 600 с. Пустая часть после завершения не заполняется последним значением.'});
}
const conditions=[['baseline','Исходный'],['reset','Сброс перед входом'],['native-order','Сохранённый порядок'],['order-disabled','Обновление отключено']];
for(const [id,model,label] of [['R20','learner-22','NL22'],['R20NT','trainer-111','NT111']]){
 const engine=(controls.engine??[]).filter(r=>r.model===model);
if(conditions.every(([key])=>engine.some(r=>r.condition===key))){
 const rows=Array.from({length:150},(_,i)=>[i+1,...conditions.map(([key])=>engine.find(r=>r.condition===key).zone_peaks_V?.[i]*1000??null),11.5]);
 chart(id,'Одно состояние '+label+' в разных механизмах инференса',['ID объекта',...conditions.map(r=>r[1]),'Порог'],rows,
 {kind:'line_dense',format:'0.0',max:Math.ceil(Math.max(...rows.flatMap(r=>r.slice(1)).filter(Number.isFinite))/5)*5,x:'ID тестового объекта Iris в исходном порядке',y:'Пик потенциала LTZone, мВ',comparison:'diagnostic',description:'Во всех условиях загружается одно неизменное сохранённое состояние. Изменяется только механизм инференса или сброс перед каждым входом. Изменения обучения на этой диаграмме отсутствуют.'});
}
}
for(const wave of d.additional_waveforms??[]){
 const values=wave.rows.flatMap(r=>r.slice(1)).filter(Number.isFinite);
 const s=chart(wave.id,wave.title,['Относительное время с','Исторический график мВ','Новое обучение мВ'],wave.rows,
 {kind:'line_dense',format:'0.0',max:Math.ceil(Math.max(...values)/10)*10,x:'Время относительно первого максимума, с',y:'Суммарный потенциал сом, мВ',description:wave.interpretation});
 s.charts.items[0].xAxis.numberFormatCode='0.00';s.charts.items[0].xAxis.tickLabelInterval=Math.ceil(wave.rows.length/8);s.getRange(`A6:A${wave.rows.length+5}`).setNumberFormat('0.00');
}
if(controls.geometry_effect?.changed_ids.length){
 const effect=controls.geometry_effect;
 chart('R36','Порядок расчёта изменяет ответы одной модели NL22',['Условие',...effect.changed_ids.map(id=>'Тест № '+id)],effect.rows,
 {max:1,x:'Условие расчёта одного неизменного обученного состояния',y:'Выходной импульс: 1 — есть, 0 — нет',comparison:'diagnostic',description:'Ручной порядок → штатный → ручной повторно. Показаны конкретные изменившиеся ответы. В штатном условии совпал весь исторический вектор 150 ответов. d и s одной модели между условиями не менялись; полное историческое программное обеспечение этим не восстановлено.'});
}
if(controls.prior_order_effect?.changed_ids.length){
 const effect=controls.prior_order_effect;
 chart('R37','NL22 предыдущего отчёта: прямой обратный контроль',['Условие',...effect.changed_ids.map(id=>'Тест № '+id)],effect.rows,
 {max:1,x:'Порядок расчёта точной конфигурации предыдущего отчёта',y:'Выходной импульс: 1 — есть, 0 — нет',comparison:'diagnostic',description:'Использована прежняя конфигурация G958de87d4b9d, без нового обучения и без изменения её параметров. Ручной режим повторил ScientificComparisons; штатный порядок совпал со всеми 150 историческими ответами; повторный ручной режим восстановил прежний вектор.'});
}
sheet('Причины','Установленные эффекты и границы объяснений',['Фактор','Статус вывода','Наблюдение','Граница вывода','Источник доказательства'],d.causes.map(c=>[c.factor,c.status,c.finding,c.boundary,c.source]),[35,38,105,110,100]);
const cr=wb.worksheets.getItem('Причины');cr.getRange(`A6:E${d.causes.length+5}`).format.rowHeight=85;
sheet('Отдельные факторы','Независимые изменения параметров и порядка вычислений',['Вариант','Алгоритм','Повтор','Статус','Итераций','Длины','Синапсы','Калибровочные потенциалы В','Собственный вход','Пик суммы сом В','Пик LTZone мВ','TP','FP','FN','TN','BAcc','Нативные данные'],d.factors.map(r=>[r.variant,r.kind,r.repeat,r.status,r.iterations,r.dendrites.join(', '),r.synapses.join(', '),r.calibration?.join(', ')??'',r.own_answer,r.own_peak,r.own_zone_mV,...['TP','FP','FN','TN','BAcc'].map(k=>r.full_metrics?.[k]??null),r.directory]),[16,18,12,35,15,35,35,90,22,24,22,...Array(4).fill(12),20,110]);
sheet('Контроли инференса','Один физический граф; разные условия расчёта',['Модель','Условие','Различий ответов','ID различий','Максимум |Δ пика сом| В','Структура неизменна','Обучение выключено','Сохранение и загрузка','BAcc','Q'],(controls.engine??[]).map(r=>[r.model,r.condition,r.answer_differences.length,r.answer_differences.join(', '),r.peak_max_abs_difference_V,r.structure_unchanged,r.training_disabled,r.roundtrip_same_answer,r.metrics.BAcc,r.metrics.Q]),[24,28,24,90,32,28,27,30,20,14]);
sheet('Сброс и порог','Конкретные изменившиеся решения одного неизменного состояния',['Модель','ID входа','Ответ без сброса','Ответ со сбросом','LTZone без сброса мВ','LTZone со сбросом мВ','Запас без сброса мВ','Запас со сбросом мВ'],(controls.reset_examples??[]).map(r=>[r.model,r.input_id,r.baseline_answer,r.reset_answer,r.baseline_zone_mV,r.reset_zone_mV,r.baseline_margin_mV,r.reset_margin_mV]),[25,18,28,28,35,35,35,35]);
sheet('Живой контроль порядка','Каждая дополнительная попытка, включая ограничения',['Вариант','Алгоритм','Повтор','Статус процесса','Статус обучения','Итераций','Живые TP','Живые FP','Живые FN','Живые TN','Причина отсутствия измерения','Данные'],(controls.order_live??[]).map(r=>[r.variant,r.kind,r.repeat,r.process_status,r.training?.status??'нет наблюдения',r.training?.iterations??null,...['TP','FP','FN','TN'].map(k=>r.inference?.[k]??null),r.missing_inference_reason??'',r.directory]),[20,20,12,35,35,20,...Array(4).fill(18),120,110]);
sheet('Геометрия и инференс','Одна модель FO22 с архивными d/s в четырёх условиях',['Условие','TP','FP','FN','TN','BAcc','Q','Обучение выключено','Структура неизменна','Сохранение и загрузка','Данные'],(controls.geometry_engine??[]).map(r=>[r.condition,...['TP','FP','FN','TN','BAcc','Q'].map(k=>r.metrics[k]),r.training_disabled,r.structure_unchanged,r.roundtrip_same_answer,r.directory]),[30,...Array(4).fill(15),20,15,30,30,30,110]);
sheet('Прежняя NL22 и порядок','Тот же файл предыдущего отчёта: порядок как контролируемый фактор',['Условие','TP','FP','FN','TN','BAcc','Q','Обучение выключено','Структура неизменна','Данные'],(controls.prior_order??[]).map(r=>[r.condition,...['TP','FP','FN','TN','BAcc','Q'].map(k=>r.metrics[k]),r.training_disabled,r.structure_unchanged,r.directory]),[30,...Array(4).fill(15),20,15,30,30,110]);
sheet('Загрузка прежней NL22','Явные современные значения отсутствующих полей; известные исходные параметры сохранены',['Компонент','Параметр','В исходном файле','После загрузки','Происхождение'],(controls.prior_load_adaptations?.modern_missing_parameters??[]).map(r=>[r.node,r.parameter,'отсутствует',r.after.join(', '),'Нулевое значение зарегистрированного класса; одинаково во всех трёх контролях порядка. Историческим измерением не является.']),[55,45,30,25,110]);
sheet('Параметры синапсов','Действительные значения в сохранённом физическом графе',['Вариант','Алгоритм','Сопротивление МОм','Секреция мс','Диссоциация мс','Компонентов'],(controls.factors??[]).flatMap(r=>r.actual_synapse_profiles.map(p=>[r.variant,r.kind,p.values.Resistance[0]/1e6,p.values.SecretionTC[0]*1000,p.values.DissociationTC[0]*1000,p.count])),[20,22,30,23,26,25]);
sheet('Файловый протокол','Общие допустимые записи 22→64→111',['Протокол','Повтор','Состояний','Завершение','Общие этапы совпали физически','Итерации совпали','Максимумы совпали','Данные'],(controls.file_protocol??[]).map(r=>[r.protocol,r.repeat,r.training_records,r.end?.status??'нет финальной записи',r.comparisons.length>0&&r.comparisons.every(c=>c.same_full_physical_state),r.comparisons.length>0&&r.comparisons.every(c=>c.same_iterations),r.comparisons.length>0&&r.comparisons.every(c=>c.same_soma_maxima),r.directory]),[30,12,22,37,40,30,30,110]);
sheet('Парсер EOF','Безопасная отдельная проверка извлечения записей',['Опыт','Повтор','Статус','Полных векторов принято','Значений в неуспешном чтении','EOF до чтения','Присвоены значения модели','Данные'],(controls.parser??[]).map(r=>[r.job.id,r.repeat??null,r.status,r.records_accepted,r.failed_read_values,r.eof_before,r.model_values_assigned,r.directory]),[40,12,35,32,40,25,35,110]);
const chronologyRows=d.history.documents.flatMap(r=>r.saves?.length?r.saves.map((save,i)=>[r.path,'',save,'История сохранения XML; запись '+(i+1)+' из '+r.saves.length+'. Часовой пояс не указан.',r.sha256]):[[r.path,r.created??'',r.modified??'',r.evidence,r.sha256]]);
sheet('Хронология','Даты источников не заменяют даты запусков',['Источник','Создан','Сохранён','Свидетельство','SHA256'],chronologyRows,[110,27,50,100,70]);
const chronology=wb.worksheets.getItem('Хронология');
chronology.getRange(`B6:C${chronologyRows.length+5}`).setNumberFormat('yyyy-mm-dd hh:mm:ss');
chronology.getRange('A3:E3').merge();chronology.getRange('A3').values=[['Метаданные Office показаны в UTC. Истории XML сохранены как записаны; их часовой пояс не указан. Даты этих свидетельств не объявляются датами запуска.']];chronology.getRange('A3').format={wrapText:true,rowHeight:35};
sheet('История кода','Кандидаты на причины и контрольные изменения',['Коммит','Дата автора','Изменение','Фактор','Статус'],d.history.commits.map(r=>[r.sha,r.author_date,r.subject,r.factor,r.status]),[48,30,100,40,70]);
wb.worksheets.getItem('История кода').getRange(`B6:B${d.history.commits.length+5}`).setNumberFormat('yyyy-mm-dd hh:mm:ss');
wb.worksheets.getItem('История кода').getRange('B5').values=[['Дата автора UTC']];
const ps=d.scientific_reference.primary_source;
const variantLabels={V0:'Исходный autoPreset',V0G:'Исходный код; дополнительный такт проверки инициализации',V1:'Предварительный контроль жизненного цикла',V1C:'Инициализация; штатный завершающий такт NL',V2:'Исторические значения конструктора апреля–июня 2022',V3:'Частичный архивный цикл на профиле V2',VP:'Предварительный контроллер протоколов',VP1:'Наблюдение между циклами без смены физического алгоритма',VB:'Файловый протокол; завершение предусловия режимов; LTZone',VT:'Дополнительные осциллограммы и безопасный парсер',R0:'Возврат автоматического Init в Rdk при исходном PulseLib',FS:'SecretionTC конструктора 2 мс',FD:'DissociationTC конструктора 2 мс; фактически 5 мс',FR:'Resistance конструктора 100 МОм; фактически 86/1000 МОм',FO:'Отключён один явный UpdateComputationOrder',FZ:'Строгий амплитудный критерий без досрочного завершения',FZC:'FZ с учётом пересечения целевого потенциала'};
sheet('Варианты кода','Раздельные физические изменения и версии измерительного контроллера',['ID','Смысл','Root на момент сборки','PulseLib','Rdk','SHA256 бинарника','Сборка','Бинарник'],(d.variants??[]).map(v=>[v.id,variantLabels[v.id]??v.label,v.root_sha,v.pulselib_sha,v.rdk_sha,v.binary_sha256,v.build,v.binary]),[18,105,50,50,50,75,40,100]);
sheet('Доступность исходников','Исполняемые варианты и полнота отдельных снимков контроллера',['ID','Бинарник и SHA подтверждены','Точный снимок replay.cpp','Точный снимок inc адаптера','Патч отслеживаемых файлов','PulseLib','Rdk','Ограничение'],(d.source_availability??[]).map(r=>[r.variant,r.binary_retained_and_sha256_verified,r.controller_source_identical_snapshot??'Отдельный снимок не найден',r.training_adapter_identical_snapshot??'Отдельный снимок не найден',r.tracked_files_patch_retained,r.sdk_commit,r.rdk_commit,r.boundary]),[18,35,110,110,40,50,50,130]);
sheet('Основной источник','Основная таблица структурных параметров NT и NL',['Запись','ID Iris','Алгоритм','Ячейки длин','Ячейки синапсов','Пять длин','Исходные синапсы','Принятые синапсы','Дополнение из записей','Статус полноты'],ps.rows.map(r=>[r.record,r.input_id,r.algorithm,r.length_range,r.synapse_range,r.dendrites.join(', '),r.original_synapses.map(v=>v??'нет').join(', '),r.effective_synapses?.join(', ')??'нет',r.donors.join(', '),r.status==='constructed'?'Полное состояние предыдущей проверки':'Недостаточно чисел синапсов']),[15,12,15,25,25,35,50,40,50,45]);
sheet('Историческая десятка','Все 60 исходных записей контрольной десятки',['Случай','Повтор','ID Iris','Алгоритм','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Итераций','Итерации дендритов','Итерации синапсов','Лист и строка источника'],evidence.cold.map(r=>[r.case,r.repeat,r.id,r.kind,...r.dendrites,...r.synapses,r.iterations,r.dendrite_iterations,r.synapse_iterations,r.source.sheet+'; '+r.source.row]),[24,12,12,19,...Array(10).fill(10),14,25,25,70]);
wb.worksheets.getItem('Основной источник').getRange('A3:H3').merge();wb.worksheets.getItem('Основной источник').getRange('A3').values=[[ps.path+'; лист «'+ps.sheet+'». Источник структуры; данные реакций имеют собственные ссылки.']];wb.worksheets.getItem('Основной источник').getRange('A3').format={wrapText:true,rowHeight:48};
sheet('Основной источник и обучение','Новые состояния и все записи основного структурного источника',['Запись источника','ID Iris','Алгоритм','Источник d','Источник s','d история','s история','Происхождение s','d новое','s новое','Δd новое минус история','Δs новое минус история','Всего попыток','Первый завершённый повтор','Статус выбранного повтора','BAcc этого состояния','Дополнение','Нативные данные'],d.primary_comparisons.map(r=>[r.record,r.id,r.algorithm,r.length_range,r.synapse_range,r.old_d.join(', '),r.old_s?.join(', ')??'нет',r.s_provenance,r.new_d?.join(', ')??'нет результата',r.new_s?.join(', ')??'нет результата',r.d_delta?.join(', ')??'нет результата',r.s_delta?.join(', ')??'не сравнивается',r.new_repeats,r.new_selected_repeat,r.new_status,r.new_inference_BAcc,r.donors.join(', '),r.new_directory]),[22,12,15,23,23,36,36,42,36,36,40,40,25,32,38,30,48,110]);
wb.worksheets.getItem('Основной источник и обучение').getRange('P6:P150').setNumberFormat('0.00%');
sheet('Режимы отдельно','32 исторических случая в трёх независимых запусках',['Случай','Повтор','Строка источника','Статус','Штатное исходное завершение','Порог после переключения В','Порог соответствует режиму','Структура при распознавании','Режим после двух периодов','Нуждается в обучении','d после','s после','Архивное замечание','Данные'],d.modes.map(r=>{const a=r.after_two_periods??r.pattern_changes?.at(-1);return [r.case,r.repeat,r.source_row,r.status,r.training_precondition?r.training_precondition.is_need_to_train===false:null,r.immediate?.threshold??null,r.threshold_matches_requested_mode??null,r.recognition_structure_unchanged??null,a?.calculate_mode??null,a?.is_need_to_train??null,a?.dendrites?.join(', ')??'',a?.synapses?.join(', ')??'',r.archived_transition_note??'Серия изменений входа',r.directory];}),[22,12,22,35,35,32,33,36,36,30,35,35,95,110]);
sheet('Режимы и история','Исходные записи таблицы режимов и новые наблюдения',['Случай','Повтор','Строка источника','Исходные ячейки G–R без переинтерпретации','Новый статус','Новый порог В','Порог соответствует запросу','Структура при распознавании','Архивное замечание'],d.modes.map(r=>[r.case,r.repeat,r.source_row,r.historical_cells?Object.entries(r.historical_cells).map(([k,v])=>k+': '+(v??'пусто')).join('; '):'Серия изменений входа; четыре исходных вектора документированы в протоколе',r.status,r.immediate?.threshold??null,r.threshold_matches_requested_mode??null,r.recognition_structure_unchanged??null,r.archived_transition_note??'']),[22,12,23,150,30,25,35,35,100]);
sheet('Переобучение','Историческая последовательность 90 направленных переходов',['Повтор','Переход','ID до','ID после','Статус','Итераций','d','s','Причина завершения','Данные'],d.protocol_training.filter(r=>r.phase==='warm'&&r.stage_index).map(r=>{const seq=r.job.stages;const i=r.stage_index;return [r.repeat,i,i===1?r.job.target_id:seq[i-2].target_id,r.stage.target_id,r.status,r.iterations,r.dendrites.join(', '),r.synapses.join(', '),r.status==='completed'?'Внешняя граница режима 1 по нулевым структурным статусам':r.status,r.directory];}),[12,17,17,20,35,18,35,35,100,110]);
sheet('Переобучение и история','Каждый документированный переход: структура и число итераций',['Повтор','Переход','ID до','ID после','Ист итераций','Новых итераций','Δ итераций','d история','d новое','Δ d','s история','s новое','Δ s','Исторический лист и строка','Новые данные'],warm.map(r=>[r.repeat,r.transition,r.from_id,r.to_id,r.old.iterations,r.new?.iterations??null,r.iteration_delta,r.old.dendrites.join(', '),r.new?.dendrites.join(', ')??'',r.d_delta?.join(', ')??'',r.old.synapses.join(', '),r.new?.synapses.join(', ')??'',r.s_delta?.join(', ')??'',r.old.source.sheet+'; '+r.old.source.row,r.new?.directory??'нет результата']),[12,18,15,15,20,23,20,...Array(6).fill(38),70,110]);
const coverageBytes=await fs.readFile(path.join(work,'coverage-ledger.json'));
const coverage=JSON.parse(coverageBytes.toString('utf8'));
sheet('Полнота выполнения','Результат либо конкретная причина для всей запланированной матрицы',['Семейство варианта','Реальный бинарник','Серия','Задание','Повтор','Этап','Статус','Причина','Собственный вход','Полный инференс','Данные'],coverage.map(r=>[r.variant_family,r.actual_variant,r.cohort,r.job,r.repeat,r.stage,r.status,r.reason??r.inference_plan??'',r.own_status??'',r.full_status??'',r.directory??'']),[25,25,30,40,12,12,45,110,30,30,110]);
sheet('Протоколы','Объект сравнения и условия интерпретации',['Обозначение','Определение','Применение'],[
 ['История','Числовой результат из старого отчёта или таблицы','Источник указан в ScientificComparisons и в реестре источников'],
 ['Предыдущая проверка','Инференс исходных сохранённых или восстановленных структур на autoPreset','Не является результатом нового обучения'],
 ['Новое обучение','Фактически полученная структура и измеренный инференс','Архивные d и s не подставлялись'],
 ['V1C и VP1','Инициализация после изменения структуры; прежнее условие остановки','VP1 дополнительно записывает испытания между циклами; физический алгоритм тот же'],
 ['V2','V1C с историческими параметрами новых синапсов','Пилот не прошёл контроль собственного входа; массовое расширение не выполняется'],
 ['V3','Частичная реконструкция архивного цикла и решений 2023 года','Не является полной программой 2022 года'],
 ['R0','Без исправления PulseLib; восстановлен автоматический Init в Rdk','Изолированное исследование причины неинициализации'],
 ['Повторное использование инференса','Совпадают физический граф, параметры, начальный вход, тестовый набор и бинарник','Повторы обучения выполняются независимо'],
 ['FP и FN','Ложное срабатывание и пропуск; Q=FP+FN','Подвыборки 150, 30 и 10 различаются и не смешиваются'],
 ['Предварительные схемы','Явные реконструкции последовательностей 1+4 и 2+4','Не выбираются по лучшему совпадению с архивом']],[36,105,110]);
wb.worksheets.getItem('Протоколы').getRange('A6:C15').format.rowHeight=65;
for(const [name,ranges] of [
 ['Переход все показатели',['G6:I47','K6:N47']],
 ['Все последовательности',['I6:K248','M6:M248']],
 ['Контроли инференса',['I6:I17']],
 ['Геометрия и инференс',['F6:F9']],
 ['Прежняя NL22 и порядок',['F6:F8']],
 ['Отдельные факторы',[`P6:P${d.factors.length+5}`]]
])for(const range of ranges)wb.worksheets.getItem(name).getRange(range).setNumberFormat('0.00%');
wb.recalculate();
await fs.mkdir(out,{recursive:true});await fs.mkdir(path.join(work,'xlsx-qa'),{recursive:true});
const scan=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!',options:{useRegex:true,maxResults:30},maxChars:1500});
await fs.writeFile(path.join(work,'workbook-scan.ndjson'),scan.ndjson);
await savePublishedWorkbook(await SpreadsheetFile.exportXlsx(wb),path.join(out,'TrainingReproducibility.xlsx'),work);
await fs.writeFile(path.join(work,'report-figures.json'),JSON.stringify(figures,null,2));
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
if(hash(rawData)!==hash(await fs.readFile(path.join(work,'report-data.json')))||hash(coverageBytes)!==hash(await fs.readFile(path.join(work,'coverage-ledger.json'))))throw new Error('Evidence changed during workbook build; rerun with a frozen snapshot');
await fs.writeFile(path.join(work,'workbook-provenance.json'),JSON.stringify({report_data_sha256:hash(rawData),coverage_sha256:hash(coverageBytes),charts:figures.length},null,2));
for(const s of wb.worksheets.items){const blob=await wb.render({sheetName:s.name,range:'A1:H16',scale:1.5,format:'png'});await fs.writeFile(path.join(work,'xlsx-qa',s.name+'.png'),new Uint8Array(await blob.arrayBuffer()));}
console.log('Exported workbook with '+figures.length+' native comparison charts');
