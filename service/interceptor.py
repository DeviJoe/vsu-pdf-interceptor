import re
import io
import reportlab.pdfgen.canvas
import requests
import ocrmypdf
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF


def get_pdf_from_moodle(user_link: str, name):
    link = re.split(r'svg/', user_link)[0] + 'svg/'

    i = 1
    doc = reportlab.pdfgen.canvas.Canvas('./generated_pdf/' + name + '.pdf')
    pict = requests.get(link + str(i))
    svg_pict = io.BytesIO(pict.content)
    drawing = svg2rlg(svg_pict)
    doc.setPageSize((drawing.width, drawing.height))

    while True:
        pict = requests.get(link + str(i))
        if pict.status_code == 200:
            svg_pict = io.BytesIO(pict.content)
            drawing = svg2rlg(svg_pict)
            renderPDF.draw(drawing, doc, 0, 0)
            doc.showPage()
            i += 1
        else:
            break

    doc.save()


def ocr_pdf(pdf_input, pdf_output):
    ocrmypdf.ocr(pdf_input, pdf_output, language='rus+eng')

