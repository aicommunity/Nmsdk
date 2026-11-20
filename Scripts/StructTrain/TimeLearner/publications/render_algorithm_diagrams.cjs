/* Reproducible Graphviz diagrams for the maintained scientific DOCX reports.
 * Use the configured bundled Node.js and its @viz-js/viz and sharp packages.
 * Experimental curves are rendered separately from their original samples.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

async function main() {
  const args = process.argv.slice(2);
  const options = {};
  for (let i = 0; i < args.length; i += 2) {
    if (!['--spec', '--output', '--node-modules'].includes(args[i]) || !args[i + 1])
      throw new Error('Expected --spec, --output and --node-modules');
    options[args[i]] = args[i + 1];
  }
  for (const key of ['--spec', '--output', '--node-modules'])
    if (!options[key]) throw new Error('Missing ' + key);
  const source = fs.readFileSync(options['--spec']);
  const spec = JSON.parse(source);
  if (spec.kind !== 'timelearner_scientific_diagram_sources' || spec.schema_version !== 1 ||
      !Array.isArray(spec.diagrams) || !spec.diagrams.length || spec.diagrams.length > 16)
    throw new Error('Known finite diagram specification required');
  const output = path.resolve(options['--output']);
  if (fs.existsSync(output)) throw new Error('Fresh output directory required');
  const modules = path.resolve(options['--node-modules']);
  const { instance } = require(path.join(modules, '@viz-js/viz'));
  const sharp = require(path.join(modules, 'sharp'));
  const viz = await instance();
  const records = [];
  const seen = new Set();
  fs.mkdirSync(output, { recursive: true });
  const digest = value => crypto.createHash('sha256').update(value).digest('hex');
  for (const diagram of spec.diagrams) {
    let dot = diagram.dot;
    if (diagram.source !== undefined) {
      if (dot !== undefined || diagram.source !== diagram.id + '.dot')
        throw new Error('A diagram uses one local DOT source');
      dot = fs.readFileSync(path.join(path.dirname(path.resolve(options['--spec'])), diagram.source), 'utf8');
    }
    if (!/^[a-z0-9-]{1,64}$/.test(diagram.id) || seen.has(diagram.id) ||
        typeof dot !== 'string' || dot.length > 128 * 1024 ||
        typeof diagram.caption !== 'string' || !diagram.caption.trim())
      throw new Error('Unique bounded diagram source required');
    seen.add(diagram.id);
    const engine = diagram.engine || 'dot';
    if (!['dot', 'neato'].includes(engine)) throw new Error('Known diagram layout engine required');
    const svg = viz.renderString(dot, { format: 'svg', engine });
    const raw = Buffer.from(svg, 'utf8');
    const png = await sharp(raw, { density: 180 }).png().toBuffer();
    fs.writeFileSync(path.join(output, diagram.id + '.dot'), dot, 'utf8');
    fs.writeFileSync(path.join(output, diagram.id + '.svg'), raw);
    fs.writeFileSync(path.join(output, diagram.id + '.png'), png);
    const image = await sharp(png).metadata();
    records.push({ id: diagram.id, caption: diagram.caption,
      dot_sha256: digest(Buffer.from(dot)), svg_sha256: digest(raw),
      png_sha256: digest(png), width: image.width, height: image.height,
      scientific_measurement: false, renderer: 'Graphviz through @viz-js/viz', engine });
  }
  const result = { kind: 'timelearner_scientific_diagram_render', schema_version: 1,
    source_sha256: digest(source), diagrams: records, visually_reviewed: false };
  fs.writeFileSync(path.join(output, 'manifest.json'), JSON.stringify(result, null, 2) + '\n');
  process.stdout.write(JSON.stringify({ output, diagrams: records.length, visually_reviewed: false }) + '\n');
}
main().catch(error => { process.stderr.write(error.stack + '\n'); process.exitCode = 1; });
