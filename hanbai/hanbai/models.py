from django.core import validators
from django.db import models


class ExtraField(models.Model):
    class FieldTypeChoices(models.IntegerChoices):
        STRING = 1
        INTEGER = 2

    field_name = models.CharField(max_length=255, null=True, blank=True)
    value_type = models.IntegerField(choices=FieldTypeChoices.choices, default=FieldTypeChoices.STRING.value)
    string_value = models.CharField(max_length=255, null=True, blank=True)
    integer_value = models.IntegerField(null=True, blank=True)
    section = models.ForeignKey(
        'CustomSection',
        on_delete=models.CASCADE,
        related_name='fields',
    )

    @property
    def value(self):
        if self.value_type == self.FieldTypeChoices.STRING:
            return self.string_value
        elif self.value_type == self.FieldTypeChoices.INTEGER:
            return self.integer_value


class BasicVehicleInfo(models.Model):
    class YearChoices(models.TextChoices):
        SEIREKI = '西', '西暦'
        SHOWA = '昭', '昭和'
        HEISEI = '平', '平成'
        REIWA = '令', '令和'

    class DistanceChoices(models.TextChoices):
        MILES = 'M', 'マイル'
        KILOMETERS = 'KM', 'キロメータ'

    car_model = models.CharField('型式', max_length=255, blank=True)
    car_name = models.CharField('車名', max_length=255, blank=True)
    model_year = models.CharField('年式_年', max_length=2, choices=YearChoices.choices, blank=True)
    model_month = models.IntegerField('年式_月',
                                      validators=[validators.MinValueValidator(1),
                                                  validators.MaxValueValidator(12)],
                                      null=True, blank=True)
    inspection_year = models.IntegerField('車検_年', null=True, blank=True)
    inspection_month = models.IntegerField('車検_月',
                                           validators=[validators.MinValueValidator(1),
                                                       validators.MaxValueValidator(12)],
                                           null=True, blank=True)
    model_number = models.CharField('車台番号', max_length=255, blank=True)
    registration_number = models.CharField('登録番号', max_length=255, blank=True)

    class Meta:
        abstract = True


class VehicleInfo(BasicVehicleInfo):
    '''車輌明細'''
    distance_traveled_unit = models.CharField(max_length=3,
                                              choices=BasicVehicleInfo.DistanceChoices.choices,
                                              default=BasicVehicleInfo.DistanceChoices.KILOMETERS,
                                              blank=True)
    distance_traveled = models.IntegerField('走行', validators=[validators.MinValueValidator(0)],
                                            null=True, blank=True)
    doors = models.IntegerField('ドア', validators=[validators.MinValueValidator(1)], default=5,
                                null=True, blank=True)
    color = models.CharField('色', max_length=255,
                             blank=True)
    engine_displacement = models.CharField('排気量cc', max_length=255, blank=True)
    expeted_delivery_month = models.IntegerField('納車予定月',
                                                 validators=[validators.MinValueValidator(1),
                                                             validators.MaxValueValidator(12)],
                                                 null=True, blank=True)
    expected_delivery_year = models.IntegerField('納車予定年', null=True, blank=True)
    extra_equipment = models.TextField('装備', blank=True)


class PreviousVehicleInfo(BasicVehicleInfo):
    '''下取車(したどりしゃ）'''
    owner = models.TextField('使用者', blank=True)
    model_specification = models.CharField('型式指定', max_length=255, blank=True)
    classification = models.CharField('類別', max_length=255, blank=True)


class CustomerInfo(models.Model):
    '''ご購入者(ごこうにゅうしゃ）'''
    name = models.CharField('氏名', max_length=255, blank=True)
    name_furi = models.CharField('フリガナ', max_length=255, blank=True)
    birthday = models.DateField('生年月日', null=True, blank=True)
    # TODO:: Validation?
    postal_code = models.CharField('郵便番号', max_length=8, blank=True)  # ppp-cccc
    phone = models.CharField('電話番号', max_length=12, blank=True)  # xxx-yyy-zzzz
    address = models.TextField('住所', blank=True)
    contact_name = models.CharField('連絡先＿名', max_length=255, blank=True)
    contact_phone = models.CharField('連絡先', max_length=12, blank=True)


class RegisteredHolderInfo(models.Model):
    '''登録名義人（とうろくめいぎにん）'''
    name = models.CharField('氏名', max_length=255, blank=True)
    name_furi = models.CharField('フリガナ', max_length=255, blank=True)
    postal_code = models.CharField('郵便番号', max_length=8, blank=True)
    phone = models.CharField('電話番号', max_length=12, blank=True)
    address = models.TextField('住所', blank=True)


