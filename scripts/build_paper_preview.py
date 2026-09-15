"""Build the current paper PDF from its editable Markdown source.

Requires reportlab==4.4.9. Supports the headings, paragraphs, links, figures, tables,
captions and editorial subtitle used by the current section draft.
"""

from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle


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
    canvas.drawString(doc.leftMargin, 15 * mm, "Preliminary draft | 15 September 2026")
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
        "caption": ParagraphStyle("FigureCaption", fontName="Times-Italic", fontSize=10,
                                  leading=13, spaceAfter=10, allowWidows=0, allowOrphans=0),
        "table_caption": ParagraphStyle("TableCaption", fontName="Times-Italic", fontSize=10,
                                        leading=13, spaceAfter=7, keepWithNext=True),
        "table_body": ParagraphStyle("TableBody", fontName="Times-Roman", fontSize=10,
                                     leading=12),
        "table_header": ParagraphStyle("TableHeader", fontName="Times-Bold", fontSize=10,
                                       leading=12),
        "table_number": ParagraphStyle("TableNumber", fontName="Times-Roman", fontSize=10,
                                       leading=12, alignment=TA_RIGHT),
        "reference": ParagraphStyle("Reference", fontName="Times-Roman", fontSize=10.5,
                                    leading=14, leftIndent=17, firstLineIndent=-17,
                                    spaceAfter=6, allowWidows=0, allowOrphans=0),
    }
    story = []
    references = False
    for block in re.split(r"\n\s*\n", SOURCE.read_text(encoding="utf-8").strip()):
        if block == "<!-- pagebreak -->":
            story.append(PageBreak())
            continue
        if block.startswith("|"):
            rows = [[cell.strip() for cell in line.strip().strip("|").split("|")]
                    for line in block.splitlines()]
            if len(rows) < 3 or not all(re.fullmatch(r":?-+:?", cell) for cell in rows[1]):
                raise ValueError("Expected a Markdown table header separator")
            alignments = rows.pop(1)
            columns = len(rows[0])
            if any(len(row) != columns for row in rows):
                raise ValueError("Inconsistent table column count")
            fractions = {3: [0.31, 0.26, 0.43], 4: [0.25, 0.18, 0.22, 0.35],
                         5: [0.25, 0.1875, 0.1875, 0.1875, 0.1875]}.get(columns)
            if fractions is None:
                fractions = [1 / columns] * columns
            cells = [[Paragraph(inline_markup(cell), styles["table_header" if n == 0 else
                      "table_number" if alignments[c].endswith(":") else "table_body"])
                      for c, cell in enumerate(row)] for n, row in enumerate(rows)]
            table = Table(cells, colWidths=[162 * mm * fraction for fraction in fractions],
                          repeatRows=1, hAlign="LEFT", spaceAfter=10)
            table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E9F0F7")),
                ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.HexColor("#506579")),
                ("LINEBELOW", (0, 1), (-1, -1), 0.25, colors.HexColor("#CCD3DB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            story.append(KeepTogether([table]))
            continue
        figure = re.fullmatch(r"!\[([^\]]+)\]\(([^)]+)\)", block)
        if figure:
            path = (SOURCE.parent / figure.group(2)).resolve()
            if not path.is_relative_to(SOURCE.parent.resolve()):
                raise ValueError("Paper figures must stay within the paper folder")
            item = Image(str(path))
            scale = min(162 * mm / item.imageWidth, 175 * mm / item.imageHeight)
            item.drawWidth = item.imageWidth * scale
            item.drawHeight = item.imageHeight * scale
            item.keepWithNext = True
            story.append(item)
            continue
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
            elif text.startswith(("2. ", "3. ", "5. ", "6. ", "7. ", "8. ")):
                story.append(PageBreak())
        elif re.match(r"Figure \d+\.", block):
            text, style = block, "caption"
        elif re.match(r"Table \d+\.", block):
            text, style = block, "table_caption"
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
                            subject="Preliminary research draft - Sections 1-8")
    doc.build(story, onFirstPage=page_footer, onLaterPages=page_footer)
    print(f"Created {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
