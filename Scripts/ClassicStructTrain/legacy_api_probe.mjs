import {Workbook} from '@oai/artifact-tool';
const wb=Workbook.create();
console.log(wb.help('*',{search:'axis',include:'index,examples,notes',maxChars:6500}).ndjson);
