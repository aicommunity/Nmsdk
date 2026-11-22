"""Small native OMML writer used by the maintained scientific reports."""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def _put(parent, value):
    if isinstance(value, str):
        run=OxmlElement('m:r')
        properties=OxmlElement('m:rPr');literal=OxmlElement('m:lit')
        literal.set(qn('m:val'),'1');properties.append(literal);run.append(properties)
        text=OxmlElement('m:t')
        text.set(qn('xml:space'),'preserve');text.text=value
        run.append(text);parent.append(run);return
    kind=value[0]
    if kind=='row':
        for item in value[1:]:_put(parent,item)
        return
    if kind in ('sub','sup','subsup'):
        tag={'sub':'sSub','sup':'sSup','subsup':'sSubSup'}[kind]
        node=OxmlElement('m:'+tag)
        fields=[('e',value[1]),('sub' if kind!='sup' else 'sup',value[2])]
        if kind=='subsup':fields.append(('sup',value[3]))
        for name,item in fields:
            field=OxmlElement('m:'+name);_put(field,item);node.append(field)
    elif kind=='fraction':
        node=OxmlElement('m:f')
        for name,item in [('num',value[1]),('den',value[2])]:
            field=OxmlElement('m:'+name);_put(field,item);node.append(field)
    elif kind=='delimited':
        node=OxmlElement('m:d');properties=OxmlElement('m:dPr')
        for name,text in [('begChr',value[1]),('endChr',value[2])]:
            field=OxmlElement('m:'+name);field.set(qn('m:val'),text);properties.append(field)
        node.append(properties);body=OxmlElement('m:e')
        for item in value[3:]:_put(body,item)
        node.append(body)
    elif kind=='function':
        node=OxmlElement('m:func');name=OxmlElement('m:fName');_put(name,value[1])
        node.append(name);body=OxmlElement('m:e');_put(body,value[2]);node.append(body)
    else:raise ValueError('Unknown OMML node '+str(kind))
    parent.append(node)


def equation(document, *values):
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt
    paragraph=document.add_paragraph();paragraph.alignment=WD_ALIGN_PARAGRAPH.CENTER
    paragraph.paragraph_format.space_before=Pt(5)
    paragraph.paragraph_format.space_after=Pt(7)
    paragraph.paragraph_format.keep_together=True
    math=OxmlElement('m:oMath')
    for value in values:_put(math,value)
    paragraph._p.append(math)
    return paragraph


def sub(value,index):return ['sub',value,index]
def sup(value,index):return ['sup',value,index]
def scripts(value,index,exponent):return ['subsup',value,index,exponent]
def absolute(value):return ['delimited','|','|',value]
def group(*values):return ['delimited','(',')',*values]
