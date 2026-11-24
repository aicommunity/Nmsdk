// Small native-Excel visual check before rendering the complete workbook.
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const repo=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'../..');
try{
const wb=Workbook.create(),sh=wb.worksheets.add('Style');
sh.getRange('A1:B4').values=[['X','Class 1'],[.02,.03],[.06,.08],[.11,.14]];
sh.getRange('D1:E2').values=[['X','Class 2'],[.15,.18]];
const c=sh.charts.add('scatter',[sh.getRange('A1:A4'),sh.getRange('B1:B4')]);c.title='Compact scatter, no artificial zeros';c.setPosition('G2','Q20');
c.apply({scatterOptions:{style:'marker'}});c.displayBlanksAs='gap';
const a=c.series.items[0];a.xValuesSource="'Style'!A2:A4";a.valuesSource="'Style'!B2:B4";a.line={fill:'none',width:0,style:'solid'};
const b=c.series.add('Class 2');b.xValuesSource="'Style'!D2:D2";b.valuesSource="'Style'!E2:E2";b.line={fill:'none',width:0,style:'solid'};
c.xAxis={min:0,max:.2};c.yAxis={min:0,max:.2,minorGridlines:null,majorGridlines:{fill:'#D7DEE5',width:.6,style:'solid'}};
sh.getRange('A7:B11').values=[['Time','Measured'],[0,0],[.1,.04],[.2,-1.9],[.3,.01]];
const l=sh.charts.add('line',[sh.getRange('A7:A11'),sh.getRange('B7:B11')]);l.title='Positive voltage window; negative reset retained in cells';l.setPosition('G23','Q42');
l.series.items[0].marker={symbol:'circle',size:9,fill:'none',line:{fill:'#176A8A',width:1.5,style:'solid'}};
l.series.items[0].line={style:'dashed',fill:'#176A8A',width:2};
l.yAxis={min:0,max:.09,numberFormatCode:'0.000',minorGridlines:null,majorGridlines:{fill:'#D7DEE5',width:.6,style:'solid'}};
const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(repo,'Reports/StructTrainClassic/_work/LegacyChecks-20261123/chart-style-check.xlsx'));console.log('Style check exported');
}catch(e){console.error(e.message);process.exit(1);}
