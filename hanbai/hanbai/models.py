from django.core import validators
from django.db import models


class ExtraField(models.Model):
    class FieldTypeChoices(models.IntegerChoices):
        STRING = 1
        INTEGER = 2

    field_name = models.CharField(max_length=255, null=False, blank=False)
    value_type = models.IntegerField(choices=FieldTypeChoices)
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

    car_model = models.CharField('型式', max_length=255)
    car_name = models.CharField('車名', max_length=255)
    model_year = models.CharField('年式_年', max_length=2, choices=YearChoices)
    model_month = models.IntegerField('年式_月',
                                      validators=[validators.MinValueValidator(1),
                                                  validators.MaxValueValidator(12)])
    inspection_year = models.IntegerField('車検_年')
    inspection_month = models.IntegerField('車検_月',
                                           validators=[validators.MinValueValidator(1),
                                                       validators.MaxValueValidator(12)])
    model_number = models.CharField('車台番号', max_length=255)
    registration_number = models.CharField('登録番号', max_length=255)

    class Meta:
        abstract = True


class VehicleInfo(BasicVehicleInfo):
    '''？？？（？？？）'''
    distance_traveled_unit = models.CharField(max_length=3,
                                              choices=BasicVehicleInfo.DistanceChoices,
                                              default=BasicVehicleInfo.DistanceChoices.KILOMETERS)
    distance_traveled = models.IntegerField('走行', validators=[validators.MinValueValidator(0)])
    doors = models.IntegerField('ドア', validators=[validators.MinValueValidator(1)], default=5)
    color = models.CharField('色', max_length=255)
    expeted_delivery_month = models.IntegerField('納車予定月',
                                                 validators=[validators.MinValueValidator(1),
                                                             validators.MaxValueValidator(12)])
    expected_delivery_year = models.IntegerField('納車予定年')
    extra_equipment = models.TextField('装備')


class PreviousVehicleInfo(BasicVehicleInfo):
    '''下取車(したどりしゃ）'''
    owner = models.TextField('使用者')
    model_specificaiton = models.CharField('型式指定', max_length=255)
    classification = models.CharField('類別', max_length=255)


class CustomerInfo(models.Model):
    '''ご購入者(ごこうにゅうしゃ）'''
    name = models.CharField('氏名', max_length=255)
    name_furi = models.CharField('フリガナ', max_length=255)
    birthday = models.DateField('生年月日')
    # TODO:: Validation?
    postal_code = models.CharField('郵便番号', max_length=8) # ppp-cccc
    phone = models.CharField('電話番号', max_length=12) # xxx-yyy-zzzz
    address = models.TextField('住所')
    contact_name = models.CharField('連絡先＿名', max_length=255)
    contact_phone = models.CharField('連絡先', max_length=12)


class InCareOfInfo(models.Model):
    '''登録名義人（とうろくめいぎにん）'''
    name = models.CharField('氏名', max_length=255)
    name_furi = models.CharField('フリガナ', max_length=255)
    postal_code = models.CharField('郵便番号', max_length=8)
    phone = models.CharField('電話番号', max_length=12)
    address = models.TextField('住所')


class Itemization(models.Model):
    pass


class ExtraSectionFields(models.Model):
    field = models.ForeignKey(ExtraField)
    section = models.ForeignKey('ExtraSection')


class ExtraSection(models.Model):
    section_name = models.CharField(max_length=255)
    fields = models.ManyToManyField(through=ExtraSectionFields)
    
