import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const work = path.join(root, 'Reports/StructTrainClassic/DiscrepancyDiagnosis-20261124');
const checkpoint = process.argv.includes('--checkpoint');
const delivery = checkpoint ? path.join(work, 'checkpoint') :
  path.join(root, 'Reports/StructTrainClassic/outputs/01a20798-0fce-7661-bd9d-b3506770ffc9/DiscrepancyDiagnosis');
const read = async name => JSON.parse(await fs.readFile(path.join(work, name), 'utf8'));
const data = await read('diagnosis-analysis.json');
const report = await read('diagnosis-report.json');
const historical = await read('archival-answers.json');
const source = await read('source-audit.json');
const coverage = await read('diagnosis-coverage.json');
const runtime = await read('runtime-provenance.json');
const history = JSON.parse(await fs.readFile(path.join(root,
  'Reports/StructTrainClassic/TrainingReproducibility-20261123/history.json'), 'utf8'));
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
const findings = table('Статусы причин', 'Степень подтверждения причин и границы измерений',
  ['Наблюдение', 'Статус', 'Основание'], report.findings, [50, 39, 78]);
findings.getRange(`A4:C${report.findings.length + 3}`).format = { rowHeight: 43, wrapText: true };
table('Источники и состояния', 'Соответствие исторических файлов и исходных ячеек',
  ['Лист', 'Состояние', 'Диапазон', 'Файл', 'SHA256', 'Число ответов', 'Лишние значения', 'Дендриты и синапсы'],
  source.protocols.map(r => [r.sheet, r.state, r.range, r.file, r.file_sha256, r.mapped_answers,
    r.unmapped_answer_lines.join(', '), r.graph_ds.join(', ')]), [44, 15, 18, 64, 68, 18, 18, 34]);
table('Датировка источников', 'Даты редактирования документов и сохранения конфигураций',
  ['Источник', 'Создан', 'Изменён', 'Сохранения конфигурации', 'SHA256'],
  history.documents.map(r => [r.path, r.created, r.modified, r.saves?.join(', '), r.sha256]), [62, 28, 28, 72, 68]);
table('Ревизии PulseLib', 'Изменения PulseLib по датам из предшествующей проверки',
  ['Ревизия', 'Дата автора', 'Сообщение коммита', 'Предмет проверки', 'SHA256 патча', 'Патч'],
  history.commits.map(r => [r.sha, r.author_date, r.subject, r.factor, r.patch_sha256, r.patch]),
  [47, 29, 64, 61, 68, 61]);
if (source.retained_order_variants?.length) {
  table('Сборки порядка', 'Происхождение раздельно собранных вариантов изменения порядка',
    ['Условие', 'SHA256 бинарника', 'Ревизия PulseLib', 'Ревизия Rdk',
     'SHA256 контроллера', 'SHA256 адаптера обучения'],
    source.retained_order_variants.map(r => [r.id, r.binary_sha256, r.pulselib_sha, r.rdk_sha,
      r.controller_sha256, r.training_adapter_sha256]), [16, 68, 48, 48, 68, 68]);
}
const historicalSchemes = new Map([['Схема 0 на 1', ['0_1', 1]],
  ['Схема 0 на 1+4 для 150 примеров', ['0_1_4_full', 2]]]);
const protocolLabels = { '0_1': 'Одиночные итерации для № 61',
  '0_1_4_full': 'Переход № 51 → № 61 с настройкой синапсов' };
const byContext = new Map(data.sequence_context.filter(r => r.repeat === 1)
  .map(r => [r.scheme + '/' + r.stage, r]));
const perStimulus = source.protocols.flatMap(r => {
  const link = historicalSchemes.get(r.sheet);
  const observed = link && byContext.get(link[0] + '/' + ((r.state - 1) * link[1]));
  const column = r.range.split('2:')[0];
  return (r.input_ids ?? []).map((id, index) => [r.sheet, r.state, r.job, id, column + (index + 2),
    r.file, index + 2, r.file_sha256, r.answers[index], observed?.live_answers?.[index],
    observed?.snapshot_answers?.[index], observed?.snapshot_log]);
});
table('Ответы исторических схем', 'Первичные ответы и новые измерения в первом повторе',
  ['Лист', 'Состояние', 'Граф из прошлого отчёта', 'Объект Iris', 'Ячейка', 'Файл первичных ответов',
   'Строка файла', 'SHA256', 'Исторический ответ', 'Живой тест', 'Инференс снимка', 'Журнал инференса снимка'],
  perStimulus, [43, 14, 24, 15, 13, 61, 17, 68, 19, 16, 19, 57]);
