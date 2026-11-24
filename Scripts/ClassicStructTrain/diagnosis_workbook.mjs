import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const work = path.join(root, 'Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124');
const delivery = path.join(root, 'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/DiscrepancyDiagnosis');
const read = async name => JSON.parse(await fs.readFile(path.join(work, name), 'utf8'));
const data = await read('diagnosis-analysis.json');
const report = await read('diagnosis-report.json');
const historical = await read('archival-answers.json');
const source = await read('source-audit.json');
const workbook = Workbook.create();
const chartIndex = [];

function col(index) {
  let name = '';
  for (let cursor = index; cursor; cursor = Math.floor((cursor - 1) / 26))
    name = String.fromCharCode(65 + (cursor - 1) % 26) + name;
  return name;
}

function table(name, title, headers, rows, widths = []) {
  const sheet = workbook.worksheets.add(name);
  const end = col(headers.length);
  sheet.showGridLines = false;
  sheet.getRange(`A1:${end}1`).merge();
  sheet.getRange('A1').values = [[title]];
  sheet.getRange('A1').format = { font: { name: 'Arial', size: 17, bold: true }, rowHeight: 36, wrapText: true };
  sheet.getRange(`A3:${end}3`).values = [headers];
  sheet.getRange(`A3:${end}3`).format = {
    fill: '#29455E', font: { name: 'Arial', size: 11, bold: true, color: '#FFFFFF' },
    rowHeight: 34, wrapText: true,
  };
  for (let start = 0; start < rows.length; start += 1000) {
    const block = rows.slice(start, start + 1000);
    sheet.getRange(`A${start + 4}:${end}${start + block.length + 3}`).values = block;
  }
  headers.forEach((_, i) => {
    const letter = col(i + 1);
    sheet.getRange(`${letter}:${letter}`).format.columnWidth = widths[i] ?? 18;
  });
  sheet.freezePanes.freezeRows(3);
  return sheet;
}

table('Обзор', 'Диагностика расхождений NMSDK', ['Наблюдение', 'Результат', 'Граница вывода'],
  report.overview, [52, 24, 88]);
table('Источники и состояния', 'Соответствие исторических файлов и исходных ячеек',
  ['Лист', 'Состояние', 'Диапазон', 'Файл', 'SHA256', 'Число ответов', 'Лишние значения', 'Дендриты и синапсы'],
  source.protocols.map(r => [r.sheet, r.state, r.range, r.file, r.file_sha256, r.mapped_answers,
    r.unmapped_answer_lines.join(', '), r.graph_ds.join(', ')]), [44, 15, 18, 64, 68, 18, 18, 34]);
const raw = table('Архивные ответы', 'Исходные ответы и ответы двух предыдущих серий',
  ['Модель', 'Стартовый снимок', 'Объект Iris', 'Ячейка', 'История', 'Проверка снимка', 'Новое обучение',
   'Различие со снимком', 'Различие с новым', 'Файл', 'SHA256', 'Журнал проверки', 'Журнал новой модели'],
  historical.map(r => [r.experiment, r.state, r.input_id, r.cell, r.historical, r.previous, r.trained,
    null, null, r.source, r.sha256, r.previous_log, r.trained_log]), [18, 16, 14, 14, 12, 18, 18, 19, 20, 48, 68, 50, 56]);
raw.getRange(`H4:I${historical.length + 3}`).formulas = historical.map((_, index) => {
  const row = index + 4;
  return [`=ABS(E${row}-F${row})`, `=ABS(E${row}-G${row})`];
});
table('Опыты инференса', 'Обратные контроли на неизменных графах',
  ['Модель', 'Фактор', 'Повтор', 'Изменилось', 'Возврат', 'История до', 'История после', 'TP до', 'FP до', 'FN до',
   'TN до', 'TP после', 'FP после', 'FN после', 'TN после', 'Журнал вмешательства'],
  data.inference_comparisons.map(r => [r.label, r.factor, r.repeat, r.changed.length, r.reversal ? 'да' : 'нет',
    r.history_diff_before, r.history_diff_after, ...Object.values(r.metrics_before), ...Object.values(r.metrics_after),
    r.logs[1]]), [20, 16, 12, 15, 12, 17, 17]);
table('Изменённые ответы', 'Ответ и запас до порога для каждого переключения',
  ['Модель', 'Фактор', 'Повтор', 'Объект Iris', 'До', 'После', 'История', 'До, мкВ', 'После, мкВ', 'Первый такт до', 'Первый такт после', 'Журнал'],
  data.inference_comparisons.flatMap(r => r.changed.map(c => [r.label, r.factor, r.repeat, c.id, c.before,
    c.after, c.historical, c.margin_before_uV, c.margin_after_uV, c.first_zone_before, c.first_zone_after, r.logs[1]])),
  [22, 17, 12, 14, 10, 10, 12, 16, 16, 19, 19, 58]);
