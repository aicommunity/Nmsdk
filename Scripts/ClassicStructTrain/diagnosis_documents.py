"""Produce the diagnosis plan and final report with the native workbook charts."""
from pathlib import Path
import argparse
import hashlib
import sys
from zipfile import ZipFile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from diagnosis_run import DELIVERY, WORK, load, save, relative


def document(title):
    doc = Document()
    section = doc.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin, section.bottom_margin = Cm(2), Cm(2)
    section.left_margin, section.right_margin = Cm(3), Cm(1.5)
    section.footer_distance = Cm(1)
    for name in ("Normal", "Title", "Heading 1", "Heading 2", "Caption"):
        style = doc.styles[name]
        style.font.name = "Times New Roman"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style.font.size = Pt({"Title": 18, "Caption": 11}.get(name, 14))
        for element in style.element.xpath(".//w:pBdr"):
            element.getparent().remove(element)
        for fonts in style.element.xpath(".//w:rFonts"):
            for attribute in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):
                fonts.attrib.pop(qn("w:" + attribute), None)
    normal = doc.styles["Normal"].paragraph_format
    normal.first_line_indent = Cm(1.25)
    normal.line_spacing = 1.5
    normal.space_after = Pt(3)
    normal.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    caption = doc.styles["Caption"].paragraph_format
    caption.first_line_indent = Cm(0)
    caption.line_spacing = 1.1
    caption.space_after = Pt(6)
    caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.paragraph_format.first_line_indent = Cm(0)
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    doc.core_properties.title = title
    doc.core_properties.author = "Проект NMSDK"
    p = doc.add_paragraph(title, "Title")
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Cm(0)
    return doc


def paragraph(doc, text):
    doc.add_paragraph(text)