table('Пересчёт архивных итогов', 'Проверка итоговых ячеек по первичным ответам',
  ['Лист', 'Состояние', 'Ячейка итога', 'Показатель', 'Пересчёт', 'Формула или формула общей группы',
   'Общая формула', 'Строки ответов', 'SHA256'],
  source.protocols.flatMap(r => (r.summary_audit ?? []).map(m => [r.sheet, r.state, m.cell, m.metric,
    m.recalculated, m.formula, m.shared_formula ? 'да' : 'нет', m.answer_rows?.join('–'), r.sha256])),
  [43, 14, 16, 15, 18, 42, 17, 18, 68]);
if (source.structure) {
  const p = source.structure;
  table('Структурный источник', 'Исторические длины и числа синапсов NT и NL',
    ['Запись', 'Объект', 'Алгоритм', 'Вариант', 'Лист', 'Ячейки длин', 'Ячейки синапсов', 'Длины',
     'Синапсы в источнике', 'Использовано для графа', 'Файл', 'SHA256', 'Проверка'],
    p.rows.map(r => [r.record, r.input_id, r.algorithm, r.label, p.sheet, r.length_range, r.synapse_range,
      r.dendrites.join(', '), r.original_synapses.map(v => v ?? '—').join(', '),
      r.effective_synapses?.join(', '), p.path, p.sha256, r.directory]),
    [15, 13, 14, 33, 26, 21, 21, 26, 30, 24, 56, 68, 58]);
}
if (data.order_structure?.length) {
  table('Длины в контрольной десятке', 'Длины дендритов из первичной книги и двух учебных условий',
    ['Сборки', 'Алгоритм', 'Объект', 'Ячейки', 'Исторические длины', 'Длины исходные', 'Длины без перестановки',
     'Исходное совпадение', 'Совпадение без вызова', 'Файл', 'SHA256', 'Журнал исходный', 'Журнал без вызова'],
    data.order_structure.map(r => [r.matched ? 'Одна' : 'Раздельные', r.kind, r.target, r.cells.join(', '),
      r.historical_d.map(d=>d.join(', ')).join(' / '),
      r.native_d.join(', '), r.disabled_d.join(', '), r.native_matches ? 'да' : 'нет',
      r.disabled_matches ? 'да' : 'нет', r.source, r.sha256, ...r.logs]),
    [17, 14, 12, 21, 28, 25, 25, 22, 22, 62, 68, 60, 60]);
}
if (data.order_rechecks?.length) {
  table('Перепроверка сборок', 'Результаты повторения опытов на одном исполняемом файле',
    ['Задание', 'Совпали статус, итерации и структура', 'Журнал раздельных сборок', 'Журнал одной сборки'],
    data.order_rechecks.map(r => [r.job, r.same ? 'да' : 'нет', r.previous_log, r.matched_log]),
    [38, 36, 65, 65]);
}
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
   'TN до', 'TP после', 'FP после', 'FN после', 'TN после', 'Входов', 'Тип наблюдения', 'Возврат физического сигнала',
   'Макс. изменение пика, мкВ', 'Объект макс. изменения', 'Макс. сдвиг времени ответа, с', 'Журнал вмешательства'],
  data.inference_comparisons.map(r => [r.label, r.factor, r.repeat, r.changed.length, r.reversal ? 'да' : 'нет',
    r.history_diff_before, r.history_diff_after, ...Object.values(r.metrics_before), ...Object.values(r.metrics_after),
    r.tested_inputs, r.observation_mode, r.physical_reversal ? 'да' : 'нет', r.largest_peak_change_uV,
    r.largest_peak_change_id, r.largest_response_delay_change_s, r.logs[1]]), [20, 16, 12, 15, 12, 17, 17]);
table('Изменённые ответы', 'Ответ и запас до порога для каждого переключения',
  ['Модель', 'Фактор', 'Повтор', 'Объект Iris', 'До', 'После', 'История', 'До, мкВ', 'После, мкВ', 'Первый такт до', 'Первый такт после', 'Журнал'],
  data.inference_comparisons.flatMap(r => r.changed.map(c => [r.label, r.factor, r.repeat, c.id, c.before,
    c.after, c.historical, c.margin_before_uV, c.margin_after_uV, c.first_zone_before, c.first_zone_after, r.logs[1]])),
  [22, 17, 12, 14, 10, 10, 12, 16, 16, 19, 19, 58]);
table('Траектории обучения', 'Нативные результаты и ограничения',
  ['Серия', 'Задание', 'Статус', 'Причина', 'Итерации', 'Такты', 'Модельное время, с', 'Время запуска, с',
   'Дендриты', 'Синапсы', 'Свой вход', 'Пик LTZone, мВ', 'Журнал обучения', 'Журнал своего входа'],
  data.training.map(r => [r.phase, r.run, r.status, r.stop_reason, r.iterations, r.ticks, r.elapsed_model_s,
    r.elapsed_wall_s, r.d.join(', '), r.s.join(', '), r.own_recognized, r.own_zone_mV, r.directory, r.own_log]),
  [23, 43, 27, 34, 13, 13, 18, 18, 22, 22, 15, 19, 58]);