class CustomSection(models.Model):
    '''
    Parent-agnostic collection of extra fields
    Another field holds a 1 to 1 with this section.
    This section holds a 1 to many with custom fields.
    Ultimately, it is a 1-to-many to extra fields from the parent model, but only one foreign key field.
    '''
    section_name = models.CharField(max_length=255, blank=True)

    def integer_aggregate(self):
        return sum(self.fields.filter(
            value_type=ExtraField.FieldTypeChoices.INTEGER,
            integer_value__isnull=False,
        ).values_list('integer_value', flat=True))


class InsuranceTax(models.Model):
    '''税金・保険料'''
    vehicle_tax = models.PositiveIntegerField('自動車税', null=True, blank=True)
    acquisition_tax = models.PositiveIntegerField('得得税', null=True, blank=True)
    weight_tax = models.PositiveIntegerField('重量税', null=True, blank=True)
    vehicle_liability_insurance = models.PositiveIntegerField('自賠責保険料', null=True, blank=True)
    optional_insurance = models.PositiveIntegerField('任意保険料', null=True, blank=True)
    stamp_duty = models.PositiveIntegerField('印紙税', null=True, blank=True)

    @property
    def total(self):
        return sum([field or 0 for field in [
            self.vehicle_tax,
            self.acquisition_tax,
            self.weight_tax,
            self.vehicle_liability_insurance,
            self.optional_insurance,
            self.stamp_duty,
        ]])


class ConsumptionTax(models.Model):
    '''消費税課税対象'''
    # 手続代行費用
    inspection_registration_delivery_tax = models.PositiveIntegerField('検査・登録・届出', null=True, blank=True)
    proof_of_storage_space = models.PositiveIntegerField('車庫証明', null=True, blank=True)
    previous_vehicle_processing_fee = models.PositiveIntegerField('下取者手続', null=True, blank=True)
    # 手続代行費用 おわり

    delivery_fee = models.PositiveIntegerField('納車費用', null=True, blank=True)
    audit_fee = models.PositiveIntegerField('査定料', null=True, blank=True)
    remaining_vehicle_tax = models.PositiveIntegerField('自動車税未経過相当額', null=True, blank=True)
    remaining_liability = models.PositiveIntegerField('自賠責未経過相当額', null=True, blank=True)
    recycle_management_fee = models.PositiveIntegerField('リサイクル資金管理料金', null=True, blank=True)
    extras = models.OneToOneField(
        CustomSection,
        help_text='追加項目',
        on_delete=models.CASCADE,
    )

    @property
    def total(self):
        return sum([field or 0 for field in [
            self.inspection_registration_delivery_tax,
            self.proof_of_storage_space,
            self.previous_vehicle_processing_fee,
            self.delivery_fee,
            self.audit_fee,
            self.remaining_vehicle_tax,
            self.remaining_liability,
            self.recycle_management_fee,
            self.extras.integer_aggregate(),
        ]])


class TaxExemption(models.Model):
    '''非課税'''
    # 預り法定費用
    inspection_registration_delivery_exemption = models.PositiveIntegerField('怨嗟・登録・届出', null=True, blank=True)
    proof_of_storage_exemption = models.PositiveIntegerField('車庫証明', null=True, blank=True)
    previous_vehicle_processing_exemption = models.PositiveIntegerField('下取者手続', null=True, blank=True)
    recycle_deposit = models.PositiveIntegerField('リサイクル預託金額合計', null=True, blank=True)

    @property
    def total(self):
        return sum([field or 0 for field in [
            self.inspection_registration_delivery_exemption,
            self.proof_of_storage_exemption,
            self.previous_vehicle_processing_exemption,
            self.recycle_deposit
        ]])


