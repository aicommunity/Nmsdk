"""Build the Word edition of the NeuroModeler guide from its Markdown source."""

import re
from pathlib import Path

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.image.image import Image
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE
from docx.shared import Cm, Pt, RGBColor


GUIDE = Path(__file__).resolve().parents[2] / "Docs/GUI/Classic-Structural-Training"
INLINE = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\(([^)]+)\)")
IMAGE = re.compile(r"!\[([^\]]+)\]\(([^)]+)\)")
ITEM = re.compile(r"(\d+\.|-) (.+)")


def add_inline(paragraph, text):
    offset = 0
    for match in INLINE.finditer(text):
        paragraph.add_run(text[offset:match.start()])
        code, bold, label, target = match.groups()
        if code:
            run = paragraph.add_run(code)
            run.font.name = "Consolas"
            run.font.size = Pt(9.5)
        elif bold:
            paragraph.add_run(bold).bold = True
        else:
            link = OxmlElement("w:hyperlink")
            link_id = paragraph.part.relate_to(
                target, RELATIONSHIP_TYPE.HYPERLINK, is_external=True
            )
            link.set(qn("r:id"), link_id)
            run = paragraph.add_run(label)
            run.underline = True
            link.append(run._r)
            paragraph._p.append(link)
        offset = match.end()
    paragraph.add_run(text[offset:])


def style_document(document):
    section = document.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1.5)
    section.top_margin = section.bottom_margin = Cm(2)
    section.footer_distance = Cm(1)

    styles = document.styles
    for name, size in (("Normal", 13), ("Title", 19), ("Heading 1", 15), ("Heading 2", 13),
                       ("Caption", 11)):
        style = styles[name]
        style.font.name = "Times New Roman"
        style.font.size = Pt(size)
        style.font.color.rgb = RGBColor.from_string("111111")
        fonts = style.element.get_or_add_rPr().rFonts
        for theme_attribute in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
            fonts.attrib.pop(qn("w:" + theme_attribute), None)
    normal = styles["Normal"].paragraph_format
    normal.first_line_indent = Cm(1.25)
    normal.space_after = Pt(5)
    normal.line_spacing = 1.17
    styles["Title"].paragraph_format.keep_with_next = True
    styles["Title"].font.bold = True
    styles["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    styles["Title"].paragraph_format.first_line_indent = Cm(0)
    for border in styles["Title"].element.xpath(".//w:pBdr"):
        border.getparent().remove(border)
    for name in ("Heading 1", "Heading 2"):
        styles[name].paragraph_format.space_before = Pt(13)
        styles[name].paragraph_format.space_after = Pt(5)
        styles[name].paragraph_format.first_line_indent = Cm(0)

    item = styles.add_style("Guide Step", WD_STYLE_TYPE.PARAGRAPH)
    item.base_style = styles["Normal"]
    item.paragraph_format.left_indent = Cm(0.55)
    item.paragraph_format.first_line_indent = Cm(-0.55)
    item.paragraph_format.keep_together = True
    item.paragraph_format.tab_stops.add_tab_stop(Cm(0.55))

    caption = styles["Caption"]
    caption.font.italic = False
    caption.font.bold = False
    caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption.paragraph_format.first_line_indent = Cm(0)
    caption.paragraph_format.space_before = Pt(3)

    table_caption = styles.add_style("Guide Table Caption", WD_STYLE_TYPE.PARAGRAPH)
    table_caption.base_style = styles["Caption"]
    table_caption.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    table_caption.paragraph_format.keep_with_next = True

    sample = styles.add_style("Guide Data", WD_STYLE_TYPE.PARAGRAPH)
    sample.base_style = styles["Normal"]
    sample.font.name = "Consolas"
    sample.font.size = Pt(11)
    sample.paragraph_format.first_line_indent = Cm(0)
    sample.paragraph_format.left_indent = Cm(1.25)
    sample.paragraph_format.line_spacing = 1.0
    sample.paragraph_format.keep_together = True

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.first_line_indent = Cm(0)
    number = OxmlElement("w:fldSimple")
    number.set(qn("w:instr"), "PAGE")
    footer._p.append(number)
    document.settings.element.append(OxmlElement("w:doNotAutoCompressPictures"))


def add_table(document, lines):
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in lines]
    table = document.add_table(rows=0, cols=len(rows[0]))
    table.style = "Table Grid"
    widths = [Cm(16.5 * fraction) for fraction in (0.29, 0.33, 0.38)]
    table.autofit = False
    for column, width in zip(table.columns, widths, strict=True):
        column.width = width
    for index, values in enumerate([rows[0], *rows[2:]]):
        row = table.add_row()
        props = row._tr.get_or_add_trPr()
        props.append(OxmlElement("w:cantSplit"))
        if not index:
            props.append(OxmlElement("w:tblHeader"))
        for cell, value, width in zip(row.cells, values, widths, strict=True):
            cell.width = width
            if not index:
                fill = OxmlElement("w:shd")
                fill.set(qn("w:fill"), "EBEEF1")
                cell._tc.get_or_add_tcPr().append(fill)
            paragraph = cell.paragraphs[0]
            paragraph.paragraph_format.first_line_indent = Cm(0)
            paragraph.paragraph_format.line_spacing = 1.05
            paragraph.paragraph_format.keep_with_next = index < len(rows) - 2
            paragraph.paragraph_format.space_after = Pt(3)
            paragraph.paragraph_format.space_before = Pt(3)
            add_inline(paragraph, f"**{value}**" if not index else value)


