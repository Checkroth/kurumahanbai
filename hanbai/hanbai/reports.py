from io import BytesIO
from xml.sax.saxutils import escape

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import enums, colors

from django.conf import settings


ZERO_PAD = TableStyle([
    ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
])
WIDTH, HEIGHT = A5
MARGIN = 75
WIDTH = WIDTH - MARGIN
HEIGHT = HEIGHT - MARGIN
THIRDS = WIDTH // 3
SIXTHS = WIDTH // 6


class OrderReport:
    def __init__(self, order):
        self.order = order
        # Configuration
        self.font_name = 'NotoSerifJP-Regular'
        self.bold_font_name = 'NotoSerifJP-Bold'
        # TODO:: Manullay declaring is probably better
        self.styles = getSampleStyleSheet()
        for style in self.styles:
            style.fontName = reg_font_name
        self.normal_style = styles['Normal']
        self.normal_style.fontSize = 7
        styles['Heading4'].fontName = bold_font_name



        # Report instance instantiation
        self.target = BytesIO()
        self.doc = SimpleDocTemplate(
            doc_target,
            pagesize=A5,
            rightMargin=MARGIN // 2
            leftMargin=MARGIN // 2,
            topMargin=MARGIN // 2,
            bottomMargin=MARGIN // 2,
        )

    def make_report(self):
        # create the components in order & add them to report here.
        # Each component section should just return a table or paragraph;
        # Adding to the table will be done here.
        pass

    def upper_table(self):
        header_cell = self.header()
        vehicle_info_cell = self.vehicle_info()
        previous_vehicle_info_cell = self.previous_vehicle_info()

        company_info_cell = self.company_info()
        customer_info_cell = self.customer_info()
        registered_holder_info_cell = self.registered_holder_info()

    def header(self):
        return Paragraph('注文書', styles['Heading'])

    def vehicle_info(self):
        info = self.order.vehicle_info
        table = Table([
            # Col 1: Labels
            [Paragraph('車輌明細', styles['Heading4']),
             Paragraph(info._meta.get_field('car_name').verbose_name, self.normal_style),
             Pargaraph('年式', self.normal_style),
             Paragraph(info._meta.get_field('car_model'.verbose_name), self.normal_style),
             Paragraph(info._meta.get_field('distance_traveled').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('engine_displacement').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('expected_delivery_year').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('doors').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('extra_equipment').verbose_name, self.normal_style)],
            # Col 2: Values
            [Paragraph('', styles['Heading']),
             Paragraph(info.car_name, self.normal_style),
             Pargaraph(f'{info.model_year}年{info.model_month}月', self.normal_style),
             Paragraph(info.car_model, self.normal_style),
             Paragraph(info.distance_traveled, self.normal_style),
             Paragraph(info.engine_displacement, self.normal_style),
             Paragraph(f'{info.expected_delivery_year}年', self.normal_style),
             Paragraph(info.doors, self.normal_style),
             Paragraph(info.extra_equipment, self.normal_style)]  # Todo: split/join with newlines
            ]
        ])
        return table