class Itemization(models.Model):
    '''
    Number comments correspond to numbers on original sheet
    '''
    vehicle_price = models.PositiveIntegerField('車輌本体価格 (1)', null=True, blank=True)  # 1
    special_discount = models.PositiveIntegerField('特別値引き (2)', null=True, blank=True)  # 2
    # 3 not required
    # 4 is aggregate of 1, 2, 3
    accessories = models.OneToOneField(  # 5
        CustomSection,
        related_name='itemization_accessories',
        help_text='付属品',
        on_delete=models.CASCADE,
    )

    custom_specs = models.OneToOneField(  # 6
        CustomSection,
        related_name='itemization_custom_specs',
        help_text='特別仕様',
        on_delete=models.PROTECT,
    )
    # 7, 8 not required
    # 9 is aggreegate of 4, 5, 6, 7, 8
    insurance_tax = models.OneToOneField(  # 10
        InsuranceTax,
        help_text='税金・保険料',
        on_delete=models.PROTECT,
    )
    consumption_tax = models.OneToOneField(  # 11
        ConsumptionTax,
        help_text='消費税課税対象（課税)',
        on_delete=models.PROTECT,
    )
    consumption_tax_exemption = models.OneToOneField(  # 12
        TaxExemption,
        help_text='消費税課税対象（非課税)',
        on_delete=models.PROTECT,
    )

    # 13 is aggregate of 4, 5, 6, 7, 8, 11, 16
    # 14 is aggregate of 9, 10, 11, 12
    down_payment = models.PositiveIntegerField('頭金', null=True, blank=True)  # 15
    trade_in_price = models.PositiveIntegerField('下取者価格', null=True, blank=True)  # 16
    # 残金 is aggregate of 14, 15, 16

    @property
    def subtotal(self):
        '''4: 車両本体課税対象額'''
        vehicle_price = self.vehicle_price or 0
        special_discount = self.special_discount or 0
        return (vehicle_price - special_discount) or None

    @property
    def accessories_total(self):
        '''5: 付属品価格'''
        return self.accessories.integer_aggregate() or None

    @property
    def custom_specs_total(self):
        '''6: 特別仕様価格'''
        return self.custom_specs.integer_aggregate() or None

    @property
    def total_sale_price(self):
        '''9: 車両販売価格'''
        subtotal = self.subtotal or 0
        accessories = self.accessories_total or 0
        custom_specs = self.custom_specs_total or 0
        return subtotal + accessories + custom_specs

    @property
    def insurance_tax_total(self):
        '''10: 税金・保険料'''
        return self.insurance_tax.total or None

    @property
    def consumption_tax_total(self):
        '''11: 消費税課税対象（課税)'''
        return self.consumption_tax.total or None

    @property
    def tax_exemption_total(self):
        '''12: 消費税課税対象（非課税)'''
        return self.consumption_tax_exemption.total or None

    @property
    def all_tax_total(self):
        '''13: 消費税合計 (9 + 11 - 16)'''
        # TODO:: what is 16?
        return self.all_total

    @property
    def taxable_total(self):
        '''(9 + 10 + 11)'''
        return sum([
            self.total_sale_price or 0,
            self.insurance_tax_total or 0,
            self.consumption_tax_total or 0,
        ])

    @property
    def all_total(self):
        '''14 合計 ( 9 + 10 + 11 + 12)'''
        return sum(filter(None, [self.taxable_total, self.tax_exemption_total]))


class PaymentDetails(models.Model):
    '''支払い明細'''
    installment_count = models.PositiveIntegerField('支払い回数', null=True, blank=True)
    initial_installment_price = models.PositiveIntegerField('初回支払い額', null=True, blank=True)
    second_and_on_installment_price = models.PositiveIntegerField('2回目以降支払い額', null=True, blank=True)
    bonus_amount = models.PositiveIntegerField('ボーナス支払い額', null=True, blank=True)
    bonus_count = models.PositiveIntegerField('ボーナス回数', null=True, blank=True)
    credit_card_company = models.CharField('クレジット会社名', max_length=255, blank=True)


class Order(models.Model):
    '''注文書'''
    started = models.DateTimeField()
    last_edited = models.DateTimeField(null=True, blank=True)
    completed = models.DateTimeField(null=True, blank=True)

    # SellerAddress? (父さん会社情報)
    vehicle_info = models.OneToOneField(
        VehicleInfo,
        help_text='車輌明細',
        on_delete=models.PROTECT,
    )
    previous_vehicle_info = models.OneToOneField(
        PreviousVehicleInfo,
        help_text='下取者',
        on_delete=models.PROTECT,
    )
    customer_info = models.OneToOneField(
        CustomerInfo,
        help_text='ご購入者',
        on_delete=models.PROTECT,
    )
    registered_holder_info = models.OneToOneField(
        RegisteredHolderInfo,
        help_text='登録名義人',
        on_delete=models.PROTECT,
    )
    itemization = models.OneToOneField(
        Itemization,
        help_text='お支払い金額詳細',
        on_delete=models.PROTECT,
    )
    payment_details = models.OneToOneField(
        PaymentDetails,
        help_text='お支払い明細',
        on_delete=models.PROTECT,
    )
    notes = models.TextField('備考', blank=True)
    person_in_charge = models.CharField('担当者', max_length=255, blank=True)

    def json(self):
        ret = {
            'id': self.pk,
            'itemization': {
                'total_sale_price': self.itemization.total_sale_price,
                'taxable_total': self.itemization.taxable_total,
                'all_tax_total': self.itemization.all_tax_total,
                'subtotal': self.itemization.subtotal,
                'accessories_total': self.itemization.accessories_total,
                'custom_specs_total': self.itemization.custom_specs_total,
                'insurance_tax_total': self.itemization.insurance_tax_total,
                'consumption_tax_total': self.itemization.consumption_tax_total,
                'tax_exemption_total': self.itemization.tax_exemption_total,
                'all_total': self.itemization.all_total,
            },
        }
        for k, v in ret['itemization'].items():
            ret['itemization'][k] = v or 0
        return ret
