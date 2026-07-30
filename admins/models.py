from django.db import models

class SalesData(models.Model):

    store = models.IntegerField()

    weekly_sales = models.FloatField()

    holiday_flag = models.IntegerField()

    temperature = models.FloatField()

    fuel_price = models.FloatField()

    cpi = models.FloatField()

    unemployment = models.FloatField()

    year = models.IntegerField()

    month = models.IntegerField()

    week = models.IntegerField()

    quarter = models.IntegerField()

    def __str__(self):
        return f"{self.store} - {self.weekly_sales}"
class Dataset(models.Model):

    name = models.CharField(max_length=255)

    csv_file = models.FileField(
        upload_to='datasets/'
    )

    uploaded_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name
    

class PredictionHistory(models.Model):

    store = models.IntegerField()

    holiday_flag = models.IntegerField()

    temperature = models.FloatField()

    fuel_price = models.FloatField()

    cpi = models.FloatField()

    unemployment = models.FloatField()
    year = models.IntegerField(default=2025)
    month = models.IntegerField(default=1)
    week = models.IntegerField(default=1)
    quarter = models.IntegerField(default=1)

    predicted_sales = models.FloatField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.store} - {self.predicted_sales}"