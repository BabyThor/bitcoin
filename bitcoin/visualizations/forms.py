from django import forms

class SettingsForm(forms.Form):
    diff_eu_th = forms.CharField(label='EU-TH %', max_length=100)
    diff_us_th = forms.CharField(label='US-TH %', max_length=100)
    diff_currency = forms.CharField(label='CURRENCY %', max_length=100)