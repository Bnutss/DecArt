from rest_framework import serializers
from .models import Coming, ProductArrival, ProductExpense, ProductStock


class ProductArrivalSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductArrival
        fields = ['id', 'product_name', 'quantity', 'unit_price']


class ComingSerializer(serializers.ModelSerializer):
    products = ProductArrivalSerializer(many=True, read_only=True)
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    total_without_vat = serializers.SerializerMethodField()
    total_with_vat = serializers.SerializerMethodField()

    class Meta:
        model = Coming
        fields = [
            'id', 'warehouse_name', 'contract_number', 'invoice_number',
            'vat_percentage', 'comment', 'created_at', 'is_posted',
            'posting_date', 'products', 'total_without_vat', 'total_with_vat'
        ]

    def get_total_without_vat(self, obj):
        """
        Расчет общей суммы без НДС.
        """
        total = 0
        for product in obj.products.all():
            total += product.quantity * product.unit_price
        return total

    def get_total_with_vat(self, obj):
        """
        Расчет общей суммы с НДС.
        """
        total_without_vat = self.get_total_without_vat(obj)
        vat_percentage = obj.vat_percentage
        return total_without_vat * (1 + vat_percentage / 100)


class ProductExpenseSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    total = serializers.SerializerMethodField()  # Сумма за количество (quantity * unit_price)

    class Meta:
        model = ProductExpense
        fields = [
            'id', 'quantity', 'unit_price', 'date',
            'warehouse', 'warehouse_name',
            'product', 'product_name',
            'total'
        ]

    def get_total(self, obj):
        return float(obj.quantity) * float(obj.unit_price)


class ProductStockSerializer(serializers.ModelSerializer):
    warehouse_name = serializers.CharField(source='warehouse.name', read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = ProductStock
        fields = ['id', 'warehouse', 'warehouse_name', 'product', 'product_name', 'quantity', 'barcode']
