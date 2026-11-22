"""Draft layout for the next scientific edition, not a compliance certificate.

The released fourth edition is deliberately unaffected. Full standards review,
report structure, references and visual acceptance remain release requirements.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor


def _font(style, family, size):
    style.font.name = family
    style.font.size = Pt(size)
    style.font.color.rgb = RGBColor(0, 0, 0)
    properties = style.element.get_or_add_rPr()
    fonts = properties.find(qn('w:rFonts'))
    if fonts is None:
        fonts = OxmlElement('w:rFonts')
        properties.insert(0, fonts)
    for name in ('ascii', 'hAnsi', 'eastAsia', 'cs'):
        fonts.set(qn('w:' + name), family)
    for name in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        fonts.attrib.pop(qn('w:' + name), None)


class GostDraftLayout:
    """Apply the explicitly selected A4 profile to a fresh Word document."""

    def __init__(self, document, profile):
        if (profile.get('kind') != 'timelearner_scientific_report_format_profile'
                or profile.get('schema_version') != 1):
            raise ValueError('Known scientific report format profile required')
        self.document = document
        self.profile = profile
        self.sections = self.subsections = self.equations = self.tables = 0
        page = profile['page']
        body = profile['body']
        section = document.sections[0]
        section.page_width = Mm(page['width_mm'])
        section.page_height = Mm(page['height_mm'])
        for name, size in page['margins_mm'].items():
            setattr(section, name + '_margin', Mm(size))
        self.width = section.page_width - section.left_margin - section.right_margin
        self.height = section.page_height - section.top_margin - section.bottom_margin
        section.different_first_page_header_footer = True
        for name in ('Normal', 'Title', 'Subtitle', 'Heading 1', 'Heading 2', 'Caption'):
            style = document.styles[name]
            _font(style, body['font'], body['project_font_size_pt'])
            style.font.bold = name.startswith('Heading')
            style.font.italic = False
            style.font.underline = False
            properties = style.element.find(qn('w:pPr'))
            if properties is not None:
                for border in list(properties.findall(qn('w:pBdr'))):
                    properties.remove(border)
            paragraph = style.paragraph_format
            paragraph.line_spacing = body['line_spacing']
            paragraph.first_line_indent = Mm(body['first_line_indent_mm'])
            paragraph.space_before = paragraph.space_after = Pt(0)
            paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for name in ('Title', 'Subtitle', 'Caption'):
            document.styles[name].paragraph_format.first_line_indent = Mm(0)
            document.styles[name].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
        # ГОСТ 7.32-2017:6.5.8 and 6.6.3: multi-line figure and table
        # names use single spacing, independently of the body spacing.
        document.styles['Caption'].paragraph_format.line_spacing = 1.0
        for name in ('Heading 1', 'Heading 2'):
            paragraph = document.styles[name].paragraph_format
            paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
            paragraph.keep_with_next = True
            paragraph.space_before = paragraph.space_after = Pt(14)
        document.styles['Heading 1'].paragraph_format.page_break_before = True
        code = document.styles['Псевдокод']
        _font(code, 'Consolas', 12)
        code.paragraph_format.first_line_indent = Mm(0)
        code.paragraph_format.line_spacing = 1.5
        code.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        footer = section.footer.paragraphs[0]
        footer.clear()
        footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
        footer.paragraph_format.first_line_indent = Mm(0)
        field = OxmlElement('w:fldSimple')
        field.set(qn('w:instr'), 'PAGE')
        footer._p.append(field)

    def heading(self, text, level=1):
        if level == 1:
            self.sections += 1
            self.subsections = 0
            number = str(self.sections)
        elif level == 2 and self.sections:
            self.subsections += 1
            number = f'{self.sections}.{self.subsections}'
        else:
            raise ValueError('Only numbered sections and subsections are supported')
        return self.document.add_heading(number + ' ' + text, level=level)

    def structural_heading(self, text):
        paragraph = self.document.add_paragraph(text.upper(), style='Heading 1')
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
        paragraph.paragraph_format.first_line_indent = Mm(0)
        return paragraph

    def number_equation(self, paragraph):
        self.equations += 1
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.first_line_indent = Mm(0)
        paragraph.paragraph_format.space_before = Pt(21)
        paragraph.paragraph_format.space_after = Pt(21)
        tabs = paragraph.paragraph_format.tab_stops
        tabs.add_tab_stop(int(self.width / 2), WD_TAB_ALIGNMENT.CENTER)
        tabs.add_tab_stop(self.width, WD_TAB_ALIGNMENT.RIGHT)
        # Move a genuine tab run before the editable OMML expression.
        run = paragraph.add_run('\t')
        math = paragraph._p.find(qn('m:oMath'))
        paragraph._p.remove(run._r)
        paragraph._p.insert(paragraph._p.index(math), run._r)
        paragraph.add_run('\t(' + str(self.equations) + ')')

    def table_caption(self, title):
        self.tables += 1
        paragraph = self.document.add_paragraph(
            f'Таблица {self.tables} — {title.rstrip().rstrip(".")}', style='Caption')
        paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
        paragraph.paragraph_format.keep_with_next = True
        return paragraph

    def format_table(self, table):
        for row_index, row in enumerate(table.rows):
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    paragraph.paragraph_format.first_line_indent = Mm(0)
                    paragraph.paragraph_format.line_spacing = 1.0
                    if len(table.rows) <= 12:
                        paragraph.paragraph_format.keep_with_next = row_index < len(table.rows) - 1
                    for run in paragraph.runs:
                        run.font.name = self.profile['body']['font']
                        run.font.size = Pt(12)
                        run.bold = False
