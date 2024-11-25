from django import forms
from .models import Branch, Product, GroupProduct
from warehouses.models import Warehouse


class BranchForm(forms.ModelForm):
    class Meta:
        model = Branch
        fields = ['name']


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = ['name', 'branch']


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'unit', 'product_group', 'photo']


class ProductGroupForm(forms.ModelForm):
    class Meta:
        model = GroupProduct
        fields = ['name']
