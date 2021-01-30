from django.core import validators
from django.db import models


class ExtraField(models.Model):
    class FieldTypeChoices(models.IntegerChoices):
        STRING = 1
        INTEGER = 2

    field_name = models.CharField(max_length=255, null=False, blank=False)
    value_type = models.IntegerField(choices=FieldTypeChoices.choices)
    string_value = models.CharField(max_length=255, null=True, blank=True)
    integer_value = models.IntegerField(null=True)

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
                                      null=True)
    inspection_year = models.IntegerField('車検_年', null=True)
    inspection_month = models.IntegerField('車検_月',
                                           validators=[validators.MinValueValidator(1),
                                                       validators.MaxValueValidator(12)],
                                           null=True)
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
                                            null=True)
    doors = models.IntegerField('ドア', validators=[validators.MinValueValidator(1)], default=5,
                                null=True)
    color = models.CharField('色', max_length=255,
                             blank=True)
    expeted_delivery_month = models.IntegerField('納車予定月',
                                                 validators=[validators.MinValueValidator(1),
                                                             validators.MaxValueValidator(12)],
                                                 null=True)
    expected_delivery_year = models.IntegerField('納車予定年', null=True)
    extra_equipment = models.TextField('装備', blank=True)


class PreviousVehicleInfo(BasicVehicleInfo):
    '''下取車(したどりしゃ）'''
    owner = models.TextField('使用者', blank=True)
    model_specificaiton = models.CharField('型式指定', max_length=255, blank=True)
    classification = models.CharField('類別', max_length=255, blank=True)


class CustomerInfo(models.Model):
    '''ご購入者(ごこうにゅうしゃ）'''
    name = models.CharField('氏名', max_length=255, blank=True)
    name_furi = models.CharField('フリガナ', max_length=255, blank=True)
    birthday = models.DateField('生年月日', null=True)
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


class CustomSectionFields(models.Model):
    field = models.ForeignKey(ExtraField, on_delete=models.PROTECT)
    section = models.ForeignKey('CustomSection', on_delete=models.PROTECT)


class CustomSection(models.Model):
    section_name = models.CharField(max_length=255, blank=True)
    fields = models.ManyToManyField(ExtraField, through=CustomSectionFields)


class InsuranceTax(models.Model):
    '''税金・保険料'''
    vehicle_tax = models.PositiveIntegerField('自動車税', null=True)
    income_tax = models.PositiveIntegerField('所得税', null=True)
    vehicle_liability_insurance = models.PositiveIntegerField('自賠責保険料', null=True)
    optional_insurance = models.PositiveIntegerField('任意保険料', null=True)
    stamp_duty = models.PositiveIntegerField('印紙税', null=True)


class ConsumptionTax(models.Model):
    '''消費税課税対象'''
    # 手続代行費用
    inspection_registration_delivery_tax = models.PositiveIntegerField('検査・登録・届出', null=True)
    proof_of_storage_space = models.PositiveIntegerField('車庫証明', null=True)
    previous_vehicle_processing_fee = models.PositiveIntegerField('下取者手続', null=True)
    # 手続代行費用 おわり

    delivery_fee = models.PositiveIntegerField('納車費用', null=True)
    audit_fee = models.PositiveIntegerField('査定料', null=True)
    remaining_vehicle_tax = models.PositiveIntegerField('自動車税未経過相当額', null=True)
    remiaining_liability = models.PositiveIntegerField('自賠責未経過相当額', null=True)
    recycle_management_fee = models.PositiveIntegerField('リサイクル資金管理料金', null=True)
    extras = models.OneToOneField(
        CustomSection,
        help_text='追加項目',
        on_delete=models.CASCADE,
    )


class TaxExemption(models.Model):
    '''非課税'''
    # 預り法定費用
    inspection_registration_delivery_exemption = models.PositiveIntegerField('怨嗟・登録・届出', null=True)
    proof_of_storage_exemption = models.PositiveIntegerField('車庫証明', null=True)
    previous_vehicle_processing_exemption = models.PositiveIntegerField('下取者手続', null=True)
    recycle_deposit = models.PositiveIntegerField('リサイクル預託金額合計', null=True)


class Itemization(models.Model):
    '''
    Number comments correspond to numbers on original sheet
    '''
    vehicle_price = models.PositiveIntegerField('車輌本体価格', null=True)  # 1
    special_discount = models.PositiveIntegerField('特別値引き', null=True)  # 2
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
    # 14 is aggregate of all
    down_payment = models.PositiveIntegerField('頭金', null=True)  # 15
    trade_in_price = models.PositiveIntegerField('下取者価格', null=True)  # 16
    # 残金 is aggregate of 14, 15, 16


class PaymentDetails(models.Model):
    '''支払い明細'''
    installment_count = models.PositiveIntegerField('支払い回数', null=True)
    initial_installment_price = models.PositiveIntegerField('初回支払い額', null=True)
    second_and_on_installment_price = models.PositiveIntegerField('2回目以降支払い額', null=True)
    bonus_amount = models.PositiveIntegerField('ボーナス支払い額', null=True)
    bonus_count = models.PositiveIntegerField('ボーナス回数', null=True)
    credit_card_company = models.CharField('クレジット会社名', max_length=255, blank=True)


class Order(models.Model):
    '''注文書'''
    started = models.DateTimeField()
    last_edited = models.DateTimeField(null=True)
    completed = models.DateTimeField(null=True)

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
    notes = models.TextField('備考', blank=True)
    person_in_charge = models.CharField('担当者', max_length=255, blank=True)
