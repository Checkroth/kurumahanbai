from copy import deepcopy
from io import BytesIO
from typing import Optional
import textwrap
from xml.sax.saxutils import escape

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import enums, colors

from django.conf import settings


ZERO_PAD = [
    ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ('TOPPADDING', (0, 0), (-1, -1), 0),
]
WIDTH, HEIGHT = A4
MARGIN = 75
WIDTH = WIDTH - MARGIN
HEIGHT = HEIGHT - MARGIN
THIRDS = WIDTH // 3
SIXTHS = WIDTH // 6
EIGTH = WIDTH // 8
SIXTEENTH = EIGTH // 2


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
        self.normal_style.fontSize = 5
        self.normal_style.leading = 6
        self.textarea_width = 12  # TODO:: Set actual width
        self.vertical_style = self.normal_style
        self.styles['Heading4'].fontName = self.bold_font_name
        self.basic_tablestyle = [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), .5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]

        # Report instance instantiation
        self.basic_spacer = Spacer(1, 12)
        self.doc_target = BytesIO()
        self.doc = SimpleDocTemplate(
            self.doc_target,
            pagesize=A4,
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
        main_content.append(self.middle_table())

        self.doc.build(main_content)
        self.doc_target.seek(0)
        return self.doc_target

    def upper_table(self):
        '''
        注文書                [Seller Address(Constant)
        [Vehicle Info]        [Customer Info]
        [Prev. Vehicle Info]  [Holder Info]
        '''
        header_cell = self.header()
        vehicle_info_cell = self.vehicle_info()
        previous_vehicle_info_cell = self.previous_vehicle_info()

        company_info_cell = self.company_info()
        customer_info_cell = self.customer_info()
        registered_holder_info_cell = self.registered_holder_info()
        '''
        [HEADER_CELL]
        [VEHICLE_INFO_CELL]
        [PREVIOUS_VEHICLE_INFO_CELL]
        '''
        table = Table([
            # Row 1
            [
                # Row1.Col1
                [header_cell, self.basic_spacer, vehicle_info_cell, self.basic_spacer, previous_vehicle_info_cell],
                # Row1.Col2
                [company_info_cell, self.basic_spacer, customer_info_cell, self.basic_spacer, registered_holder_info_cell]
            ],
        ], colWidths=[WIDTH // 2] * 2)

        style = deepcopy(ZERO_PAD)
        # TODO:: Main table should not have borders. They are just here for initial styling.
        style += [
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), .5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (1, 0), (1, -1), 10),
        ]
        table.setStyle(TableStyle(style))
        return table

    def middle_table(self):
        '''
        [お支払い現金合計] = [車輌販売価額] + [諸費用合計] + [消費税合計] - [下取車価額]
        '''
        sale_price = 2137880
        expenses = 831200
        consumption_tax = 0
        previous_vehicle_cost = 0
        total = sale_price + expenses
        style = self.normal_style

        table = Table([
            [Paragraph('お支払い現金合計', style),
             Paragraph('=', style),
             Paragraph('車輌販売価額', style),
             Paragraph('+', style),
             Paragraph('諸費用合計', style),
             Paragraph('+', style),
             Paragraph('消費税合計', style),
             Paragraph('-', style),
             Paragraph('下取車価額', style)],
            [Paragraph(f'{total:n}', style),
             Paragraph('=', style),
             Paragraph(f'{sale_price:n}', style),
             Paragraph('+', style),
             Paragraph(f'{expenses:n}', style),
             Paragraph('+', style),
             Paragraph(f'{consumption_tax:n}', style),
             Paragraph('-', style),
             Paragraph(f'{previous_vehicle_cost:n}', style)]
        ])
        tstyle = deepcopy(ZERO_PAD)
        tstyle += [
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), .5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (1, 0), (1, -1), 10),
        ]
        table.setStyle(tstyle)
        return table

    def bottom_table(self):
        '''
        [Itemization Totals]     [TAX/INSURANCE]           [ACCESSORIES]
        [...Itemization    ]     [CONSUMPTION/PROCESS]     [ACCESSORIES]
        [...Itemization    ]     [TAX EXEMPTION]           [CUSTOM SPECS]
        '''
        table = Table([
        ])
        return table

    def header(self):
        style = ParagraphStyle(
            name='CenterHeading1',
            parent=self.styles['Heading1'],
            alignment=enums.TA_CENTER,
            leading=10,
        )
        return Paragraph('注文書', style)

    def _text_to_lines(self, text: Optional[str], width=None):
        if not width:
            width = self.textarea_width
        lines = text.splitlines() if text else ['']
        lines = [textwrap.wrap(line, width=width) or [''] for line in lines]
        lines = [escape(subline) for line in lines for subline in line]
        return '<br />'.join(lines)

    def _cell_from_fieldname(self, model):
        def get_field(field):
            # Global special cases
            if field == 'postal_code':
                verbose_name = '〒'
            else:
                verbose_name = model._meta.get_field(field).verbose_name

            return Paragraph(verbose_name, self.normal_style)

        return get_field

    def _cell_from_fieldval(self, model):
        def get_field(field):
            field_value = getattr(model, field)
            # Global special cases
            if 'phone' in field:
                field_value = f'Tel　{field_value}' if field_value else 'Tel'
            converted = str(field_value) if field_value or field_value == 0 else ''
            return Paragraph(escape(converted), self.normal_style)

        return get_field

    def vehicle_info(self):
        info = self.order.vehicle_info
        extra_equipment = self._text_to_lines(info.extra_equipment, 48)
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info)
        table = Table([
            [Paragraph('車輌明細', self.styles['Heading4'])],
            [cell_from_fieldname('car_name'), cell_from_fieldval('car_name')],
            [Paragraph('年式', self.normal_style), Paragraph(f'{info.model_year}年{info.model_month}月', self.normal_style),
             cell_from_fieldname('color'), cell_from_fieldval('color')],
            [cell_from_fieldname('car_model'), cell_from_fieldval('car_model'),
             cell_from_fieldname('model_number'), cell_from_fieldval('model_number')],
            [cell_from_fieldname('distance_traveled'), cell_from_fieldval('distance_traveled'),
             cell_from_fieldname('registration_number'), cell_from_fieldval('registration_number')],
            [cell_from_fieldname('engine_displacement'), cell_from_fieldval('engine_displacement'),
             Paragraph('車検', self.normal_style), Paragraph(f'{info.inspection_year}年{info.inspection_month}月', self.normal_style)],
            [cell_from_fieldname('expected_delivery_year'), Paragraph(f'{info.expected_delivery_year}年', self.normal_style),
             cell_from_fieldname('doors'), cell_from_fieldval('doors')],
            [cell_from_fieldname('extra_equipment'), Paragraph(extra_equipment, self.normal_style)],
        ], colWidths = [SIXTEENTH , EIGTH + SIXTEENTH] * 2)
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (1, 1), (-1, 1)),
            ('SPAN', (1, -1), (-1, -1)),
        ]
        table.setStyle(TableStyle(style))
        return table

    def previous_vehicle_info(self):
        info = self.order.previous_vehicle_info
        owner = self._text_to_lines(info.owner)
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info)
        table = Table([
            [Paragraph('下取車', self.styles['Heading4'])],
            [cell_from_fieldname('car_name'), cell_from_fieldval('car_name')],
            [cell_from_fieldname('model_number'), cell_from_fieldval('model_number'),
             Paragraph('年式', self.normal_style), Paragraph(f'{info.model_year}年{info.model_month}月', self.normal_style)],
            [cell_from_fieldname('registration_number'), cell_from_fieldval('registration_number'),
             Paragraph('車検', self.normal_style), Paragraph(f'{info.inspection_year}年{info.inspection_month}月', self.normal_style)],
            [cell_from_fieldname('owner'), Paragraph(owner, self.normal_style),
             cell_from_fieldname('car_model'), cell_from_fieldval('car_model')],
        ])
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('SPAN', (0, 0), (-1, 0)),
            ('SPAN', (1, 1), (-1, 1)),
        ]
        table.setStyle(TableStyle(style))
        return table

    def company_info(self):
        info = '<br />'.join([
            '★あなたの愛車のトータルアドバイザー★',
            '〒018-0841',
            'オートサービス佐々木',
            '有利本荘市加賀沢字加賀沢４５',
            'ＴＥＬ６６ー２１０４',
            'ＦＡＸ６６ー２１８５',
        ])
        return Paragraph(info, self.normal_style)

    def customer_info(self):
        info = self.order.customer_info
        address = self._text_to_lines(info.address)
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info)
        table = Table([
            [Paragraph('<br />'.join('ご購入者'), self.vertical_style),
             cell_from_fieldname('name_furi'), cell_from_fieldval('name_furi')],
            ['', cell_from_fieldname('name'), cell_from_fieldval('name')],
            ['', cell_from_fieldname('birthday'), cell_from_fieldval('birthday')],
            ['', cell_from_fieldname('postal_code'), cell_from_fieldval('postal_code')],
            ['', cell_from_fieldname('address'), Paragraph(address, self.normal_style)],
            ['', cell_from_fieldname('contact_phone'), cell_from_fieldval('contact_name'), cell_from_fieldval('contact_phone')],
        ], colWidths=[SIXTEENTH // 2, SIXTEENTH, (EIGTH * 2), EIGTH])
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('VALAIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (0, -1)),
            ('SPAN', (2, 0), (3, 0)),
            ('SPAN', (2, 1), (3, 1)),
            ('SPAN', (2, 2), (3, 2)),
            ('SPAN', (2, 3), (3, 3)),
            ('SPAN', (2, 4), (3, 4)),
        ]
        table.setStyle(TableStyle(style))
        return table

    def registered_holder_info(self):
        info = self.order.registered_holder_info
        address = self._text_to_lines(info.address)
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info)
        table = Table([[Paragraph('test', self.normal_style)]])
        table = Table([
            [Paragraph('<br />'.join('登録名義人'), self.vertical_style),
             cell_from_fieldname('name_furi'), cell_from_fieldval('name_furi')],
            ['', cell_from_fieldname('name'), cell_from_fieldval('name')],
            ['', cell_from_fieldname('postal_code'), cell_from_fieldval('postal_code'), cell_from_fieldval('phone')],
            ['', cell_from_fieldname('address'), Paragraph(address, self.normal_style)],
        ], colWidths = [SIXTEENTH // 2, SIXTEENTH, (EIGTH * 2), EIGTH])
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (0, -1)),
            ('SPAN', (2, 0), (3, 0)),
            ('SPAN', (2, 1), (3, 1)),
            ('SPAN', (2, 2), (3, 2)),
            ('SPAN', (2, 3), (2, 3)),
            ('SPAN', (2, 4), (2, 4)),
        ]
        table.setStyle(TableStyle(style))
        return table
