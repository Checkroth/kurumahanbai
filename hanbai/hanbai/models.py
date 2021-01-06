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
        if self.value_type == FieldTypeChoices.STRING:
            return self.string_value
        elif self.value_type == FieldTypeChoices.INTEGER:
            return self.integer_value


class CarInfo(models.Model):
    class YearChoices(models.TextChoices):
        SEIREKI = '西', '西暦'
        SHOWA = '昭', '昭和'
        HEISEI = '平', '平成'
        REIWA = '令', '令和'

    class DistanceChoices(models.TextChoices):
        MILES = 'M', 'マイル'
        KILOMETERS = 'KM', 'キロメータ'

    car_name = models.CharField('社名', max_length=255, blank=False)
    model_year = models.CharField(max_length=2, '年式_年', choices=YearChoices)
    model_month = models.IntegerField('年式_月', validators=[validators.MinValueValidator(1),
                                                             validators.MaxValueValidator(12)])
    car_model = models.CharField('型式', max_length=255, blank=False)
    distance_traveled_unit = models.CharField(max_length=3,
                                              choices=DistanceChoices,
                                              default=DistanceChoices.KILOMETERS)
    distance_traveled = models.IntegerField('走行', validators=[validators.MinValueValidator(0)])
    doors = models.IntegerField('ドア', validators=[validators.MinValueValidator(1)], default=5)
    color = models.CharField('色', max_length=255, blank=False)
    model_number = models.CharField('車台番号', max_length=255, blank=False)
    registration_number = models.CharField('登録番号', max_length=255, blank=False)
    inspection_year = models.IntegerField('車検_年')
    inspection_month = models.IntegerField('車検_月', validators=[validators.MinValueValidator(1),
                                                                  validators.MaxValueValidator(12)])
    expeted_delivery_month = models.IntegerField('納車予定月', validators=[validators.MinValueValidator(1),
                                                                           validators.MaxValueValidator(12)])
    expected_delivery_year = models.IntegerField('納車予定年')
    extra_equipment = models.TextField('装備')


class PreviousOwnerInfo(models.Model):
    pass


class CustomerInfo(models.Model):
    pass


class Itemization(models.Model):
    pass


class ExtraSectionFields(models.Model):
    field = models.ForeignKey(ExtraField)
    section = models.ForeignKey(ExtraSection)


class ExtraSection(models.Model):
    section_name = models.CharField(max_length=255)
    