table('Физические параметры', 'Параметры в сохранённом графе после обучения',
  ['Серия', 'Задание', 'Сопротивление, Ом', 'Секреция, с', 'Диссоциация, с', 'Число компонентов'],
  data.training.flatMap(r => r.profile.map(p => [r.phase, r.run, +p.resistance_ohm, +p.secretion_s,
    +p.dissociation_s, p.components])), [25, 48, 23, 18, 21, 22]);
table('Профиль фиксированного графа', 'Применённые параметры синапса при инференсе без обучения',
  ['Модель', 'Профиль', 'Повтор', 'Срабатывания TP', 'Ложные FP', 'Пропуски FN', 'Отказы TN', 'Изменённые ID',
   'Сопротивление, Ом', 'Секреция, с', 'Диссоциация, с', 'Компоненты', 'Журнал'],
  data.profile_inference.flatMap(r => r.actual_profile.map(p => [r.label, r.profile, r.repeat,
    ...Object.values(r.metrics), r.changed_ids.join(', '), +p.resistance_ohm, +p.secretion_s,
    +p.dissociation_s, p.components, r.directory])), [18, 23, 12, 17, 17, 18, 18, 48, 24, 18, 21, 18, 56]);
table('Контекст обучения', 'Живой тест, отдельный снимок и пауза',
  ['Схема', 'Повтор', 'Этап стенда', 'Итерации живой', 'Итерации снимок', 'Итерации пауза', 'Ошибки живой', 'Ошибки снимок',
   'Длины живой', 'Длины снимок', 'Длины пауза', 'Синапсы живой', 'Синапсы снимок', 'Синапсы пауза',
   'Изменения при переходе к снимку', 'Журнал снимка'],
  data.sequence_context.map(r => [protocolLabels[r.scheme], r.repeat, r.stage, ...r.iterations, r.live_Q, r.snapshot_Q,
    ...r.d.map(x => x?.join(', ')), ...r.s.map(x => x?.join(', ')),
    r.changes?.map(([id, before, after]) => `${id} ${before}→${after}`).join(', '), r.snapshot_log]),
  [39, 13, 14, 18, 18, 18, 18, 18]);
table('Повторы последовательностей', 'Повторяемость структуры и ответов внутри условий',
  ['Протокол', 'Условие', 'Полных повторов', 'Совпадение учебных рядов', 'Измеренных состояний', 'Совпадение векторов'],
  (data.sequence_repeats ?? []).map(r => [protocolLabels[r.scheme], r.mode, r.repeats,
    r.same_training ? 'да' : 'нет', r.evaluation_states, r.same_answers == null ? null : r.same_answers ? 'да' : 'нет']),
  [39, 19, 19, 26, 23, 26]);
table('Первый переход', 'Префикс непрерывного переобучения от № 22 к № 37',
  ['Повтор', 'С входа', 'На вход', 'Итерации архив', 'Итерации сейчас', 'Длины архив', 'Длины сейчас',
   'Синапсы архив', 'Синапсы сейчас', 'Причина завершения', 'Журнал'],
  data.warm_prefix_22_37.map(r => [r.repeat, r.from_id, r.to_id, r.historical_iterations, r.observed_iterations,
    r.historical_d.join(', '), r.observed_d.join(', '), r.historical_s.join(', '), r.observed_s.join(', '),
    r.stop_reason, r.log]), [13, 15, 15, 21, 21, 25, 25, 25, 25, 24, 60]);
table('Порядок при переобучении', 'Отдельная проверка обновления порядка в переходе № 22 → № 37',
  ['Сборки', 'Условие', 'Повтор', 'Целевой объект', 'Итерации', 'Такты', 'Длины', 'Синапсы', 'Статус', 'Журнал'],
  (data.warm_order ?? []).flatMap(r => r.stages.map((s, index) => [
    r.matched ? 'Одна' : 'Раздельные', r.mode, r.repeat, index === 0 ? 22 : 37, s.iterations, s.ticks,
    s.dendrites.join(', '),
    s.synapses.join(', '), s.status, r.log])),
  [18, 22, 14, 17, 14, 14, 25, 25, 23, 58]);
