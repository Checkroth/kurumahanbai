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
FOURTHS = WIDTH // 4
SIXTHS = WIDTH // 6
EIGHTHS = WIDTH // 8
SIXTEENTHS = EIGHTHS // 2
THIRTY2NDS = SIXTEENTHS // 2


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
        self.small_style = deepcopy(self.normal_style)
        self.small_style.fontSize = 4
        self.center_style = deepcopy(self.styles['Normal'])
        self.center_style.alignment = enums.TA_CENTER
        self.right_style = deepcopy(self.normal_style)
        self.right_style.alignment = enums.TA_RIGHT
        
        self.textarea_width = 12  # TODO:: Set actual width
        self.vertical_style = self.normal_style
        self.styles['Heading4'].fontName = self.bold_font_name
        self.styles['Heading4'].fontSize = 6
        self.floating_tablestyle = [
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 2),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ]
        self.basic_tablestyle = deepcopy(self.floating_tablestyle)
        self.basic_tablestyle += [
            ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
            ('BOX', (0, 0), (-1, -1), .5, colors.black),
        ]
        self.totals_style = deepcopy(self.styles['Normal'])
        self.totals_style.fontSize = 7
        self.totals_style.alignment = enums.TA_CENTER

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
        main_content.append(self.basic_spacer)
        main_content.append(self.middle_table())
        main_content.append(self.basic_spacer)
        main_content.append(self.bottom_table())

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
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (1, 0), (1, -1), 10),
        ]
        table.setStyle(TableStyle(style))
        return table

    def middle_table(self):
        '''
        [お支払い現金合計] = [車輌販売価額] + [諸費用合計] + [消費税合計] - [下取車価額]
        '''
        # TODO:: actual numbres
        sale_price = 2137880
        expenses = 831200
        consumption_tax = 0
        previous_vehicle_cost = 0
        total = sale_price + expenses
        style = self.totals_style

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
        ], rowHeights=(15, 15))
        tstyle = deepcopy(self.floating_tablestyle)
        tstyle += [
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (1, 0), (1, -1), 10),
            ('SPAN', (1, 0), (1, 1)),
            ('SPAN', (3, 0), (3, 1)),
            ('SPAN', (5, 0), (5, 1)),
            ('SPAN', (7, 0), (7, 1)),
        ]
        table.setStyle(tstyle)
        return table

    def bottom_table(self):
        '''
        [Itemization Totals]     [TAX/INSURANCE]           [ACCESSORIES]
        [...Itemization    ]     [CONSUMPTION/PROCESS]     [ACCESSORIES]
        [...Itemization    ]     [TAX EXEMPTION]           [CUSTOM SPECS]
        '''
        itemization_totals_cell = self.itemization_totals()
        trade_in_totals_cell = self.trade_in_totals()
        payment_details_cell = self.payment_details()
        notes_cell = self.notes()

        tax_insurance_cell = self.tax_insurance()
        consumption_process_cell = self.consumption_process()
        tax_exemption_cell = self.tax_exemption()

        accessories_cell = self.accessories()
        custom_specs_cell = self.custom_specs()
        table = Table([[
            [itemization_totals_cell,
             self.basic_spacer,
             trade_in_totals_cell,
             self.basic_spacer,
             payment_details_cell,
             self.basic_spacer, notes_cell],
            [tax_insurance_cell, consumption_process_cell, tax_exemption_cell],
            [accessories_cell, custom_specs_cell],
        ]])
        style = deepcopy(ZERO_PAD)
        style += [
            ('ALIGN', (0, 0), (0, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (1, 0), (1, -1), 10),
        ]
        table.setStyle(TableStyle(style))
        return table

    def header(self):
        style = ParagraphStyle(
            name='CenterHeading1',
            parent=self.styles['Heading1'],
            alignment=enums.TA_CENTER,
            leading=10,
        )
        return Paragraph('注文書', style)

    def cells_from_extras(self, extras, leading=0, min_length=1):
        rows = [
            ([''] * leading)
            + [Paragraph(extra.field_name if extra.field_name is not None else '', self.normal_style),
               Paragraph(escape(str(extra.value if extra.value is not None else  '')), self.right_style)]
            for extra in extras.fields.all()
        ]
        num_rows_to_add = max(min_length - len(rows), 0)
        blank_rows = [
            [Paragraph('', self.normal_style), Paragraph('', self.normal_style)]
            for _ in range(num_rows_to_add)
        ]
        return rows + blank_rows

    def _text_to_lines(self, text: Optional[str], width=None):
        if not width:
            width = self.textarea_width
        lines = text.splitlines() if text else ['']
        lines = [textwrap.wrap(line, width=width) or [''] for line in lines]
        lines = [escape(subline) for line in lines for subline in line]
        return '<br />'.join(lines)

    def _cell_from_fieldname(self, model, global_style=None):
        if global_style is None:
            global_style = self.normal_style

        def get_field(field, style=None):
            if style is None:
                style = global_style
            # Global special cases
            if field == 'postal_code':
                verbose_name = '〒'
            else:
                verbose_name = model._meta.get_field(field).verbose_name

            return Paragraph(verbose_name, style)

        return get_field

    def _cell_from_fieldval(self, model, global_style=None):
        if global_style is None:
            global_style = self.normal_style

        def get_field(field, nocomma=False, style=None):
            if style is None:
                style = global_style
            field_value = getattr(model, field)
            # Global special cases
            if 'phone' in field:
                field_value = f'Tel　{field_value}' if field_value else 'Tel'

            try:
                field_value = int(field_value)
                if nocomma:
                    converted = str(field_value)
                else:
                    converted = f'{field_value:,}'
            except (ValueError, TypeError):
                converted = str(field_value) if field_value is not None else ''
            return Paragraph(escape(converted), style)

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
        ], colWidths = [SIXTEENTHS , EIGHTHS + SIXTEENTHS] * 2)
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
            ['', cell_from_fieldname('postal_code'), cell_from_fieldval('postal_code', nocomma=True)],
            ['', cell_from_fieldname('address'), Paragraph(address, self.normal_style)],
            ['', cell_from_fieldname('contact_phone'), cell_from_fieldval('contact_name'), cell_from_fieldval('contact_phone')],
        ], colWidths=[SIXTEENTHS // 2, SIXTEENTHS, (EIGHTHS * 2), EIGHTHS])
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
            ['', cell_from_fieldname('postal_code'),
             cell_from_fieldval('postal_code', nocomma=True),
             cell_from_fieldval('phone', nocomma=True)],
            ['', cell_from_fieldname('address'), Paragraph(address, self.normal_style)],
        ], colWidths = [SIXTEENTHS // 2, SIXTEENTHS, (EIGHTHS * 2), EIGHTHS])
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

    def itemization_totals(self):
        info = self.order.itemization
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info, global_style=self.right_style)
        table = Table([
            [cell_from_fieldname('vehicle_price'), cell_from_fieldval('vehicle_price')],
            [cell_from_fieldname('special_discount'), cell_from_fieldval('special_discount')],
            [Paragraph('車両本体課税対象額 (1 + 2 + 3)', self.normal_style), cell_from_fieldval('subtotal')],
            [Paragraph('付属品価格 (5)', self.normal_style), cell_from_fieldval('accessories_total')],
            [Paragraph('特別仕様価格 (6)', self.normal_style), cell_from_fieldval('custom_specs_total')],
            [Paragraph('車両販売価格 (4 + 5 + 6+ 7+ 8)', self.normal_style), cell_from_fieldval('total_sale_price')],
            [Paragraph('税金・保険料 (10)', self.normal_style), cell_from_fieldval('insurance_tax_total')],
            [Paragraph('消費税課税対象（課税) (11)', self.normal_style), cell_from_fieldval('consumption_tax_total')],
            [Paragraph('消費税課税対象（非課税) (12)', self.normal_style), cell_from_fieldval('tax_exemption_total')],
            [Paragraph('消費税合計 (13)', self.normal_style), cell_from_fieldval('all_tax_total')],
            [Paragraph('合計 (14)', self.normal_style), cell_from_fieldval('all_total')],
        ])
        style = deepcopy(self.basic_tablestyle)        
        table.setStyle(style)
        return table

    def trade_in_totals(self):
        info = self.order.itemization
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info)
        table = Table([
            [cell_from_fieldname('down_payment'), cell_from_fieldval('down_payment')],
            [cell_from_fieldname('trade_in_price'), cell_from_fieldval('trade_in_price')],
        ])
        style = deepcopy(self.basic_tablestyle)        
        table.setStyle(style)
        return table

    def payment_details(self):
        info = self.order.payment_details
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info)
        table = Table([
            [cell_from_fieldname('installment_count'), cell_from_fieldval('installment_count')],
            [cell_from_fieldname('initial_installment_price'), cell_from_fieldval('initial_installment_price')],
            [cell_from_fieldname('second_and_on_installment_price'), cell_from_fieldval('second_and_on_installment_price')],
            [cell_from_fieldname('bonus_amount'), cell_from_fieldval('bonus_amount')],
            [cell_from_fieldname('bonus_count'), cell_from_fieldval('bonus_count')],
            [cell_from_fieldname('credit_card_company'), cell_from_fieldval('credit_card_company')],
        ])
        style = deepcopy(self.basic_tablestyle)        
        table.setStyle(style)
        return table

    def notes(self):
        notes = self._text_to_lines(self.order.notes, 48)
        table = Table([
            [Paragraph('備考', self.styles['Heading4'])],
            [Paragraph(notes, self.normal_style)]
        ])
        style = deepcopy(self.basic_tablestyle)
        table.setStyle(style)
        return table

    def tax_insurance(self):
        info = self.order.itemization.insurance_tax
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info, global_style=self.right_style)
        table = Table([
            [Paragraph('<br />'.join('税金・保険料'), self.vertical_style),
             cell_from_fieldname('vehicle_tax'), cell_from_fieldval('vehicle_tax')],
            ['', cell_from_fieldname('acquisition_tax'), cell_from_fieldval('acquisition_tax')],
            ['', cell_from_fieldname('weight_tax'), cell_from_fieldval('weight_tax')],
            ['', cell_from_fieldname('vehicle_liability_insurance'), cell_from_fieldval('vehicle_liability_insurance')],
            ['', cell_from_fieldname('optional_insurance'), cell_from_fieldval('optional_insurance')],
            ['', cell_from_fieldname('stamp_duty'), cell_from_fieldval('stamp_duty')],
            ['', Paragraph('計', self.normal_style), Paragraph(str(info.total), self.right_style)],
        ], colWidths=[THIRTY2NDS, (THIRDS // 2) - THIRTY2NDS, (THIRDS // 2) - THIRTY2NDS])
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('VALAIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('SPAN', (0, 0), (0, -1)),
        ]
        table.setStyle(style)
        return table

    def consumption_process(self):
        info = self.order.itemization.consumption_tax
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info, global_style=self.right_style)
        rows = [
            [Paragraph('<br />'.join('消費税課税対象'), self.vertical_style),
             Paragraph('<br />'.join(['手続', '代行', '費用']), self.normal_style),
             cell_from_fieldname('inspection_registration_delivery_tax', style=self.small_style),
             cell_from_fieldval('inspection_registration_delivery_tax')],
            ['', '', cell_from_fieldname('proof_of_storage_space'), cell_from_fieldval('proof_of_storage_space')],
            ['', '', cell_from_fieldname('previous_vehicle_processing_fee'), cell_from_fieldval('previous_vehicle_processing_fee')],
            ['', cell_from_fieldname('delivery_fee'), '', cell_from_fieldval('delivery_fee')],
            ['', cell_from_fieldname('audit_fee'), '', cell_from_fieldval('audit_fee')],
            ['', cell_from_fieldname('remaining_vehicle_tax'), '', cell_from_fieldval('remaining_vehicle_tax')],
            ['', cell_from_fieldname('remaining_liability'), '', cell_from_fieldval('remaining_liability')],
            ['', cell_from_fieldname('recycle_management_fee'), '', cell_from_fieldval('recycle_management_fee')],
        ] + self.cells_from_extras(info.extras, leading=1)
        table = Table(
            rows,
            colWidths=[
                THIRTY2NDS,
                THIRTY2NDS + (THIRTY2NDS // 2),
                (THIRDS // 2) - (THIRTY2NDS * 2) - (THIRTY2NDS // 2),
                (THIRDS // 2) - THIRTY2NDS
            ],
            rowHeights=[10] * len(rows)
        )
        style = deepcopy(self.basic_tablestyle)
        lower_spans = [
            ('SPAN', (1, rownum), (2, rownum))
            for rownum in range(3, len(rows) + 1)
        ]
        style += [
            ('VALAIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('VALAIGN', (1, 0), (1, 0), 'MIDDLE'),
            ('SPAN', (0, 0), (0, -1)),
            ('SPAN', (1, 0), (1, 2)),
        ]
        style += lower_spans
        table.setStyle(style)
        return table

    def tax_exemption(self):
        info = self.order.itemization.consumption_tax_exemption
        cell_from_fieldname = self._cell_from_fieldname(info)
        cell_from_fieldval = self._cell_from_fieldval(info, global_style=self.right_style)
        rows = [
            [Paragraph('<br />'.join('非課税'), self.vertical_style),
             Paragraph('<br />'.join(['預り', '法定', '費用']), self.normal_style),
             cell_from_fieldname('inspection_registration_delivery_exemption', style=self.small_style),
             cell_from_fieldval('inspection_registration_delivery_exemption')],
            ['', '', cell_from_fieldname('proof_of_storage_exemption'), cell_from_fieldval('proof_of_storage_exemption')],
            ['', '', cell_from_fieldname('previous_vehicle_processing_exemption'),
             cell_from_fieldval('previous_vehicle_processing_exemption')],
            ['', cell_from_fieldname('recycle_deposit'), '', cell_from_fieldval('recycle_deposit')]
        ]
        table = Table(
            rows,
            colWidths=[
                THIRTY2NDS,
                THIRTY2NDS + (THIRTY2NDS // 2),
                (THIRDS // 2) - (THIRTY2NDS * 2) - (THIRTY2NDS // 2),
                (THIRDS // 2) - THIRTY2NDS
            ],
            rowHeights=[10] * len(rows)
        )
        style = deepcopy(self.basic_tablestyle)
        lower_spans = [
            ('SPAN', (1, rownum), (2, rownum))
            for rownum in range(3, len(rows) + 1)
        ]
        style += [
            ('SPAN', (0, 0), (0, -1)),
            ('SPAN', (1, 0), (1, 2)),
        ]
        style += lower_spans
        table.setStyle(style)
        return table

    def accessories(self):
        itemized_rows = self.cells_from_extras(self.order.itemization.accessories, leading=1, min_length=10)
        total = self.order.itemization.accessories_total
        total = str(total) if total is not None else '0'
        rows = [
            [Paragraph('<br />'.join('付属品'), self.vertical_style), '', ''],
        ] + itemized_rows + [
            ['', Paragraph('計 (5)', self.normal_style), Paragraph(total, self.right_style)],
        ]
        table = Table(
            rows,
            colWidths=[THIRTY2NDS, (THIRDS // 2) - THIRTY2NDS, (THIRDS // 2) - THIRTY2NDS],
            rowHeights=[10] * len(rows)
        )
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('SPAN', (0, 0), (0, -1)),
        ]
        table.setStyle(style)
        return table

    def custom_specs(self):
        itemized_rows = self.cells_from_extras(self.order.itemization.custom_specs, leading=1, min_length=10)
        total = self.order.itemization.custom_specs_total
        total = str(total) if total is not None else '0'
        rows = [
            [Paragraph('<br />'.join('特別仕様'), self.vertical_style), '', ''],
        ] + itemized_rows + [
            ['', Paragraph('計 (6)', self.normal_style), Paragraph(total, self.right_style)],
        ]
        table = Table(
            rows,
            colWidths=[THIRTY2NDS, (THIRDS // 2) - THIRTY2NDS, (THIRDS // 2) - THIRTY2NDS],
            rowHeights=[10] * len(rows),
        )
        style = deepcopy(self.basic_tablestyle)
        style += [
            ('SPAN', (0, 0), (0, -1)),
        ]
        table.setStyle(style)
        return table
