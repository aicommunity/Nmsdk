import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
process.on('uncaughtException',e=>{console.error(e.message);console.error(e.stack.split('\n').filter(s=>s.includes('legacy_results_workbook')).join('\n'));process.exit(1);});
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
const work=path.join(repo,'Reports/StructTrainClassic/LegacyChecks-20261123');
const out=path.join(repo,'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/LegacyChecks');
const read=async p=>JSON.parse(await fs.readFile(p,'utf8'));
const a=await read(path.join(work,'assessment.json'));
const d=await read(path.join(work,'execution-plan-data.json'));
const jobs=await read(path.join(repo,'Bin/Configs/StructTrainClassic/LegacyInference/recovered-jobs.json'));
const mapping=await read(path.join(work,'recovered-mapping.json'));
const recovery=await read(path.join(work,'recovery-summary.json'));
const refs=await read(path.join(work,'protocol-references.json'));
const wb=Workbook.create(),names=['Сохранённые модели','Восстановленные состояния','Распознавание','Эпохи','Подвыборки','Базовые модели','Сигналы','Переходы','Проекции Iris','Ответы','Реестр структур','Покрытие графиков','Оцифровка','Сопоставление осциллограмм','Контекст проекта'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const colors={header:'#273F57',old:'#567E9B',fresh:'#B46B33',green:'#4D8274',grey:'#6D7681',purple:'#9670A1',gold:'#B59A3D'};
const figures=[],previews=[];
const col=n=>{let s='';for(;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
function table(sh,title,headers,rows,widths,height=28){
 const last=Math.max(6,rows.length+5),end=col(headers.length);sh.showGridLines=false;
 sh.getRange(`A1:${end}${last}`).format={font:{name:'Arial',size:10,color:'#203343'},verticalAlignment:'center'};
 sh.getRange('A2').values=[[title]];sh.getRange('A2').format={font:{name:'Arial',size:17,bold:true},rowHeight:30};
 sh.getRange(`A5:${end}5`).values=[headers];sh.getRange(`A5:${end}5`).format={fill:colors.header,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:38,wrapText:true};
 if(rows.length)sh.getRange(`A6:${end}${rows.length+5}`).values=rows;
 sh.getRange(`A6:${end}${last}`).format.rowHeight=height;sh.getRange(`A6:${end}${last}`).format.wrapText=true;
 widths.forEach((w,i)=>sh.getRange(`${col(i+1)}1:${col(i+1)}${last}`).format.columnWidth=w);
 sh.freezePanes.freezeRows(5);previews.push({sheet:sh.name,range:`A1:${col(Math.min(headers.length,9))}${Math.min(13,last)}`});
}
function note(sh,text){sh.getRange('A3').values=[[text]];sh.getRange('A3').format={font:{name:'Arial',size:10,italic:true,color:'#5E6C77'}};}
function chart(sh,type,ranges,title,start,end,description,analysis='',format='0.0%'){
 if(type==='column')type='bar';
 const c=sh.charts.add(type,ranges);c.title=title;c.setPosition(start,end);
 c.displayBlanksAs='gap';
 if(type==='scatter')c.apply({scatterOptions:{style:'marker'}});
 c.titleTextStyle.typeface='Arial';c.titleTextStyle.fontSize=17;c.legend={position:'top',textStyle:{typeface:'Arial',fontSize:14}};
 c.xAxis={axisType:type==='scatter'?'valueAxis':'textAxis',textStyle:{typeface:'Arial',fontSize:14},majorGridlines:null,minorGridlines:null};
 c.yAxis={numberFormatCode:format,numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:14},minorGridlines:null,majorGridlines:{fill:'#D7DEE5',width:0.6,style:'solid'}};
 if(format.includes('%')){c.yAxis.min=0;if(/точность|распознавание|precision|recall|TPR|TP из|M018/i.test(title))c.yAxis.max=1;}
 if(type==='line'&&format==='0.000'){
  c.yAxis.min=0;c.yAxis.max=.09;
  description+=' Показано положительное окно 0–0,09 В, как в архивных осциллограммах. Отрицательные фазы сброса сохранены в числовых рядах XLSX.';
  c.xAxis.numberFormatCode='0.00';c.xAxis.numberFormatSourceLinked=false;c.xAxis.tickLabelInterval=Math.max(1,Math.ceil((ranges[0].values.length-1)/8));
 }
 const palette=[colors.old,colors.fresh,colors.green,colors.purple,colors.gold,colors.grey];
 c.series.items.forEach((s,i)=>{s.fill=palette[i%palette.length];if(type==='line')s.line={fill:palette[i%palette.length],style:'solid',width:2};});
 const f={id:`V${String(figures.length+1).padStart(2,'0')}`,sheet:sh.name,index:figures.filter(f=>f.sheet===sh.name).length+1,title,range:`${start}:${end}`,description,analysis};figures.push(f);return c;
}
function metricFormulas(sh,row,start,counts){
 const [tp,fp,fn,tn]=counts.map(c=>`${c}${row}`),cs=col(start);
 sh.getRange(`${cs}${row}:${col(start+5)}${row}`).formulas=[[
 `=IFERROR(${tp}/(${tp}+${fp}),"")`,`=IFERROR(${tp}/(${tp}+${fn}),"")`,
 `=IFERROR((${tp}/(${tp}+${fn})+${tn}/(${tn}+${fp}))/2,"")`,`=${fp}+${fn}`,
 `=IFERROR((${fp}+${fn})/SUM(${tp},${fp},${fn},${tn}),"")`,`=IFERROR((${tp}+${tn})/SUM(${tp},${fp},${fn},${tn}),"")`]];
 sh.getRange(`${cs}${row}:${col(start+2)}${row}`).setNumberFormat('0.0%');sh.getRange(`${col(start+4)}${row}:${col(start+5)}${row}`).setNumberFormat('0.0%');
}
const fullSaved=a.saved.filter(r=>r.repeat===1&&r.answers.length===150);
let sh=sheets[names[0]];
const savedRows=fullSaved.map(r=>{const ref=a.saved_comparisons.find(x=>x.case===r.case)?.references[0];return [r.job.source_model,r.job.target_id,r.job.activation,r.loaded_readback.all_initialized,r.graph_loading.passed,r.graph_inference.passed,
 r.TP,r.FP,r.FN,r.TN,null,null,null,null,null,null,ref?.metrics.balanced_accuracy??null,ref?.mismatch_ids.length??null,r.job.source_component,r.answers[r.job.target_id-1],r.peaks[r.job.target_id-1]];});
table(sh,'Исходные сохранённые состояния: структура и инференс',['Модель','Обучающий ID','Активность','Инициализация','Граф при загрузке','Граф при инференсе','TP','FP','FN','TN','Precision','Recall','BAcc','Q ошибок','Риск','Accuracy','Архив BAcc','Различия ответов','Исходный компонент','Ответ на свой ID','Пик на своём ID, В'],savedRows,[12,17,20,20,20,22,9,9,9,9,16,16,16,14,14,16,18,20,63,22,25],35);
note(sh,'Восемь состояний запускались с явно включённым поддеревом и внешними источниками для транзитных входов. M018 сохранён активным.');
for(let i=0;i<savedRows.length;i++)metricFormulas(sh,i+6,11,['G','H','I','J']);sh.getRange('Q6:Q14').setNumberFormat('0.0%');
chart(sh,'column',[sh.getRange('A5:A14'),sh.getRange('M5:M14'),sh.getRange('Q5:Q14')],'Сохранённые модели: сбалансированная точность','A18','N37','Архив и новый инференс на 150 входах; отсутствующие архивные столбцы оставлены пустыми.','Структурное соответствие оценивается отдельно от классификации. Для 110 и 132 исторические столбцы не подменялись 111 и 134.');
// Physical readback and source counters remain explicit, channel by channel.
sh=sheets[names[1]];
const states=jobs.map(j=>{const m=a.first_by_job[j.id];const native=[...a.saved,...a.recovered].find(r=>r.case===m?.case&&r.repeat===1);return [j.id,j.kind,...j.dendrites,...j.synapses,native?.physically_ready??null,native?.graph_loading.passed??null,native?.graph_inference.passed??null,
 a.reused.some(r=>r.recovered_job===j.id)?'Повторно использован эквивалентный прогон':'Отдельный прогон',mapping.filter(r=>r.job===j.id).length,j.profile_donor,j.config];});
table(sh,'Восстановленные физические состояния без повторных экспериментов',['Состояние','Алгоритм','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Готово физически','Сохранено при загрузке','Стабильно при инференсе','Измерение','Число ссылок','Профиль','Конфигурация'],states,[22,16,...Array(10).fill(8),22,24,24,51,18,14,110],32);
note(sh,`${recovery.source_rows} исходных строк; ${recovery.completed_partial_rows} неполных строк дополнены однозначно; ${recovery.unresolved_rows} остаются неполными. Профили взяты из M001 и M019, порог — из FixedLTZThreshold.`);
sh=sheets[names[2]];
const recRows=a.recognition_comparisons.map(r=>{let x=r.archived_metrics,y=r.measured_metrics;return [`${r.reference.kind==='trainer'?'NT':'NL'}${r.reference.id}${String(r.reference.variant).match(/\(\d+\)/)?.[0]??''}`,r.job,x.TP,x.FP,x.FN,x.TN,null,null,null,null,null,null,y.TP,y.FP,y.FN,y.TN,null,null,null,null,null,null,r.mismatch_ids.length,r.mismatch_ids.join(', '),r.reference.source_range];});
table(sh,'Исторические столбцы распознавания и autoPreset',['Модель','Состояние','Арх TP','Арх FP','Арх FN','Арх TN','Арх precision','Арх recall','Арх BAcc','Арх Q','Арх риск','Арх accuracy','Нов TP','Нов FP','Нов FN','Нов TN','Нов precision','Нов recall','Нов BAcc','Нов Q','Нов риск','Нов accuracy','Различий','ID различий','Исторический диапазон'],recRows,[34,24,...Array(4).fill(11),...Array(6).fill(16),...Array(4).fill(11),...Array(6).fill(16),15,70,25],34);
note(sh,'Источник: Эксперименты/Тестирование/Распознавание/Распознавание.xlsx. Сопоставлены алгоритм, обучающий ID и структурный вариант.');
sh.getRange('A4').values=[['Варианты закреплены существовавшим до запуска манифестом: без индекса — первая документированная структура ID; альтернативы сохранены в реестре. Выбор по новому качеству не выполнялся.']];
for(let i=0;i<recRows.length;i++){metricFormulas(sh,i+6,7,['C','D','E','F']);metricFormulas(sh,i+6,17,['M','N','O','P']);}
const recEnd=recRows.length+5;
chart(sh,'column',[sh.getRange(`A5:A${recEnd}`),sh.getRange(`I5:I${recEnd}`),sh.getRange(`S5:S${recEnd}`)],'Распознавание: архив и восстановленные состояния','A31','T52','Сбалансированная точность по всем соответствующим историческим моделям.');
chart(sh,'column',[sh.getRange(`A5:A${recEnd}`),sh.getRange(`W5:W${recEnd}`)],'Различия бинарных ответов на 150 входах','A55','T75','Число несовпадений ответов; структурный критерий проверен независимо.','','0');
sh=sheets[names[3]];
table(sh,'Схема 0 на 1 плюс 4: состояния эпох и классификация',['Эпоха','Арх TP','Арх FP','Арх FN','Арх TN','Арх precision','Арх recall','Арх BAcc','Арх Q','Арх риск','Арх accuracy','Нов TP','Нов FP','Нов FN','Нов TN','Нов precision','Нов recall','Нов BAcc','Нов Q','Нов риск','Нов accuracy','Состояние'],
 a.epochs.map(e=>[e.epoch,e.archived.TP,e.archived.FP,e.archived.FN,e.archived.TN,...Array(6).fill(null),e.measured.TP,e.measured.FP,e.measured.FN,e.measured.TN,...Array(6).fill(null),e.job]),[12,...Array(20).fill(16),24],30);
note(sh,'Архив: Обучение нескольким примерам.xlsx, схема для 150 примеров, строки 2–15; ВКР, приложение В. Эпохи канонически 0–13.');
for(let i=0;i<a.epochs.length;i++){metricFormulas(sh,i+6,6,['B','C','D','E']);metricFormulas(sh,i+6,16,['L','M','N','O']);}
const eEnd=a.epochs.length+5;
for(const [title,cols,start,end,format,desc] of [
 ['Precision и recall по эпохам',['F','G','P','Q'],'A23','L43','0.0%','Архивные и новые precision/recall, одинаковая популяция 150 входов.'],
 ['Исторический Q: количество ошибок',['I','S'],'N23','Y43','0','Шкала FP+FN сохранена как количество ошибок.'],
 ['Нормированная доля ошибок по эпохам',['J','T'],'A46','L66','0.0%','Отдельная шкала (FP+FN)/150, без смешения с количеством ошибок.'],
 ['Сбалансированная точность по эпохам',['H','R'],'N46','Y66','0.0%','Полусумма TPR и TNR при одном и том же классе 2.']])
 chart(sh,'line',[sh.getRange(`A5:A${eEnd}`),...cols.map(c=>sh.getRange(`${c}5:${c}${eEnd}`))],title,start,end,desc,'',format);
sh=sheets[names[4]];
const protocolResults=new Map(a.protocols.filter(r=>r.repeat===1).map(r=>[r.case,r]));
const subRows=refs.map(r=>{let measured=r.input_ids.length===150?a.first_by_job[r.job]:protocolResults.get(r.job);let mismatches=measured?r.answers.filter((v,i)=>v!==measured.answers[i]).length:null;let own=r.input_ids.filter(id=>id>=51&&id<=100).length;let tp=r.answers.filter((v,i)=>v===1&&r.input_ids[i]>=51&&r.input_ids[i]<=100).length;let fp=r.answers.filter((v,i)=>v===1&&!(r.input_ids[i]>=51&&r.input_ids[i]<=100)).length;let ntp=measured?measured.answers.filter((v,i)=>v===1&&r.input_ids[i]>=51&&r.input_ids[i]<=100).length:null;let nfp=measured?measured.answers.filter((v,i)=>v===1&&!(r.input_ids[i]>=51&&r.input_ids[i]<=100)).length:null;return [r.sheet,r.state,r.input_ids.length,r.job,tp,fp,own-tp,r.input_ids.length-own-fp,ntp,nfp,ntp==null?null:own-ntp,nfp==null?null:r.input_ids.length-own-nfp,mismatches,r.source_range];});
table(sh,'Исторические подвыборки: отдельные непрерывные последовательности',['Схема','Состояние','N','Прогон','Арх TP','Арх FP','Арх FN','Арх TN','Нов TP','Нов FP','Нов FN','Нов TN','Различий','Источник'],subRows,[54,15,10,42,...Array(8).fill(12),16,24],32);
note(sh,'Для 10 и 30 входов выполнены собственные последовательности; ответы из полного прохода не подставлялись. Лишние строки output_data не объявлены ответами без независимого подтверждения.');
let block=72;
for(const scheme of ['Схема 3 на 4','Схема 0 на 1','Схема 0 на 1(2)+4','Схема 0 на 1+4(верн. синапсы)']){
 const rows=subRows.filter(r=>r[0]===scheme).sort((x,y)=>x[1]-y[1]);if(!rows.length)continue;
 sh.getRange(`A${block}:I${block}`).values=[['Состояние','Арх TPR','Арх TNR','Арх BAcc','Нов TPR','Нов TNR','Нов BAcc','Арх риск','Нов риск']];
 sh.getRange(`A${block+1}:I${block+rows.length}`).values=rows.map(r=>{const pos=r[4]+r[6],neg=r[5]+r[7];return [r[1],r[4]/pos,neg?r[7]/neg:null,neg?.5*(r[4]/pos+r[7]/neg):null,r[8]==null?null:r[8]/pos,r[11]==null||!neg?null:r[11]/neg,r[8]==null||!neg?null:.5*(r[8]/pos+r[11]/neg),(r[5]+r[6])/r[2],r[9]==null?null:(r[9]+r[10])/r[2]];});
 sh.getRange(`B${block+1}:I${block+rows.length}`).setNumberFormat('0.0%');
 const columns=rows[0][2]===10?['B','E']:['D','G'];
 chart(sh,'line',[sh.getRange(`A${block}:A${block+rows.length}`),...columns.map(c=>sh.getRange(`${c}${block}:${c}${block+rows.length}`))],`${scheme}: ${rows[0][2]===10?'TP из 10':'сбалансированная точность'}`,`K${block}`,`W${block+20}`,'Архив и отдельный непрерывный прогон на исходной подвыборке.');
 if(rows[0][2]===30)chart(sh,'line',[sh.getRange(`A${block}:A${block+rows.length}`),...['H','I'].map(c=>sh.getRange(`${c}${block}:${c}${block+rows.length}`))],`${scheme}: доля ошибок`,`K${block+23}`,`W${block+43}`,'Нормированная доля (FP+FN)/30; классовые знаменатели не смешиваются.');
 block+=48;
}
// Baseline models compare fixed physical states, never new training.
sh=sheets[names[5]];
table(sh,'Примеры 51 и 61 и их средняя структура',['Состояние','Арх TP','Арх FP','Арх FN','Арх TN','Арх precision','Арх recall','Арх BAcc','Арх Q','Арх риск','Арх accuracy','Нов TP','Нов FP','Нов FN','Нов TN','Нов precision','Нов recall','Нов BAcc','Нов Q','Нов риск','Нов accuracy','Прогон'],
 a.baselines.map(b=>[String(b.label).startsWith('Среднее')?'Среднее':String(b.label),b.archived.TP,b.archived.FP,b.archived.FN,b.archived.TN,...Array(6).fill(null),b.measured.TP,b.measured.FP,b.measured.FN,b.measured.TN,...Array(6).fill(null),b.job]),[24,...Array(20).fill(16),24],34);
note(sh,'Источники: ВКР, таблицы 6–8; Исследование примеров. Профиль физики — архивный NL, порог распознавания 0,0115 В.');
for(let i=0;i<a.baselines.length;i++){metricFormulas(sh,i+6,6,['B','C','D','E']);metricFormulas(sh,i+6,16,['L','M','N','O']);}
chart(sh,'column',[sh.getRange('A5:A8'),sh.getRange('F5:F8'),sh.getRange('G5:G8'),sh.getRange('P5:P8'),sh.getRange('Q5:Q8')],'Базовые структуры: precision и recall','A12','L32','Сохранены исходные три базовые структуры, классификация на 150 входах.');
chart(sh,'column',[sh.getRange('A5:A8'),sh.getRange('I5:I8'),sh.getRange('S5:S8')],'Базовые структуры: число ошибок','N12','Y32','Количество ошибок FP+FN, отдельно от процентной шкалы.','','0');

const waveCache=new Map();
async function traceFor(jobId,input){
 const measured=a.first_by_job[jobId];const record=measured||protocolResults.get(jobId);if(!record)return [];
 const directory=measured?measured.directory:record.directory;
 if(!waveCache.has(directory)){
  const raw=await fs.readFile(path.join(repo,directory,'waveforms.jsonl'),'utf8');waveCache.set(directory,raw.trim().split('\n').filter(Boolean).map(x=>JSON.parse(x)));
 }
 return waveCache.get(directory).filter(x=>x.input_id===input&&x.repeat===1);
}
sh=sheets[names[6]];
table(sh,'Потенциалы сом: измеренные ряды',['Время, с','Сома 1, В','Сома 2, В','Сома 3, В','Сома 4, В','Сома 5, В','Сумма, В','LTZone','Вход'],[],[18,18,18,18,18,18,18,14,18],20);
note(sh,'Сумма вычислена из пяти нативных SumPotential. Графики показывают положительное окно 0–0,09 В; отрицательные фазы сброса сохранены в таблицах и JSONL.');
const signals=[['M001-activated',45,'Сохранённая NT45: отдельные сомы и сумма'],['M018-preserved',132,'Сохранённая NT132: отдельные сомы и сумма']];
const baselineJob=a.baselines.find(b=>String(b.label)==='51')?.job;if(baselineJob)signals.push([baselineJob,51,'Восстановленная NL51: отдельные сомы и сумма']);
for(let k=0;k<signals.length;k++){
 const [id,input,title]=signals[k],trace=await traceFor(id,input);if(!trace.length)continue;
 const first=6+k*1340,last=first+trace.length-1;
 sh.getRange(`A${first-1}:I${first-1}`).values=[['Время, с','Сома 1, В','Сома 2, В','Сома 3, В','Сома 4, В','Сома 5, В','Сумма, В','LTZone','Вход']];
 sh.getRange(`A${first}:I${last}`).values=trace.map(r=>[r.time,...r.soma,r.sum_soma,r.LTZone,r.input_id]);
 sh.getRange(`A${first}:G${last}`).setNumberFormat('0.0000');
 chart(sh,'line',[sh.getRange(`A${first-1}:A${last}`),...['B','C','D','E','F','G'].map(c=>sh.getRange(`${c}${first-1}:${c}${last}`))],title,`K${6+k*24}`,`Y${27+k*24}`,'Один входной период; потенциалы в вольтах, время от подачи входа в секундах.','','0.000');
}
const five=a.protocols.filter(r=>r.repeat===1&&r.case.includes('-five111'));
if(five.length>=2){
 const series=[];
 for(const record of five){
  const raw=await fs.readFile(path.join(repo,record.directory,'waveforms.jsonl'),'utf8');const points=raw.trim().split('\n').filter(Boolean).map(x=>JSON.parse(x));let period=-1;
  series.push({label:`${record.kind==='learner'?'NL':'NT'}111, ${record.job.threshold_control?'учебный порог 100':'порог 0,0115'}`,values:points.map(p=>{if(p.tick===0)period++;return [p.time+period*1334/2000,p.sum_soma];})});
 }
 const row=4030,last=row+series[0].values.length;
 sh.getRange(`A${row}:${col(series.length+1)}${row}`).values=[['Время, с',...series.map(s=>s.label)]];
 sh.getRange(`A${row+1}:${col(series.length+1)}${last}`).values=series[0].values.map((p,i)=>[p[0],...series.map(s=>s.values[i]?.[1]??null)]);
 chart(sh,'line',[sh.getRange(`A${row}:A${last}`),...series.map((s,i)=>sh.getRange(`${col(i+2)}${row}:${col(i+2)}${last}`))],'NL111 и NT111: фиксированные структуры и порог LTZone','K80','Y102','Пять периодов. Контроль с документированным учебным порогом 100 изолирует обратную связь LTZone при выключенном обучении. Промежуточные состояния итераций 6–10 отсутствуют.','','0.000');
}
sh.getRange('A6:I10720').format.font={name:'Arial',size:10};
sh=sheets[names[7]];
table(sh,'Входные переходы на фиксированной структуре',['Прогон','Переход','Статус','Число входов','Описание'],
 a.protocols.filter(r=>r.repeat===1&&r.case.includes('-transition')).map(r=>[r.case,r.input_ids.join(' → '),r.structure_unchanged?'Граф неизменен':'Граф изменился',r.input_ids.length,'Замороженный инференс; не динамика обучения']),[47,25,25,18,84],34);
note(sh,'Исторические переходы обучения 22→129 и 22→37 проверяются здесь как отдельная диагностика фиксированных состояний.');
let transitionRow=18;
for(const after of [129,37]){
 const candidates=a.protocols.filter(r=>r.repeat===1&&r.case.endsWith(`-transition22to${after}`));if(!candidates.length)continue;
 const columns=[];
 for(const record of candidates){
  const raw=await fs.readFile(path.join(repo,record.directory,'waveforms.jsonl'),'utf8');
  const trace=raw.trim().split('\n').filter(Boolean).map(x=>JSON.parse(x));
  const values=[];let index=-1,lastInput=null;
  for(const point of trace){if(point.tick===0)index++;values.push([point.time+index*1334/2000,point.sum_soma]);}
  columns.push({label:`NL${record.job.frozen_state_reference_id??record.job.dendrites.join(',')}`,values});
 }
 const max=columns[0].values.length;const start=transitionRow;
 sh.getRange(`A${start}:${col(columns.length+1)}${start}`).values=[['Время, с',...columns.map(c=>c.label)]];
 sh.getRange(`A${start+1}:${col(columns.length+1)}${start+max}`).values=Array.from({length:max},(_,i)=>[columns[0].values[i]?.[0]??null,...columns.map(c=>c.values[i]?.[1]??null)]);
 chart(sh,'line',[sh.getRange(`A${start}:A${start+max}`),...columns.map((c,i)=>sh.getRange(`${col(i+2)}${start}:${col(i+2)}${start+max}`))],`Смена входа 22→${after}: фиксированные структуры`,`G${18+(after===129?0:25)}`,`U${39+(after===129?0:25)}`,'Две конечные структуры NL; обучение отключено. Конечное состояние перехода взято из первой серии протоколов переобучения.','','0.000');
 transitionRow+=max+20;
}
sh.getRange('A18:D16100').format.font={name:'Arial',size:10};sh.getRange('A18:D16100').setNumberFormat('0.0000');
// Six input projections reproduce the source data, not a neuronal response.
sh=sheets[names[8]];
table(sh,'Проекции нормированных Iris-входов',['ID','Класс','d1, с','d2, с','d3, с','d4, с','d5, с'],d.dataset.map(r=>[r.id,r.class,...r.pattern]),[10,12,...Array(5).fill(17)],21);
note(sh,'Источник: Протоколы экспериментов.xlsx, лист Датасет. Шесть проекций; выделены десять эталонов и примеры 51 и 61.');
const pairs=[[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]],selected=new Set([22,37,45,60,64,84,90,111,129,134]);
for(let i=0;i<6;i++){
 const [x,y]=pairs[i],start=10+i*14;
 const groups=[...[1,2,3].map(k=>({label:`Класс ${k}`,rows:d.dataset.filter(r=>r.class===k)})),{label:'10 эталонов',rows:d.dataset.filter(r=>selected.has(r.id))},{label:'Пример 51',rows:d.dataset.filter(r=>r.id===51)},{label:'Пример 61',rows:d.dataset.filter(r=>r.id===61)}];
 for(let k=0;k<groups.length;k++){
  const g=groups[k],xcol=col(start+2*k),ycol=col(start+2*k+1),last=5+g.rows.length;
  sh.getRange(`${xcol}5:${ycol}${last}`).values=[[`d${x+1}, с`,g.label],...g.rows.map(r=>[r.pattern[x],r.pattern[y]])];
  g.xref=`'${sh.name}'!${xcol}6:${xcol}${last}`;g.yref=`'${sh.name}'!${ycol}6:${ycol}${last}`;
 }
 const c=chart(sh,'scatter',[sh.getRange(`${col(start)}5:${col(start)}55`),sh.getRange(`${col(start+1)}5:${col(start+1)}55`)],`Проекция d${x+1} и d${y+1}, секунды`,i%2===0?`A${160+Math.floor(i/2)*24}`:`J${160+Math.floor(i/2)*24}`,i%2===0?`I${181+Math.floor(i/2)*24}`:`R${181+Math.floor(i/2)*24}`,'Координаты и классы повторены из архивных исходных данных. Каждый класс содержит ровно 50 точек; пустые наблюдения и соединительные линии отсутствуют.','','0.00');
 groups.forEach((g,k)=>{const s=k===0?c.series.items[0]:c.series.add(g.label);s.name=g.label;s.xValuesSource=g.xref;s.valuesSource=g.yref;s.line={fill:'none',width:0,style:'solid'};});
 c.xAxis.min=0;c.yAxis.min=0;c.xAxis.numberFormatCode='0.00';
}
sh.getRange('J5:CM155').format.font={name:'Arial',size:10};
sh=sheets[names[9]];
const measuredEntries=Object.entries(a.first_by_job).filter(([k,r],i,arr)=>arr.findIndex(([,x])=>x.case===r.case)===i);
const answerHeaders=['ID','Класс',...d.recognition_reference.map(r=>`Арх ${r.kind==='trainer'?'NT':'NL'}${r.id} ${r.variant}`),...measuredEntries.map(([key])=>key)];
table(sh,'Ответы на каждый вход: архив и все уникальные измерения',answerHeaders,d.dataset.map((r,i)=>[r.id,r.class,...d.recognition_reference.map(c=>c.answers[i]),...measuredEntries.map(([,m])=>m.answers[i]??null)]),answerHeaders.map((h,i)=>i<2?10:24),23);
note(sh,'Архивные ответы сохранены без изменений. Одинаковые измерения представлены одной колонкой; связь с источниками — в реестре структур.');sh.freezePanes.freezeColumns(2);
sh=sheets[names[10]];
const byRow=new Map(mapping.map(r=>[r.row,r]));
table(sh,'Каждая исходная структурная запись и её восстановление',['Запись','Алгоритм','Исторический случай','Статус','Прогон','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5','Источник','Дополняющий источник'],
 d.restoration_rows.map(r=>{const m=byRow.get(r.id);const job=jobs.find(j=>j.id===m?.job);return [r.id,r.kind,r.label,m?.status==='constructed'?'Восстановлено':'Недостаточно данных',m?.job??'',...(r.dendrites||Array(5).fill(null)),...(job?.synapses||r.synapses||Array(5).fill(null)),r.source,(m?.completion_donors||[]).join(', ')];}),
 [12,16,53,27,24,...Array(10).fill(8),110,48],34);
note(sh,'136 исходно неполных строк: 5 дополнены по однозначным совпадениям, 131 сохранена как пробелы данных. Структурные записи не считаются независимыми повторами эксперимента.');
sh=sheets[names[11]];
const conditional=new Set(['G03','G04','G05','G06','G07','G08']);
table(sh,'Покрытие семейств исторических графиков',['Семейство','Описание','Результат','Исторический источник','Условие сравнения'],d.families.map(f=>[f.id,f.name,conditional.has(f.id)?'Условная часть: архив сохранён; фиксированная модель не воспроизводит обучение':'Проверено по доступным данным',f.sources,f.comparison]),[17,70,95,100,110],53);
note(sh,'Внешние книги и статьи использованы как теоретические источники. Неполные состояния и недоступные траектории не выданы за воспроизведённые.');
sh.getRange('A28:F28').values=[['Источник','Путь в архиве','Роль','Канонический источник','SHA256','Размер байт']];
sh.getRange(`A29:F${28+d.documents.length}`).values=d.documents.map(r=>[r.id,r.path,r.role,r.canonical_doc,r.sha256,r.bytes]);
sh.getRange(`A29:F${28+d.documents.length}`).format.rowHeight=38;sh.getRange(`A29:F${28+d.documents.length}`).format.wrapText=true;
sh=sheets['Оцифровка'];
const digitized=await read(path.join(work,'digitized-waves.json'));
const pixelRows=digitized.flatMap(c=>c.points.map(p=>[c.id,p.pixel_x,p.pixel_y,p.time,p.potential,p.time_uncertainty,p.potential_uncertainty,p.pixel_y_min,p.pixel_y_max,c.source,c.source_asset_sha256]));
table(sh,'Оцифровка архивных кривых и оценка неопределённости',['Источник','X пиксель','Y медиана','Время, с','Потенциал, В','Граница Δt, с','Граница ΔU, В','Y минимум','Y максимум','Рисунок','SHA256 исходного изображения'],pixelRows,[16,15,15,19,19,20,20,16,16,60,74],29);
note(sh,'Время: линейная калибровка по видимым подписям с округлением до 0,1 с. Потенциал: шкала 0–0,090 В. Сохранены пиксели, толщина штриха и консервативные границы неопределённости.');
sh.getRange(`D6:G${pixelRows.length+5}`).setNumberFormat('0.000000');
sh.getRange('M5:R9').values=[['Рисунок','Секунд / пиксель','Свободный член','Нулевая линия Y','Верх шкалы Y','Невязка меток, с'],...digitized.map(c=>[c.id,c.time_slope,c.time_intercept,c.voltage_zero_pixel,c.voltage_top_pixel,c.tick_fit_max_residual])];
for(let i=0;i<digitized.length;i++){
 const c=digitized[i],bytes=await fs.readFile(c.image),w=bytes.readUInt32BE(16),h=bytes.readUInt32BE(20),row=12+i*35;
 sh.getRange(`M${row}`).values=[[c.source]];
 sh.images.add({dataUrl:'data:image/png;base64,'+bytes.toString('base64'),anchor:{from:{row:row,col:12},extent:{widthPx:900,heightPx:900*h/w}}});
}
sh=sheets['Сопоставление осциллограмм'];
table(sh,'Архивные кривые и новые измерения',['Время относительно первого максимума, с','Потенциал, В'],[],[33,22],20);
note(sh,'Один постоянный сдвиг начала времени; амплитуды и временной масштаб сохранены. Общая сетка используется только для линейной интерполяции при отображении, исходные точки сохранены.');
const overlays=await read(path.join(work,'overlays.json'));let overlayRow=6;
for(let i=0;i<overlays.length;i++){
 const o=overlays[i],last=overlayRow+o.rows.length;
 sh.getRange(`A${overlayRow}:${col(o.headers.length)}${last}`).values=[o.headers,...o.rows];
 sh.getRange(`B1:G${last}`).format.columnWidth=24;
 sh.getRange(`A${overlayRow}:${col(o.headers.length)}${overlayRow}`).format.wrapText=true;sh.getRange(`A${overlayRow}:${col(o.headers.length)}${overlayRow}`).format.rowHeight=44;
 sh.getRange(`A${overlayRow}:${col(o.headers.length)}${last}`).format.font={name:'Arial',size:10};sh.getRange(`A${overlayRow+1}:${col(o.headers.length)}${last}`).setNumberFormat('0.0000');
 chart(sh,'line',[sh.getRange(`A${overlayRow}:A${last}`),...o.headers.slice(1).map((_,k)=>sh.getRange(`${col(k+2)}${overlayRow}:${col(k+2)}${last}`))],o.title,`I${6+i*25}`,`W${27+i*25}`,
  `Оцифрованный архив обучения и фиксированный инференс. Максимальная граница неопределённости времени архива ${o.time_uncertainty_max.toFixed(3)} с; точные границы потенциала — на листе Оцифровка.`,'','0.000');
 overlayRow=last+15;
}
sh=sheets['Контекст проекта'];
const context=(a.context||[]).filter(r=>r.repeat===1);
table(sh,'Исходная активность и полный родительский проект',['Режим','Модель','Обучающий ID','N входов','Граф при загрузке','Граф при расчёте','Обучение выключено','BAcc на 150','Q на 150','Неинициализированных активных объектов'],
 context.map(r=>[r.case,r.job.source_model,r.job.target_id,r.answers.length,r.graph_loading.passed,r.graph_inference.passed,r.training_disabled,r.answers.length===150?r.metrics.balanced_accuracy:null,r.answers.length===150?r.metrics.Q:null,r.whole_initialization_audit?.uninitialized.length??null]),[42,15,18,16,24,24,24,20,17,32],34);
note(sh,'В полном проекте сохранены активность и боковые связи; обучение всех 18 тренеров выключено. Промежуточные состояния соседей не объявлены завершённо обученными.');
const isolated=context.find(r=>r.case==='M018-autonomous-context12');
const driven=context.find(r=>r.case==='M018-parent-driven-context12'),full=context.find(r=>r.case==='M018-full-context');
if(isolated&&driven&&full){
 sh.getRange('A21:E24').values=[['M018: режим','BAcc','Precision','Recall','Q'],...[[isolated,'Собственные источники'],[driven,'Транзит, без соседей'],[full,'Полный родительский проект']].map(([r,label])=>[label,r.metrics.balanced_accuracy,r.metrics.precision,r.metrics.recall,r.metrics.Q])];
 sh.getRange('B22:D24').setNumberFormat('0.0%');
 chart(sh,'bar',[sh.getRange('A21:A24'),sh.getRange('B21:B24'),sh.getRange('C21:C24'),sh.getRange('D21:D24')],'M018: три режима на 12 контрольных входах','A28','N49','Одинаковая структура M018 и один порядок 12 входов; отдельный транзитный контроль отделяет способ подачи стимулов от наличия соседних нейронов и боковых связей. Основные сравнения сохранённых моделей выполнены на 150 входах.');
}
sh=sheets['Сохранённые модели'];
sh.getRange('A42:L51').values=[['Модель','Обучающий ID','d1','d2','d3','d4','d5','s1','s2','s3','s4','s5'],...fullSaved.map(r=>[r.job.source_model,r.job.target_id,...r.dendrites,...r.synapses])];
sh.getRange('A42:L42').format={fill:colors.header,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:28};
sh.getRange('A43:L51').format={font:{name:'Arial',size:10},rowHeight:25};
sh.getRange('A54:E63').values=[['Модель','Σd архив','Σd инференс','Σs архив','Σs инференс'],...fullSaved.map(r=>[r.job.source_model,r.job.dendrites.reduce((x,y)=>x+y,0),r.dendrites.reduce((x,y)=>x+y,0),r.job.synapses.reduce((x,y)=>x+y,0),r.synapses.reduce((x,y)=>x+y,0)])];
chart(sh,'column',[sh.getRange('A54:A63'),...['B','C','D','E'].map(c=>sh.getRange(`${c}54:${c}63`))],'Сохранённые модели: структура до и после инференса','A66','N87','Σd — сумма пяти записанных длин; Σs — сумма пяти терминальных чисел синапсов. Все десять значений приведены отдельно; полное совпадение физического графа проверено независимо.','','0');
sh=sheets['Эпохи'];
sh.getRange('AA5:AG19').values=[['Эпоха','Арх TNR','Нов TNR','Арх FPR','Нов FPR','Арх FNR','Нов FNR'],...a.epochs.map(e=>[e.epoch,...Array(6).fill(null)])];
for(let i=0;i<a.epochs.length;i++){
 const r=i+6;
 sh.getRange(`AB${r}:AG${r}`).formulas=[[`=IFERROR(E${r}/(E${r}+C${r}),"")`,`=IFERROR(O${r}/(O${r}+M${r}),"")`,`=IFERROR(C${r}/(C${r}+E${r}),"")`,`=IFERROR(M${r}/(M${r}+O${r}),"")`,`=IFERROR(D${r}/(D${r}+B${r}),"")`,`=IFERROR(N${r}/(N${r}+L${r}),"")`]];
}
sh.getRange('AA5:AG19').format={font:{name:'Arial',size:10},columnWidth:17,rowHeight:25};sh.getRange('AB6:AG19').setNumberFormat('0.0%');
chart(sh,'line',[sh.getRange('A5:A19'),sh.getRange('G5:G19'),sh.getRange('Q5:Q19'),sh.getRange('AB5:AB19'),sh.getRange('AC5:AC19')],'TPR и TNR по эпохам','A69','L89','TPR=TP/(TP+FN), TNR=TN/(TN+FP); архив и новое измерение на одних и тех же 150 входах.');
chart(sh,'line',[sh.getRange('AA5:AA19'),...['AD','AE','AF','AG'].map(c=>sh.getRange(`${c}5:${c}19`))],'FPR и FNR по эпохам','N69','Y89','FPR=FP/(FP+TN), FNR=FN/(FN+TP). Кривые ошибок по классам дополняют график Q как количества ошибок.');
await fs.mkdir(out,{recursive:true});await fs.mkdir(path.join(work,'xlsx-qa'),{recursive:true});
wb.recalculate();console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:20},maxChars:1000})).ndjson);
// A real input perturbation must update the dependent classification build.
const test=sheets[names[0]],original=test.getRange('G6').values;test.getRange('G6').values=[[0]];wb.recalculate();const changed=test.getRange('K6:P6').values;test.getRange('G6').values=original;wb.recalculate();
await fs.writeFile(path.join(work,'formula-check.json'),JSON.stringify({changed,restored:test.getRange('K6:P6').values},null,2));
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(out,'LegacyModelChecks.xlsx'));
await fs.writeFile(path.join(work,'figures.json'),JSON.stringify(figures,null,2));
for(let i=0;i<previews.length;i++){let p=previews[i];const blob=await wb.render({sheetName:p.sheet,range:p.range,scale:1.2,format:'png'});await fs.writeFile(path.join(work,'xlsx-qa',`sheet-${i+1}.png`),new Uint8Array(await blob.arrayBuffer()));}
for(const f of figures){const blob=await wb.render({sheetName:f.sheet,range:f.range,scale:1.2,format:'png'});await fs.writeFile(path.join(work,'xlsx-qa',f.id+'.png'),new Uint8Array(await blob.arrayBuffer()));}
await fs.writeFile(path.join(work,'figures.json'),JSON.stringify(figures,null,2));console.log(path.join(out,'LegacyModelChecks.xlsx'));