if (data.warm_extensions?.length) {
  table('Удлинённый префикс', 'Влияние обновления порядка на более длинную последовательность',
    ['Процесс', 'Переход', 'С входа', 'На вход', 'Длины архив', 'Длины новые', 'Синапсы архив',
     'Синапсы новые', 'Итерации архив', 'Итерации в прежнем повторе', 'Итерации новые', 'Совпадение', 'Статус', 'Журнал'],
    data.warm_extensions.map(r => [r.series, r.transition, r.from_id, r.to_id, r.historical_d.join(', '),
      r.d.join(', '), r.historical_s.join(', '), r.s.join(', '), r.historical_iterations,
      r.previous_iterations, r.iterations, r.matches ? 'да' : 'нет', r.status, r.log]),
    [39, 13, 13, 13, 25, 25, 25, 25, 16, 18, 16, 17, 20, 58]);
}
const signalNames = {
  drives: 'Управление генераторами', generators: 'Выходы генераторов', synapses: 'Сигналы синапсов',
  soma: 'Потенциалы сом', zone_V: 'Потенциал LTZone, В', zone_output: 'Выход LTZone',
  wrapper_output: 'Выход оболочки', registered: 'Регистрация импульса',
};
table('Первые различия', 'Первый наблюдаемый такт расхождения по сигналу',
  ['Модель', 'Фактор', 'Объект Iris', 'Величина', 'Такт', 'Компонент', 'Значение до', 'Значение после',
   'Время до, с', 'Время после, с', 'Трасса'],
  data.tick_comparisons.flatMap(r => r.first_events.map(e => [r.label, r.factor, e.input_id, signalNames[e.quantity] ?? e.quantity,
    e.tick, JSON.stringify(e.component_index), JSON.stringify(e.before), JSON.stringify(e.after),
    e.baseline_time_s, e.changed_time_s, r.logs[1]])), [24, 18, 16, 31, 13, 14, 31, 31, 18, 18, 58]);
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
table('Среда Release', `${runtime.os} ${runtime.os_build}, ${runtime.executable_directory}`,
  ['Загруженная библиотека', 'Версия файла', 'SHA256'],
  runtime.local_modules_observed.map(r => [r.path, r.version, r.sha256]), [59, 21, 68]);
table('Покрытие', 'Сопоставление запланированных и выполненных серий',
  ['Серия', 'Запланировано', 'Завершено', 'Выполняется', 'Неуспешные процессы', 'Ожидают запуска'],
  coverage.phases.map(r => [r.phase, r.planned, r.completed_processes, r.running,
    r.failed_processes, r.pending_processes]), [31, 19, 17, 19, 26, 23]);
if (coverage.trace_pairs_pending?.length) {
  table('Ожидаемые трассы', 'Сочетания с изменёнными ответами, для которых ожидается потактовая сверка',
    ['Модель', 'Вмешательство'], coverage.trace_pairs_pending, [26, 28]);
}
table('Повтор прежних ответов', 'Контроль прежних измерений по закреплённым графам',
  ['Модель', 'Вектор совпал', 'Тот же бинарник', 'Фактический SHA256', 'Исторический SHA256', 'Журнал'],
  (data.reference_audit ?? []).map(r => [r.label, r.matches ? 'да' : 'нет', r.exact_original_binary ? 'да' : 'нет',
    r.actual_binary, r.original_binary, r.log]), [27, 18, 19, 68, 68, 63]);
table('Загрузка после сохранения', 'Реакция первого входа после повторного открытия',
  ['Серия', 'Задание', 'Тот же ответ', 'Тот же пик сом', 'Журнал'],
  (data.roundtrip_controls ?? []).map(r => [r.phase, r.run, r.same_first_answer ? 'да' : 'нет',
    r.same_first_peak ? 'да' : 'нет', r.log]), [22, 42, 19, 21, 65]);

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
  chart.titleTextStyle.fontSize = 17;
  chart.legend = { position: 'top', textStyle: { fontSize: 14 } };
  chart.xAxis = { axisType: 'textAxis', title: { text: x }, textStyle: { fontSize: 13 } };
  chart.yAxis = { min, max, title: { text: y }, textStyle: { fontSize: 13 },
    ...(figure.major_unit === undefined ? {} : { majorUnit: figure.major_unit }),
    numberFormatCode: figure.format ?? '0', numberFormatSourceLinked: false };
  chart.series.items.forEach((series, index) => {
    const color = palette[index % palette.length];
    series.fill = color;
    if (!figure.type || figure.type === 'line') {
      series.line = { fill: color, width: 2, style: 'dashed' };
      series.marker = { symbol: ['circle', 'square', 'diamond', 'triangle'][index % 4], size: 10,
        fill: index === 0 ? 'none' : color, line: { fill: color, width: 1.4, style: 'solid' } };
    }
  });
  chartIndex.push({ id, min, max, rows, x, y, major_unit: figure.major_unit });
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await fs.mkdir(delivery, { recursive: true });
await xlsx.save(path.join(delivery, 'DiscrepancyDiagnosis.xlsx'));
await fs.writeFile(path.join(checkpoint ? delivery : work, 'chart-index.json'), JSON.stringify(chartIndex, null, 2));
