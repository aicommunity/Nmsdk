import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
process.on('uncaughtException',e=>{console.error(e.message);console.error(e.stack.split('\n').filter(s=>s.includes('legacy_workbook.mjs')).join('\n'));process.exit(1);});
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const work=path.join(repo,'Reports/StructTrainClassic/LegacyInferencePlan-20261123/work');
const out=path.join(repo,'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9');
const d=JSON.parse(await fs.readFile(path.join(work,'plan-data.json'),'utf8'));
const wb=Workbook.create();
const names=['План','Модели','Состояния','Сравнение инференса','Эпохи и графики','Проекции Iris','Осциллограммы','Реестр рисунков','Ряды архива','Источники'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const color={header:'#273F57',old:'#557C9B',previous:'#C48A45',fresh:'#558368',input:'#FFF3D5',grey:'#E7EBEF'};
function col(i){let s='';for(let n=i;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;}
function table(sheet,title,headers,rows,widths,rowHeight=32){
 const last=rows.length+5; const end=col(headers.length);
 sheet.showGridLines=false;
 sheet.getRange(`A1:${end}${Math.max(last,6)}`).format.font={name:'Arial',size:10,color:'#172B3A'};
 sheet.getRange(`A1:${end}${Math.max(last,6)}`).format.verticalAlignment='center';
 sheet.getRange('A2').values=[[title]];sheet.getRange('A2').format.font={name:'Arial',size:16,bold:true};
 sheet.getRange('A2').format.wrapText=false;sheet.getRange('A2').format.rowHeight=28;
 sheet.getRange(`A5:${end}5`).values=[headers];
 sheet.getRange(`A5:${end}5`).format={fill:color.header,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:34};
 if(rows.length) sheet.getRange(`A6:${end}${last}`).values=rows;
 sheet.getRange(`A6:${end}${Math.max(last,6)}`).format.rowHeight=rowHeight;
 sheet.getRange(`A6:${end}${Math.max(last,6)}`).format.wrapText=true;
 widths.forEach((w,i)=>sheet.getRange(`${col(i+1)}1:${col(i+1)}${Math.max(last,6)}`).format.columnWidth=w);
 sheet.freezePanes.freezeRows(5);
 return last;
}
function note(sheet,range,text){sheet.getRange(range).values=[[text]];sheet.getRange(range).format.font={name:'Arial',size:10,color:'#596B78',italic:true};}
const chartViews=[];
function chart(sheet,type,ranges,title,position,numberFormat='0.0%'){
 const c=sheet.charts.add(type,ranges);c.title=title;c.setPosition(position[0],position[1]);
 c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=14;
 c.legend={position:'top',textStyle:{typeface:'Arial',fontSize:12}};
 c.xAxis={axisType:type==='scatter'?'valueAxis':'textAxis',textStyle:{typeface:'Arial',fontSize:12}};
 c.yAxis={numberFormatCode:numberFormat,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:12}};
 const palette=[color.old,color.previous,color.fresh,'#9973A2','#C0A13F','#557F7B','#8A6B59'];
 c.series.items.forEach((s,i)=>{s.fill=palette[i%palette.length];if(type==='line')s.line={fill:palette[i%palette.length],style:'solid',width:2};});
 chartViews.push({sheet:sheet.name,range:`${position[0]}:${position[1]}`});
 return c;
}

let sh=sheets['План'];
table(sh,'План проверки архивных моделей и графиков',
 ['Код','Сравнение','Исторический источник','Оси и единицы','Ряды','Способ сравнения','Доступность','Выполнение'],
 d.families.map(f=>[f.id,f.name,f.sources,f.axes,f.series,f.comparison,f.readiness,'Планируется']),[8,42,55,48,55,86,38,20],60);
note(sh,'A3','Сначала сохранённые обученные состояния из Эксперименты, затем недостающие реконструкции. Новые проверки исходных моделей ещё не запускались.');
sh.getRange('J2:K3').values=[['Выполнено семейств','Всего семейств'],[null,d.families.length]];
sh.getRange('J3').formulas=[['=COUNTIFS(H6:H23,"Выполнено")']];
sh.getRange('H6:H23').dataValidation={rule:{type:'list',values:['Планируется','Выполнено','Нет исходных данных']}};
sh.getRange('H6:H23').format.fill=color.input;sh.tabColor=color.header;

sh=sheets['Модели'];
table(sh,'Сохранённые состояния из исходных XML',
 ['ID','Класс','Обучающий ID','Текущий ID','Активен путь','Метаданные совпали','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Проект','Компонент','Флаг обучения','Режим'],
 d.models.map(m=>[m.id,m.class,m.saved_training_id,m.candidate_dataset_id,m.effective_active,m.training_metadata_matches_graph,...m.dendrites,...m.synapses,m.project,m.component,Number(m.training_flag),Number(m.calculate_mode)]),
 [9,25,16,16,16,22,...Array(10).fill(7),36,64,16,12],28);
note(sh,'A3','TrainingPattern определяет обучающий пример. InputPattern может быть текущим тестовым входом. False активности может относиться к предку.');
sh.getRange('G6:P25').setNumberFormat('0');sh.freezePanes.freezeColumns(2);

const firstGroup=new Map();for(const r of d.restoration_rows)if(r.complete&&!firstGroup.has(r.structure_group))firstGroup.set(r.structure_group,r.id);
sh=sheets['Состояния'];
table(sh,'Структуры для восстановления с сохранением всех источников',
 ['ID записи','Алгоритм','Исторический случай','Полная структура','Группа d s','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Профиль','Источник','Ответов в файле','Лишние поля заголовка','Первая запись группы'],
 d.restoration_rows.map(r=>[r.id,r.kind,r.label,r.complete,'SG_'+r.structure_group,...(r.dendrites??Array(5).fill(null)),...(r.synapses??Array(5).fill(null)),r.profile,r.source,r.answer_count??null,JSON.stringify(r.header_extra_fields??[]),r.complete?firstGroup.get(r.structure_group):null]),
 [12,14,55,20,22,...Array(10).fill(7),30,100,18,26,24],34);
note(sh,'A3','361 полная запись и 136 неполных. 70 групп d s — кандидаты; окончательное объединение требует совпадения физических настроек и протокола.');
sh.getRange(`F6:O${d.restoration_rows.length+5}`).setNumberFormat('0');sh.freezePanes.freezeColumns(3);

const previous=[];
const runDir=path.join(repo,'Reports/StructTrainClassic/run-20261123-a2');
for(const entry of await fs.readdir(runDir,{withFileTypes:true})){
 if(!entry.isDirectory()||!entry.name.startsWith('recognition'))continue;
 const file=path.join(runDir,entry.name,'results.jsonl');
 try {for(const line of (await fs.readFile(file,'utf8')).trim().split('\n')){const r=JSON.parse(line);if(r.frozen_archive_structure)previous.push(r);}}catch(e){if(e.code!=='ENOENT')throw e;}
}
const byVariant=new Map(previous.map(r=>[r.reference.variant_index,r]));
const classes=d.dataset.map(s=>s.class);
function counts(answers,target){let tp=0,fp=0,fn=0,tn=0;answers.forEach((a,i)=>{if(classes[i]===target){if(a)tp++;else fn++;}else{if(a)fp++;else tn++;}});return [tp,fp,fn,tn];}
sh=sheets['Сравнение инференса'];
const inferenceRows=d.recognition_reference.map((r,i)=>{
 const old=counts(r.answers,Math.floor((r.id-1)/50)+1),p=byVariant.get(i);
 const label=(r.kind==='learner'?'NL':'NT')+r.id+(String(r.variant).includes('(')?String(r.variant).slice(String(r.variant).indexOf('(')):'');
 const mismatch=p.answers.reduce((n,a,k)=>n+(a!==r.answers[k]),0);
 return [label,r.id,...old,null,null,null,null,null,null,p.TP,p.FP,p.FN,p.TN,null,mismatch,null,null,null,null,null,null,'Не запускалось'];
});
table(sh,'Исторический инференс и предыдущий контроль реконструкций',
 ['Модель','ID','Архив TP','Архив FP','Архив FN','Архив TN','Precision','Recall','Accuracy','Balanced accuracy','Q ошибок','Риск доля','Контроль TP','Контроль FP','Контроль FN','Контроль TN','Контроль balanced','Разных ответов','Новый TP','Новый FP','Новый FN','Новый TN','Новый balanced','Отклонение balanced','Новый запуск'],
 inferenceRows,[16,8,...Array(4).fill(12),...Array(6).fill(16),...Array(4).fill(14),20,18,...Array(4).fill(12),20,22,25],26);
note(sh,'A3','Контроль — 22 реконструкции предыдущего запуска. Новые исходные сохранённые модели ещё не проверены; пустые поля S V не являются нулями.');
for(let row=6;row<=27;row++){
 sh.getRange(`G${row}:L${row}`).formulas=[[
  `=IF(C${row}+D${row}=0,"n.a.",C${row}/(C${row}+D${row}))`,`=C${row}/(C${row}+E${row})`,
  `=(C${row}+F${row})/SUM(C${row}:F${row})`,`=0.5*(C${row}/(C${row}+E${row})+F${row}/(F${row}+D${row}))`,
  `=D${row}+E${row}`,`=K${row}/SUM(C${row}:F${row})`]];
 sh.getRange(`Q${row}`).formulas=[[`=0.5*(M${row}/(M${row}+O${row})+P${row}/(P${row}+N${row}))`]];
 sh.getRange(`W${row}:Y${row}`).formulas=[[
  `=IF(COUNT(S${row}:V${row})<4,"",IF(AND(SUM(S${row}:V${row})=150,S${row}+U${row}>0,V${row}+T${row}>0),0.5*(S${row}/(S${row}+U${row})+V${row}/(V${row}+T${row})),"n.a."))`,
  `=IF(ISNUMBER(W${row}),W${row}-J${row},"")`,
  `=IF(COUNT(S${row}:V${row})=0,"Не запускалось",IF(COUNT(S${row}:V${row})<4,"Не все счётчики",IF(SUM(S${row}:V${row})<>150,"Проверить N","Записано")))`]];
}
sh.getRange('G6:J27').setNumberFormat('0.0%');sh.getRange('L6:L27').setNumberFormat('0.0%');sh.getRange('Q6:Q27').setNumberFormat('0.0%');
sh.getRange('W6:X27').setNumberFormat('0.0%');sh.getRange('S6:V27').format.fill=color.input;
chart(sh,'bar',[sh.getRange('A5:A27'),sh.getRange('J5:J27'),sh.getRange('Q5:Q27'),sh.getRange('W5:W27')],'Сравнение инференса на 150 входах',['A32','R52']);
sh.freezePanes.freezeColumns(2);

sh=sheets['Эпохи и графики'];
table(sh,'Состояния схемы 0 на 1 плюс 4 и исторические показатели',
 ['Эпоха','TP','FP','FN','TN','Precision','Recall','Balanced accuracy','Q число ошибок','Риск доля','Ошибки процент','Precision среднее','Recall среднее','Q среднее','Новый TP','Новый FP','Новый FN','Новый TN','Новый precision','Новый recall','Новый Q','Новый риск','Источник'],
 d.epochs.map(r=>[r.epoch,r.TP,r.FP,r.FN,r.TN,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,null,r.source]),
 [10,...Array(4).fill(9),16,16,20,20,16,20,20,20,18,...Array(4).fill(12),20,20,18,18,110],26);
note(sh,'A3','Эпохи 0 13 соответствуют 14 состояниям. Источник чисел — таблица исследования; соответствие приложению В ВКР проверено.');
for(let row=6;row<=19;row++){
 sh.getRange(`F${row}:N${row}`).formulas=[[
  `=B${row}/(B${row}+C${row})`,`=B${row}/(B${row}+D${row})`,`=0.5*(B${row}/(B${row}+D${row})+E${row}/(E${row}+C${row}))`,
  `=C${row}+D${row}`,`=I${row}/SUM(B${row}:E${row})`,`=100*J${row}`,`=$B$24`, `=$C$24`,`=$D$24`]];
 sh.getRange(`S${row}:V${row}`).formulas=[[
  `=IF(COUNT(O${row}:R${row})=4,IF(O${row}+P${row}>0,O${row}/(O${row}+P${row}),"n.a."),"")`,
  `=IF(COUNT(O${row}:R${row})=4,IF(O${row}+Q${row}>0,O${row}/(O${row}+Q${row}),"n.a."),"")`,
  `=IF(COUNT(O${row}:R${row})=4,P${row}+Q${row},"")`,
  `=IF(COUNT(O${row}:R${row})=4,IF(SUM(O${row}:R${row})>0,U${row}/SUM(O${row}:R${row}),"n.a."),"")`]];
}
sh.getRange('A22:J25').values=[['Базовое состояние','Precision','Recall','Q ошибок','Риск доля','Источник','TP','FP','FN','TN'],
 ['51',null,null,null,null,'ВКР таблицы 7 и 8',d.baselines[0].TP,d.baselines[0].FP,d.baselines[0].FN,d.baselines[0].TN],
 ['Среднее 51 и 61',null,null,null,null,'ВКР таблицы 7 и 8',d.baselines[2].TP,d.baselines[2].FP,d.baselines[2].FN,d.baselines[2].TN],
 ['61',null,null,null,null,'ВКР таблицы 7 и 8',d.baselines[1].TP,d.baselines[1].FP,d.baselines[1].FN,d.baselines[1].TN]];
for(const [row,source] of [[23,d.baselines[0]],[24,d.baselines[2]],[25,d.baselines[1]]]){
 sh.getRange(`B${row}:E${row}`).formulas=[[`=G${row}/(G${row}+H${row})`,`=G${row}/(G${row}+I${row})`,`=H${row}+I${row}`,`=D${row}/SUM(G${row}:J${row})`]];
}
sh.getRange('A22:J25').format.rowHeight=30;sh.getRange('A22:J25').format.wrapText=true;
sh.getRange('F6:H19').setNumberFormat('0.0%');sh.getRange('J6:J19').setNumberFormat('0.0%');sh.getRange('L6:M19').setNumberFormat('0.0%');sh.getRange('K6:K19').setNumberFormat('0.00');
sh.getRange('B23:C25').setNumberFormat('0.0%');sh.getRange('E23:E25').setNumberFormat('0.0%');sh.getRange('O6:R19').format.fill=color.input;
sh.getRange('S6:T19').setNumberFormat('0.0%');sh.getRange('V6:V19').setNumberFormat('0.0%');
chart(sh,'line',[sh.getRange('A5:A19'),...['F','G','L','M','S','T'].map(c=>sh.getRange(`${c}5:${c}19`))],'Precision и recall по эпохам и среднее состояние',['A29','K48']);
chart(sh,'line',[sh.getRange('A5:A19'),...['I','N','U'].map(c=>sh.getRange(`${c}5:${c}19`))],'Q как количество ошибок',['M29','V48'],'0');
chart(sh,'line',[sh.getRange('A5:A19'),...['J','V'].map(c=>sh.getRange(`${c}5:${c}19`))],'Нормированная доля ошибок',['A51','K70']);
chart(sh,'line',[sh.getRange('A5:A19'),sh.getRange('H5:H19')],'Сбалансированная точность по эпохам',['M51','V70']);

sh=sheets['Проекции Iris'];
table(sh,'Входы Iris и проверка временного кодирования',['ID','Класс','d1 с','d2 с','d3 с','d4 с','d5 с'],
 d.dataset.map(r=>[r.id,r.class,...r.pattern]),[9,12,...Array(5).fill(15)],21);
note(sh,'A3','Исходные сохранённые значения листа Датасет из Протоколы экспериментов.xlsx. Числа хранятся с полной доступной точностью.');
sh.getRange('C6:G155').setNumberFormat('0.0000');
const pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],selected=new Set([22,37,45,60,64,84,90,111,129,134]);
for(let i=0;i<pairs.length;i++){
 const [x,y]=pairs[i],start=10+i*8;
 const headers=[`d${x+1}`, 'Класс 1','Класс 2','Класс 3','10 эталонов','Пример 51','Пример 61'];
 const values=d.dataset.map(r=>[r.pattern[x],...([1,2,3].map(c=>r.class===c?r.pattern[y]:null)),selected.has(r.id)?r.pattern[y]:null,r.id===51?r.pattern[y]:null,r.id===61?r.pattern[y]:null]);
 sh.getRange(`${col(start)}5:${col(start+6)}155`).values=[headers,...values];
 const c=chart(sh,'scatter',sh.getRange(`${col(start)}5:${col(start+6)}155`),`Проекция d${x+1} и d${y+1} в секундах`,
  [i%2===0?`A${160+Math.floor(i/2)*23}`:`J${160+Math.floor(i/2)*23}`,i%2===0?`I${181+Math.floor(i/2)*23}`:`R${181+Math.floor(i/2)*23}`],'0.00');
 c.xAxis.numberFormatCode='0.00';c.xAxis.numberFormatSourceLinked=false;
}

