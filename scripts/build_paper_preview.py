"""Build the current paper PDF from its editable Markdown source.

Requires reportlab==4.4.9. This deliberately supports only the headings,
paragraphs, links and editorial subtitle used by the current section draft.
"""

from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "paper" / "Predictive_Memory_Leak_Detection_Draft.md"
OUTPUT = ROOT / "output" / "pdf" / "Predictive_Memory_Leak_Detection_Draft.pdf"


def inline_markup(text, reference=False):
    """Escape prose while keeping the source's explicit web links clickable."""
    result = []
    cursor = 0
    for match in re.finditer(r"\[([^\]]+)\]\((https?://(?:[^()\s]|\([^()\s]*\))+)\)", text):
        result.append(escape(text[cursor:match.start()]))
        label, url = match.groups()
        if reference:
            result.append("<br/>")
        result.append(f'<link href="{escape(url, quote=True)}">{escape(label)}</link>')
        cursor = match.end()
    result.append(escape(text[cursor:]))
    return "".join(result)


def page_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 9)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(doc.leftMargin, 15 * mm, "Preliminary draft | 14 September 2026")
    canvas.drawRightString(A4[0] - doc.rightMargin, 15 * mm, str(doc.page))
    canvas.restoreState()


def main():
    styles = {
        "title": ParagraphStyle("PaperTitle", fontName="Times-Bold", fontSize=18,
                                leading=21, alignment=TA_CENTER, spaceAfter=12),
        "subtitle": ParagraphStyle("DraftStatus", fontName="Times-Roman", fontSize=10,
                                   leading=13, alignment=TA_CENTER, spaceAfter=14,
                                   textColor=colors.HexColor("#555555")),
        "heading": ParagraphStyle("SectionHeading", fontName="Times-Bold", fontSize=13,
                                  leading=17, spaceBefore=3, spaceAfter=11,
                                  keepWithNext=True),
        "subheading": ParagraphStyle("SubsectionHeading", fontName="Times-Bold", fontSize=11.5,
                                     leading=15, spaceBefore=10, spaceAfter=7,
                                     keepWithNext=True),
        "body": ParagraphStyle("PaperBody", fontName="Times-Roman", fontSize=11.5,
                               leading=14.5, alignment=TA_JUSTIFY, spaceAfter=7,
                               allowWidows=0, allowOrphans=0),
        "reference": ParagraphStyle("Reference", fontName="Times-Roman", fontSize=10.5,
                                    leading=14, leftIndent=17, firstLineIndent=-17,
                                    spaceAfter=6, allowWidows=0, allowOrphans=0),
    }
    story = []
    references = False
    for block in re.split(r"\n\s*\n", SOURCE.read_text(encoding="utf-8").strip()):
        if block.startswith("# "):
            text, style = block[2:], "title"
        elif block.startswith("> "):
            text, style = block[2:], "subtitle"
        elif block.startswith("### "):
            text, style = block[4:], "subheading"
        elif block.startswith("## "):
            text, style = block[3:], "heading"
            if text == "References":
                references = True
                story.append(PageBreak())
            elif text.startswith("2. "):
                story.append(PageBreak())
        else:
            text, style = block, "reference" if references else "body"
        paragraph = Paragraph(inline_markup(text.replace("\n", " "),
                                            reference=style == "reference"), styles[style])
        story.append(KeepTogether([paragraph]) if style == "reference" else paragraph)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=24 * mm,
                            rightMargin=24 * mm, topMargin=20 * mm,
                            bottomMargin=23 * mm,
                            title="Predictive Memory Leak Detection Using Time Series Analysis",
                            subject="Preliminary research draft - Introduction and Literature Survey")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f"Created {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