table('Траектории обучения', 'Нативные результаты и ограничения',
  ['Серия', 'Задание', 'Статус', 'Причина', 'Итерации', 'Такты', 'Модельное время, с', 'Время запуска, с',
   'Дендриты', 'Синапсы', 'Свой вход', 'Журнал'],
  data.training.map(r => [r.phase, r.run, r.status, r.stop_reason, r.iterations, r.ticks, r.elapsed_model_s,
    r.elapsed_wall_s, r.d.join(', '), r.s.join(', '), r.own_recognized, r.directory]),
  [23, 43, 27, 34, 13, 13, 18, 18, 22, 22, 15, 58]);
table('Физические параметры', 'Параметры в сохранённом графе после обучения',
  ['Серия', 'Задание', 'Сопротивление, Ом', 'Секреция, с', 'Диссоциация, с', 'Число компонентов'],
  data.training.flatMap(r => r.profile.map(p => [r.phase, r.run, +p.resistance_ohm, +p.secretion_s,
    +p.dissociation_s, p.components])), [25, 48, 23, 18, 21, 22]);
table('Контекст обучения', 'Живой тест, отдельный снимок и пауза',
  ['Схема', 'Повтор', 'Этап стенда', 'Итерации живой', 'Итерации снимок', 'Итерации пауза', 'Ошибки живой', 'Ошибки снимок',
   'Длины живой', 'Длины снимок', 'Длины пауза', 'Синапсы живой', 'Синапсы снимок', 'Синапсы пауза'],
  data.sequence_context.map(r => [r.scheme, r.repeat, r.stage, ...r.iterations, r.live_Q, r.snapshot_Q,
    ...r.d.map(x => x.join(', ')), ...r.s.map(x => x.join(', '))]), [20, 13, 14, 18, 18, 18, 18, 18]);
table('Первые различия', 'Первый наблюдаемый такт расхождения по сигналу',
  ['Модель', 'Фактор', 'Объект Iris', 'Величина', 'Такт', 'Время до, с', 'Время после, с', 'Трасса'],
  data.tick_comparisons.flatMap(r => r.first_events.map(e => [r.label, r.factor, e.input_id, e.quantity,
    e.tick, e.baseline_time_s, e.changed_time_s, r.logs[1]])), [24, 18, 16, 23, 13, 18, 18, 58]);
table('Первые учебные различия', 'Сравнение решений и состояний обучения по общему префиксу',
  ['Фактор', 'Задание', 'Первая запись', 'Поля', 'Первые такты по величине', 'Итерации до', 'Итерации после',
   'Статус до', 'Статус после', 'База', 'Изменение'],
  data.training_comparisons.map(r => [r.factor, r.job, r.first_difference?.record,
    r.first_difference?.fields.join(', '), Object.entries(r.first_training_ticks).map(([k,v])=>k+' '+v).join(', '),
    ...r.iterations, ...r.status, ...r.logs]), [46, 28, 18, 32, 43, 17, 17, 24, 24, 58, 58]);
table('Запуски', 'Идентификация независимых процессов',
  ['Серия', 'Задание', 'Статус', 'Время, с', 'SHA256 программы', 'SHA256 задания', 'Журнал'],
  data.processes.map(p => [p.phase, p.run, p.status, p.seconds, p.binary_sha256, p.manifest_sha256, p.path]),
  [24, 42, 24, 16, 68, 68, 60]);

const palette = ['#606972', '#166280', '#A35627', '#54765A'];
for (const figure of report.sections.flatMap(section => section.charts ?? [])) {
  const { id, title, headers, rows, min, max, x, y } = figure;
  const sheet = table(id, title, headers, rows, [36, ...headers.slice(1).map(() => 21)]);
  const chart = sheet.charts.add(figure.type ?? 'line',
    headers.map((_, index) => sheet.getRange(`${col(index+1)}3:${col(index+1)}${rows.length+3}`)));
  const top = Math.max(rows.length + 6, 12);
  chart.setPosition(`A${top}`, `P${top + 22}`);
  chart.title = title;
  chart.displayBlanksAs = 'gap';
  chart.titleTextStyle.fontSize = 15;
  chart.legend = { position: 'top', textStyle: { fontSize: 11 } };
  chart.xAxis = { axisType: 'textAxis', title: { text: x }, textStyle: { fontSize: 11 } };
  chart.yAxis = { min, max, title: { text: y }, textStyle: { fontSize: 11 },
    numberFormatCode: figure.format ?? '0', numberFormatSourceLinked: false };
  chart.series.items.forEach((series, index) => {
    const color = palette[index % palette.length];
    series.fill = color;
    if (!figure.type || figure.type === 'line') {
      series.line = { fill: color, width: 2, style: 'dashed' };
      series.marker = { symbol: ['circle', 'square', 'diamond', 'triangle'][index % 4], size: 10,
        fill: index === 0 ? 'none' : color, line: { fill: color, width: 1.4 } };
    }
  });
  chartIndex.push({ id, min, max, rows, x, y });
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await fs.mkdir(delivery, { recursive: true });
await xlsx.save(path.join(delivery, 'DiscrepancyDiagnosis.xlsx'));
await fs.writeFile(path.join(work, 'chart-index.json'), JSON.stringify(chartIndex, null, 2));