sh=sheets['Осциллограммы'];
table(sh,'Исторические осциллограммы и план снятия сравнимых сигналов',['Семейство','Историческое наблюдение','Новая запись','Условие сравнимости'],
 [['G02','Отдельные сомы и сумма','Планируется','Тот же вход, структура и физические параметры'],
 ['G03','Обучение 111 на итерациях 6 10','Планируется отдельно','Нужны состояния каждой итерации; финальный инференс отмечать отдельно'],
 ['G04','Переобучение 22 к 129','Планируется отдельно','Замороженный входной переход не является всей динамикой обучения'],
 ['G05','Переобучение 22 к 37','Планируется отдельно','Установить снимки до перехода и после него']], [15,53,32,80],42);
note(sh,'A3','Исторические изображения ниже — эталоны. Новые исходные сохранённые модели в рамках подготовки плана не запускались.');
const waveAssets=['c3a2737b','f57e7053','9266ab41','4ed6e8b5','f6b043a3'];
for(let i=0;i<waveAssets.length;i++){
 const f=d.figures.find(r=>r.asset.startsWith(waveAssets[i]));if(!f?.preview)continue;
 const bytes=await fs.readFile(f.preview);
 const imageWidth=bytes.readUInt32BE(16),imageHeight=bytes.readUInt32BE(20);
 const widthPx=Math.min(900,280*imageWidth/imageHeight),heightPx=widthPx*imageHeight/imageWidth;
 sh.getRange(`A${12+i*18}`).values=[[`${f.family}   ${f.source}   ${f.location}`]];
 sh.images.add({dataUrl:'data:image/png;base64,'+bytes.toString('base64'),anchor:{from:{row:12+i*18,col:0},extent:{widthPx,heightPx}}});
}

