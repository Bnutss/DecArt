from django import forms
from .models import Coming


class ComingForm(forms.ModelForm):
    class Meta:
        model = Coming
        fields = ['warehouse', 'contract_number', 'invoice_number', 'comment']
