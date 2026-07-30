from django import forms


class PredictionForm(forms.Form):

    store = forms.IntegerField(label="Store")

    holiday_flag = forms.ChoiceField(
        label="Holiday Flag",
        choices=[
            (0, "No"),
            (1, "Yes")
        ]
    )

    temperature = forms.FloatField(label="Temperature")

    fuel_price = forms.FloatField(label="Fuel Price")

    cpi = forms.FloatField(label="CPI")

    unemployment = forms.FloatField(label="Unemployment")

    year = forms.IntegerField(label="Year")

    month = forms.IntegerField(label="Month")

    week = forms.IntegerField(label="Week")

    quarter = forms.IntegerField(label="Quarter")