from io import BytesIO
import textwrap
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
        pdfmetrics.registerFont(TTFont(self.font_name, f'hanbai/static/fonts/{self.font_name}.ttf'))
        pdfmetrics.registerFont(TTFont(self.bold_font_name, f'hanbai/static/fonts/{self.bold_font_name}.ttf'))

        # TODO:: Manullay declaring is probably better
        self.styles = getSampleStyleSheet()
        for style in self.styles.byName.values():
            style.fontName = self.font_name
        self.normal_style = self.styles['Normal']
        self.normal_style.fontSize = 7
        self.textarea_width = 12  # TODO:: Set actual width
        self.styles['Heading4'].fontName = self.bold_font_name

        # Report instance instantiation
        self.basic_spacer = Spacer(1, 12)
        self.target = BytesIO()
        self.doc = SimpleDocTemplate(
            self.target,
            pagesize=A5,
            rightMargin=MARGIN // 2,
            leftMargin=MARGIN // 2,
            topMargin=MARGIN // 2,
            bottomMargin=MARGIN // 2,
        )

    def make_report(self):
        # create the components in order & add them to report here.
        # Each component section should just return a table or paragraph;
        # Adding to the table will be done here.
        main_content = []
        main_content.append(self.upper_table())

        self.doc.build(main_content)
        self.doc_target.seek(0)
        return self.doc_target

    def upper_table(self):
        header_cell = self.header()
        vehicle_info_cell = self.vehicle_info()
        previous_vehicle_info_cell = self.previous_vehicle_info()

        company_info_cell = self.company_info()
        customer_info_cell = self.customer_info()
        registered_holder_info_cell = self.registered_holder_info()
        table = Table([
            [header_cell, self.basic_spacer, vehicle_info_cell, self.basic_spacer, previous_vehicle_info_cell],
            [company_info_cell, self.basic_spacer, customer_info_cell, self.basic_spacer, registered_holder_info_cell],
        ])
        return table

    def header(self):
        return Paragraph('注文書', self.styles['Heading1'])

    def vehicle_info(self):
        info = self.order.vehicle_info
        extra_equipment_lines = info.extra_equipment.split('\r\n') if info.extra_equipment else ['']
        extra_equipment_lines = [textwrap.wrap(line, width=self.textarea_width) or [''] for line in extra_equipment_lines]
        extra_equipment_lines = [escape(subline) for line in extra_equipment_lines for subline in line]
        extra_equipment = '<br />'.join(extra_equipment_lines)
        table = Table([
            # Col 1: Labels
            [Paragraph('車輌明細', self.styles['Heading4']),
             Paragraph(info._meta.get_field('car_name').verbose_name, self.normal_style),
             Paragraph('年式', self.normal_style),
             Paragraph(info._meta.get_field('car_model').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('distance_traveled').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('engine_displacement').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('expected_delivery_year').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('extra_equipment').verbose_name, self.normal_style)],
            # Col 2: C1 Values
            [Paragraph('', self.styles['Heading1']),  # Continuation of heading
             Paragraph(info.car_name, self.normal_style),
             Paragraph(f'{info.model_year}年{info.model_month}月', self.normal_style),
             Paragraph(info.car_model, self.normal_style),
             Paragraph(info.distance_traveled, self.normal_style),
             Paragraph(info.engine_displacement, self.normal_style),
             Paragraph(f'{info.expected_delivery_year}年', self.normal_style),
             Paragraph(extra_equipment, self.normal_style)],
            # Col 3: Labels
            [Paragraph('', self.styles['Heading1']),  # Continuation of heading
             Paragraph('', self.normal_style),  # Continuation of car name
             Paragraph(info._meta.get_field('color').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('model_number').verbose_name, self.normal_style),
             Paragraph(info._meta.get_field('registration_number').verbose_name, self.normal_style),
             Paragraph('車検', self.normal_style),
             Paragraph(info._meta.get_field('doors').verbose_name, self.normal_style),
             Paragraph('', self.normal_style)],  # Continuation of extra equipment
            # Col 4: C3 Values
            [Paragraph('', self.styles['Heading1']),  # Continuation of heading
             Paragraph('', self.normal_style),  # Continuation of car name
             Paragraph(info.color, self.normal_style),
             Paragraph(info.model_number, self.normal_style),
             Paragraph(info.registration_number, self.normal_style),
             Paragraph(f'{info.inspection_year}年{info.inspection_month}月', self.normal_style),
             Paragraph(info.doors, self.normal_style),
             Paragraph('', self.normal_style)],  # Continuation of extra equipment
        ])
        return table

    def previous_vehicle_info(self):
        table = Table([])
        return table

    def company_info(self):
        table = Table([])
        return table

    def customer_info(self):
        table = Table([])
        return table

    def registered_holder_info(self):
        table = Table([])
        return table
