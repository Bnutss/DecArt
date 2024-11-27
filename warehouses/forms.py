from django import forms
from .models import Coming, WarehouseTransfer


class ComingForm(forms.ModelForm):
    class Meta:
        model = Coming
        fields = ['warehouse', 'contract_number', 'invoice_number', 'vat_percentage', 'comment']


class WarehouseTransferForm(forms.ModelForm):
    class Meta:
        model = WarehouseTransfer
        fields = ['source_warehouse', 'destination_warehouse', 'product', 'quantity']