def build():
    document = Document()
    style_document(document)
    document.core_properties.title = "Структурное обучение и распознавание в NeuroModeler"
    document.core_properties.subject = "NNeuronTrainer и NNeuronLearner"
    document.core_properties.author = "NMSDK"
    lines = (GUIDE / "README.md").read_text(encoding="utf-8").splitlines()
    table = []
    code_lines = None

    for line in [*lines, ""]:
        if line.startswith("```"):
            if code_lines is None:
                code_lines = []
            else:
                document.add_paragraph("\n".join(code_lines), style="Guide Data")
                code_lines = None
            continue
        if code_lines is not None:
            code_lines.append(line)
            continue
        if line.startswith("|"):
            table.append(line)
            continue
        if table:
            add_table(document, table)
            table.clear()
        if not line:
            continue
        picture = IMAGE.fullmatch(line)
        item = ITEM.fullmatch(line)
        if picture:
            label, file = picture.groups()
            paragraph = document.add_paragraph()
            paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
            paragraph.paragraph_format.first_line_indent = Cm(0)
            paragraph.paragraph_format.keep_with_next = True
            paragraph.paragraph_format.line_spacing = 1.0
            paragraph.paragraph_format.space_after = Pt(2)
            image_path = GUIDE / file
            picture_size = Image.from_file(str(image_path))
            width_cm = min(16.5, picture_size.px_width / 45,
                           16 * picture_size.px_width / picture_size.px_height)
            shape = paragraph.add_run().add_picture(str(image_path), width=Cm(width_cm))
            shape._inline.docPr.set("descr", label)
            document.add_paragraph(label, style="Caption")
        elif line.startswith("#"):
            prefix, title = line.split(" ", maxsplit=1)
            document.add_paragraph(title, style="Title" if prefix == "#" else f"Heading {len(prefix) - 1}")
        elif item:
            marker, description = item.groups()
            paragraph = document.add_paragraph(style="Guide Step")
            paragraph.add_run(("•" if marker == "-" else marker) + "\t")
            add_inline(paragraph, description)
        elif re.match(r"Таблица \d+ —", line):
            document.add_paragraph(line, style="Guide Table Caption")
        else:
            add_inline(document.add_paragraph(), line)

    document.save(GUIDE / "NeuroModeler-Classic-Training.docx")


if __name__ == "__main__":
    build()