sh=sheets['Реестр рисунков'];
const figureRows=d.figures.map(f=>[f.id,f.family,f.role,f.source,f.location,f.asset,f.duplicate_source,f.context.slice(0,220)]);
for(const c of d.charts)figureRows.push([c.id,c.family,'Диаграмма XLSX',c.source,c.member,'',false,c.title||c.axis_titles.join('; ')]);
table(sh,'Все иллюстрации собственных документов и уникальные диаграммы',['ID','Семейство','Тип','Источник','Положение','Идентификатор изображения','Копия источника','Подпись или контекст'],figureRows,[10,12,25,80,30,26,22,95],44);
note(sh,'A3','Повторные использования рисунка сохранены как ссылки. Схемы и оформление отмечены отдельно от числовых графиков.');

sh=sheets['Ряды архива'];
const points=[];
for(const c of d.charts)for(let k=0;k<c.series.length;k++){
 const s=c.series[k],n=Math.max(s.values.length,s.categories.length);
 for(let i=0;i<n;i++){
  const val=s.values[i]==null||s.values[i]===''?null:Number(s.values[i]);
  const rawX=s.categories[i];const x=rawX==null?(s.categories.length?null:i+1):!Number.isNaN(Number(rawX))?Number(rawX):rawX;
  points.push([c.id,c.family,s.name||`Ряд ${k+1}`,i+1,x,val,c.source,s.formulas.join(' ; ')]);
 }
}
table(sh,'Числовые ряды всех уникальных диаграмм исходных XLSX',['Диаграмма','Семейство','Ряд','Индекс точки','X или категория','Y','Источник','Исходные диапазоны'],points,[14,12,75,16,22,20,90,100],34);
note(sh,'A3','Значения извлечены из исходных кэшей диаграмм с сохранением пропусков; отсутствующие Y остаются пустыми.');
sh.getRange(`F6:F${points.length+5}`).setNumberFormat('0.0000');

