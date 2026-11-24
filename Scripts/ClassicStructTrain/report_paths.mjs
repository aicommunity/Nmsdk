import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const reports = path.join(root, 'Reports', 'StructTrainClassic');

export function reportPath(value) {
  const absolute = path.resolve(root, value);
  const relative = path.relative(reports, absolute);
  const [first] = relative.split(path.sep);
  if (!relative || path.isAbsolute(relative) || first === '..' || first === '_work') {
    return absolute;
  }
  const name = path.basename(absolute);
  const officeReport = /\.(docx|xlsx|md)$/i.test(name);
  if (first === 'outputs' && officeReport) {
    const directory = /Plan\.(docx|xlsx)$/i.test(name) ? path.join(reports, '_work', 'plans') : reports;
    return path.join(directory, name);
  }
  if (relative === name && (officeReport || name === '.gitattributes')) {
    return absolute;
  }
  return path.join(reports, '_work', relative);
}

export async function savePublishedWorkbook(file, target, work) {
  // The spreadsheet exporter may write a diagnostic sidecar next to the workbook.
  const staging = await fs.mkdtemp(path.join(work, 'xlsx-export-'));
  const temporary = path.join(staging, path.basename(target));
  await file.save(temporary);
  await fs.rename(temporary, target);
}
