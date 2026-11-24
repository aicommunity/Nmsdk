"""Cross-check the scientific deliverables against native execution evidence."""
from pathlib import Path
import hashlib, json, zipfile
import xml.etree.ElementTree as ET
from collections import Counter
from pypdf import PdfReader

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from report_paths import report_path
ROOT = Path(__file__).resolve().parents[2]
WORK = ROOT / 'Reports/StructTrainClassic/_work/LegacyChecks-20261123'
OUT = ROOT / 'Reports/StructTrainClassic'
NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def load(name): return json.loads((WORK / name).read_text(encoding='utf-8-sig'))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    d = load('scientific-comparison-data.json')
    figures = load('scientific-figures.json')
    native = load('scientific-native-excel-check.json')
    final = load('final-audit.json')
    assert final['passed'] and final['native_processes'] == 335
    assert native['passed'] and not native['saved_changes']
    workbook, document = OUT / 'ScientificComparisons.xlsx', OUT / 'ScientificComparisons.docx'
    assert sha(workbook).upper() == native['workbook_sha256']
    assert len(figures) == len(native['charts']) == 18
    assert Counter(f['kind'] for f in figures) == {'line_sparse': 11, 'bar': 4, 'line_dense': 3}
    assert d['direct_figures'] == 15 and d['secondary_figures'] == 3
    assert len(d['saved_models']) == 9 and len(d['recognition']) == 22
    assert load('scientific-source-conflicts.json') == []
    assert [p['old_plot'] for p in d['source_points']['E019']] == [7,8,9,9,10,10,9]
    assert [p['old_plot'] for p in d['source_points']['E020']] == [7,7,8,9,9,9,10,10,9,7,5,4,4,5]
    assert [e['source_epoch'] for e in d['epochs']] == list(range(1,15))
    assert [e['thesis_epoch'] for e in d['epochs']] == list(range(14))
    for f, check in zip(figures, native['charts']):
        assert f['id'] == check['id']
        assert check['x_axis']==f['x_axis'] and check['y_axis']==f['y_axis']
        for series in check['series']:
            if f['kind'] == 'line_sparse':
                assert series['marker_size'] >= 8 and series['dash_style'] == 4
                assert series['points'] == f['point_count']
            if f['kind'] == 'line_dense': assert series['dash_style'] == 1 and series['marker_style'] == -4142
    with zipfile.ZipFile(workbook) as z:
        assert z.testzip() is None
        charts = [n for n in z.namelist() if '/charts/chart' in n and n.endswith('.xml')]
        assert len(charts) == 18
        errors = []
        for name in z.namelist():
            if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
                errors.extend((name, c.get('r'), c.findtext('m:v', namespaces=NS)) for c in ET.fromstring(z.read(name)).findall('.//m:c', NS) if c.get('t') == 'e')
        assert not errors, errors
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(s.itertext()) for s in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        relationships = {r.get('Id'): r.get('Target') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        sheet_map = {}
        for sheet in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet', NS):
            target = relationships[sheet.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
            sheet_map[sheet.get('name')] = target.lstrip('/') if target.startswith('/') else 'xl/' + target
        def cells(name):
            values = {}
            for c in ET.fromstring(z.read(sheet_map[name])).findall('m:sheetData/m:row/m:c', NS):
                value = c.findtext('m:v', namespaces=NS)
                if c.get('t') == 's': value = shared[int(value)]
                elif c.get('t') == 'inlineStr': value = ''.join(c.find('m:is', NS).itertext())
                values[c.get('r')] = value
            return values
        passports = cells('Научные состояния')
        evidence = []
        for row in range(6,91):
            assert passports.get(f'A{row}') and passports.get(f'D{row}')
            for col in ['F','G']: assert len(passports[f'{col}{row}'].split(',')) == 5
            directory = report_path(passports[f'H{row}'])
            process = json.loads((directory / 'process.json').read_text(encoding='utf-8-sig'))
            assert process['status'] == 'completed' and process['exit_code'] == 0
            evidence.append(str(directory))
        assert not passports.get('A91')
        recovery = cells('Реестр источников')
        statuses = Counter(recovery[f'D{r}'] for r in range(6,773))
        assert statuses == {'Восстановлено':636, 'Недостаточно данных':131}
        primary=cells('Основной структурный источник')
        assert Counter(primary[f'K{r}'] for r in range(6,151))=={'Полное состояние для инференса':14,'Недостаточно синапсов':131}
        assert not primary.get('A151')
        assert d['primary_source']['path'] in primary['A3']
        assert sha(Path(d['primary_source']['path']))==d['primary_source']['sha256']
    images = load('scientific-docx-images.json')['native_charts']
    with zipfile.ZipFile(document) as z:
        assert z.testzip() is None
        media_hashes = {hashlib.sha256(z.read(name)).hexdigest() for name in z.namelist() if name.startswith('word/media/')}
        assert len(images) == 18 and all(i['sha256'] in media_hashes for i in images)
        text = ''.join(ET.fromstring(z.read('word/document.xml')).itertext())
        for f in figures: assert f['sheet'] in text and f['id'] in text
        assert d['primary_source']['path'] in text
        assert '51 и 61 — номера объектов Iris' in text
        assert 'Распознавание в схеме ноль на один' not in text
        document_xml=ET.fromstring(z.read('word/document.xml'))
        wn={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        margins=document_xml.find('.//w:sectPr/w:pgMar',wn)
        assert margins.get('{'+wn['w']+'}left')=='1701' and margins.get('{'+wn['w']+'}right')=='850'
    pdf = WORK / 'scientific-docx-gost-render/ScientificComparisons.pdf'
    pages = PdfReader(pdf).pages
    assert all(len(page.extract_text().split())>=20 for page in pages)
    toc=load('scientific-toc.json')
    import re
    normalize=lambda t:re.sub(r'\s+',' ',t).strip()
    for heading,page in toc.items():assert normalize(heading) in normalize(pages[page-1].extract_text())
    result = {'passed':True, 'direct_scientific_charts':15, 'conditional_waveforms':3, 'docx_pages':len(pages),
              'native_charts_exactly_embedded':18, 'scientific_state_references':85,
              'source_point_counts':[7,14], 'completed_native_processes':335,
              'workbook_cached_errors':0,'all_axis_titles_checked':True,'primary_source_records':145,'contents_verified':True,
              'outputs':{p.name: {'bytes':p.stat().st_size,'sha256':sha(p)} for p in [document,workbook]}}
    (WORK / 'scientific-final-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__ == '__main__': main()