sh=sheets['Источники'];
table(sh,'Полный реестр исходного архива',['ID','Путь в архиве','Роль','Формат','Канонический источник','SHA256','Размер байт'],
 d.documents.map(r=>[r.id,r.path,r.path.startsWith('Эксперименты/')?'Основной':r.role==='theory'?'Теоретический':'Дополнительный',r.extension,r.canonical_doc,r.sha256,r.bytes]),[10,110,25,15,24,72,18],38);
note(sh,'A3','Корень источников E:\\Science-Repo\\nmsdk-git\\Docs\\ClassicStructTrainExperiments. Среди копий предпочитается путь в Эксперименты.');
sh.getRange(`G6:G${d.documents.length+5}`).setNumberFormat('#,##0');

await fs.mkdir(out,{recursive:true});
wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Сравнение инференса!A5:L8',include:'values,formulas',tableMaxRows:4,tableMaxCols:12,maxChars:2200})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'formula error scan',maxChars:1500})).ndjson);
// Verify live missing/new-result behavior, then restore the unexecuted input.
const inf=sheets['Сравнение инференса'];
inf.getRange('S6:V6').values=[[49,0,1,100]];wb.recalculate();
const testFilled=inf.getRange('W6:Y6').values;
inf.getRange('S6:V6').clear({applyTo:'contents'});wb.recalculate();
const testRestored=inf.getRange('W6:Y6').values;
await fs.writeFile(path.join(work,'workbook-formula-check.json'),JSON.stringify({filled:testFilled,restored:testRestored},null,2));
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(out,'GraphComparisonPlan.xlsx'));
const previewDir=path.join(work,'xlsx-qa');await fs.mkdir(previewDir,{recursive:true});
let index=0;
for(const name of names){
 const range=name==='План'?'A1:D10':name==='Модели'?'A1:P12':name==='Состояния'?'A1:O12':name==='Сравнение инференса'?'A1:L12':name==='Эпохи и графики'?'A1:N12':name==='Реестр рисунков'?'A1:E10':name==='Ряды архива'?'A1:F12':name==='Источники'?'A1:E10':'A1:G10';
 const png=await wb.render({sheetName:name,range,scale:1.3,format:'png'});
 await fs.writeFile(path.join(previewDir,`sheet-${++index}.png`),new Uint8Array(await png.arrayBuffer()));
}
for(let i=0;i<chartViews.length;i++){
 const v=chartViews[i];const png=await wb.render({sheetName:v.sheet,range:v.range,scale:1.2,format:'png'});
 await fs.writeFile(path.join(previewDir,`chart-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
for(let i=0;i<waveAssets.length;i++){
 const firstRow=12+i*18;
 const png=await wb.render({sheetName:'Осциллограммы',range:`A${firstRow}:D${firstRow+17}`,scale:1.2,format:'png'});
 await fs.writeFile(path.join(previewDir,`wave-${i+1}.png`),new Uint8Array(await png.arrayBuffer()));
}
await fs.writeFile(path.join(work,'workbook-layout.json'),JSON.stringify({sheets:names,charts:chartViews,archivePoints:points.length},null,2));
console.log(path.join(out,'GraphComparisonPlan.xlsx'));
