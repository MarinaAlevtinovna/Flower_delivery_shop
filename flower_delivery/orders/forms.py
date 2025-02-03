from django import forms

class OrderForm(forms.Form):
    name = forms.CharField(label="Ваше имя", max_length=100, required=True)
    phone = forms.CharField(label="Телефон", max_length=20, required=True)
    address = forms.CharField(label="Адрес доставки", widget=forms.Textarea, required=True)