def plan():
    title = "План диагностики расхождений исторического обучения и инференса NMSDK"
    doc = document(title)
    paragraph(doc, "Цель работы — установить причины расхождений по исходным наблюдениям и воспроизводимым контрольным опытам, исправить подтверждённые дефекты и определить границы выводов об историческом алгоритме.")
    doc.add_heading("1 Исходные наблюдения", 1)
    paragraph(doc, "ScientificComparisons описывает инференс сохранённых и реконструированных графов. TrainingReproducibility содержит новое обучение, инференс современных состояний и изолированные факторы. Для 22 архивных столбцов сверены 3300 ответов. В первом отчёте найдено 111 различий с историей, при новом обучении — 98. Совпадение восстановилось в 89 позициях, новое различие появилось в 76, в 22 сохранилось.")
    paragraph(doc, "Для прежней конфигурации NL22 подтверждено влияние порядка расчёта на четыре решения. У нового NT111 сброс переключил решение на входе № 84. В 14 архивных состояниях перехода от № 51 к № 61 первичные файлы подтверждают счета ошибок. Пятнадцатый файл содержит восемь ответов. У 26 файлов двух схем есть по одному лишнему нулю, связь с ошибочной попыткой чтения требует проверки.")
    doc.add_heading("2 Источники и стенд", 1)
    paragraph(doc, "Закрепить исходные файлы по SHA256 и сопоставить ячейки, номер состояния, граф, вход и журнал. Проверить первые 30 записей, формулы, номера снимков, последний стимул и число успешных чтений. В журналах уточнить порядок компонентов и разделить причины остановки. Отдельно регистрировать потенциал LTZone и сумму потенциалов сом.")
    doc.add_page_break()
    doc.add_heading("3 Контролируемый инференс", 1)
    paragraph(doc, "Сверить прежние ответы на тех же конфигурациях. Провести три независимые серии с исходным условием, одним изменением и возвратом исходного условия. Пилот включает NL22, NT45, NT60, оба варианта NT64, сохранённые для сравнения графы NT111 и NL111, новый NT111, средний вход и два состояния перехода.")
    paragraph(doc, "Проверять порядок вычислений, такт смены входа и окно, точность задержек, сброс и источник ответа. В полном проходе выделить изменившиеся ID и проследить генератор, синапс, сому, LTZone и регистрацию по тактам. Подтвердившиеся факторы расширить на 22 архивных столбца, 14 состояний перехода и отдельные модели № 51, № 61 и среднего входа.")
    doc.add_heading("4 Контролируемое обучение", 1)
    paragraph(doc, "По три повтора с записью и без записи выполнить на NT и NL для № 22, 64 и 111, а также на NL для № 51, № 61 и среднего. Сверить импульсы, инициализацию, значения перед выбором действия, изменение графа и завершающий такт. Для двух схем сравнить живой тест, обучение с оценкой снимков в другом процессе и паузу той же модельной длительности.")
    paragraph(doc, "Скрестить современный и частично восстановленный циклы с двумя значениями времени секреции. Проверить реально применённые сопротивление и время диссоциации. Разделить допуск амплитуды NT, остановку после удаления и учёт пересечения цели. Сравнить порядок в обучении и при загрузке как отдельные вмешательства.")
    doc.add_page_break()
    doc.add_heading("5 Критерии завершения и материалы", 1)
    paragraph(doc, "NT80 повторить трижды последовательно при прежних пределах. Строгий NT22 исследовать до 1000 итераций или 1800 секунд на попытку. Сверять общие префиксы. Вывод о невозможности сходимости требует инварианта или повторения полного динамического состояния. Подтвердившиеся изменения исследовать на контрольной десятке и соответствующих последовательностях.")
    paragraph(doc, "Подтверждение дефекта требует воспроизвести его, устранить одним изменением и вернуть обратным контролем. Ошибка исторической записи устанавливается по первичному источнику и независимому пересчёту. В отчёте указать для каждого вывода степень подтверждения и условия применимости.")
    paragraph(doc, "Работа ведётся в исследовательских ветках, в Release из Bin/Platform/Win. Скрипты располагаются в Scripts, конфигурации — в Bin/Configs/StructTrainClassic. Исправления стенда и диагностические изменения ядра фиксируются отдельно. Итоговый DOCX включает диаграммы из XLSX и их анализ. Книга хранит ответы по каждому входу, параметры, протоколы и ссылки на журналы.")
    DELIVERY.mkdir(parents=True, exist_ok=True)
    doc.save(DELIVERY / "DiscrepancyDiagnosisPlan.docx")


def report(checkpoint=False):
    data = load(WORK / "diagnosis-report.json")
    doc = document("Диагностика расхождений исторического обучения и инференса NMSDK")
    if checkpoint:
        paragraph(doc, "Промежуточная версия. Включены завершившиеся наблюдения на момент формирования книги.")
    chart_root = WORK / "checkpoint/charts" if checkpoint else WORK / "charts"
    paragraph(doc, data["lead"])
    images = []
    for section in data["sections"]:
        doc.add_heading(section["title"], 1)
        for text in section["paragraphs"]:
            paragraph(doc, text)
        for chart in section.get("charts", []):
            image = chart_root / (chart["id"] + ".png")
            p = doc.add_paragraph()
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(image), width=Cm(16.5))
            doc.add_paragraph(f"Рисунок {len(images)+1} — {chart['title']}", "Caption")
            paragraph(doc, chart["analysis"])
            images.append(hashlib.sha256(image.read_bytes()).hexdigest())
    destination = WORK / "checkpoint" if checkpoint else DELIVERY
    target = destination / "DiscrepancyDiagnosis.docx"
    doc.save(target)
    with ZipFile(target) as archive:
        actual = [hashlib.sha256(archive.read(name)).hexdigest() for name in archive.namelist()
                  if name.startswith("word/media/")]
    assert actual == images
    audit = destination if checkpoint else WORK
    save(audit / "docx-image-audit.json", {"passed": True, "images": images, "file": relative(target)})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", choices=["plan", "report"])
    parser.add_argument("--checkpoint", action="store_true")
    options = parser.parse_args()
    if options.file == "plan":
        plan()
    else:
        report(options.checkpoint)
