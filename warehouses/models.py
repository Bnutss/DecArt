from django.db import models
from directory.models import Branch, Product
import random
from django.db import transaction
from django.utils.timezone import now


class Warehouse(models.Model):
    """
    Модель склада, привязанного к определенному филиалу.
    """
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name="warehouses", verbose_name="Филиал")
    name = models.CharField(max_length=255, verbose_name="Название склада")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"{self.name} ({self.branch.name})"

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"


class Coming(models.Model):
    """
    Модель прихода товаров на склад.
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="arrivals", verbose_name="Склад")
    contract_number = models.CharField(max_length=255, verbose_name="Номер договора", blank=True, null=True)
    invoice_number = models.CharField(max_length=255, verbose_name="Счет-фактура", blank=True, null=True)
    vat_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=12.00, verbose_name="НДС (%)",
                                         help_text="Укажите НДС в процентах (например, 12.00)")
    comment = models.TextField(verbose_name="Комментарий", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    is_posted = models.BooleanField(default=False, verbose_name="Проводка")
    posting_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата проводки")

    def save(self, *args, **kwargs):
        if self.is_posted and not self.posting_date:
            self.posting_date = now()
        if not self.is_posted:
            self.posting_date = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.warehouse} - {self.contract_number or 'Без договора'}"

    class Meta:
        verbose_name = "Приход"
        verbose_name_plural = "Приходы"


class ProductArrival(models.Model):
    """
    Модель для учета товаров, поступающих на склад.
    """
    coming = models.ForeignKey(Coming, on_delete=models.CASCADE, related_name="products", verbose_name="Приход")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="arrivals", verbose_name="Товар")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата прихода")
    barcode = models.CharField(max_length=14, blank=True, null=True, verbose_name="Штрих-код")

    def __str__(self):
        """
        Возвращает строковое представление записи.
        """
        return f"{self.product.name} - {self.quantity} ({self.coming.warehouse})"

    def save(self, *args, **kwargs):
        """
        Перед сохранением проверяет, есть ли штрих-код для данного товара.
        Если нет, генерирует новый.
        """
        if not self.barcode:
            # Проверяем, есть ли уже записи с таким же товаром
            existing_arrival = ProductArrival.objects.filter(product=self.product).first()
            if existing_arrival and existing_arrival.barcode:
                self.barcode = existing_arrival.barcode
            else:
                self.barcode = self.generate_barcode()

        super().save(*args, **kwargs)

    def generate_barcode(self):
        """
        Генерирует уникальный штрих-код с префиксом DECART и 8 случайными цифрами.
        """
        prefix = "DecArt"
        unique_number = f"{random.randint(10000000, 99999999)}"
        return prefix + unique_number

    class Meta:
        verbose_name = "Приход товара"
        verbose_name_plural = "Приход товаров"


class WarehouseTransfer(models.Model):
    """
    Модель для учета перемещения товаров между складами.
    """
    source_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="outgoing_transfers",
                                         verbose_name="Склад-отправитель")
    destination_warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="incoming_transfers",
                                              verbose_name="Склад-получатель")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="transfers", verbose_name="Товар"
                                )
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    transfer_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата перемещения")

    def __str__(self):
        return f"Перемещение {self.quantity} {self.product.name} из {self.source_warehouse.name} в {self.destination_warehouse.name}"

    class Meta:
        verbose_name = "Перемещение товара"
        verbose_name_plural = "Перемещения товаров"


class ProductStock(models.Model):
    """
    Модель для учета остатков товаров на складе.
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="stocks", verbose_name="Склад")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="stocks", verbose_name="Товар")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Остаток")
    barcode = models.CharField(max_length=14, blank=True, null=True, verbose_name="Штрих-код")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} ({self.warehouse.name})"

    class Meta:
        verbose_name = "Остаток товара"
        verbose_name_plural = "Остатки товаров"
        unique_together = ('warehouse', 'product')

    @transaction.atomic
    def transfer_to(self, destination_warehouse, quantity):
        """
        Перемещает указанное количество товара на другой склад, включая передачу штрих-кода.
        """
        if quantity <= 0:
            raise ValueError("Количество для перемещения должно быть больше 0.")

        if self.quantity < quantity:
            raise ValueError(f"Недостаточно товара на складе {self.warehouse.name}. Доступно: {self.quantity}.")

        self.quantity -= quantity
        self.save()

        destination_stock, created = ProductStock.objects.get_or_create(
            warehouse=destination_warehouse,
            product=self.product,
            defaults={"quantity": 0, "barcode": self.barcode}
        )

        if not created:
            destination_stock.barcode = self.barcode
        destination_stock.quantity += quantity
        destination_stock.save()

        WarehouseTransfer.objects.create(
            source_warehouse=self.warehouse,
            destination_warehouse=destination_warehouse,
            product=self.product,
            quantity=quantity
        )


class ProductExpense(models.Model):
    """
    Модель для учета расхода товаров со склада.
    """
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name="expenses", verbose_name="Склад")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="expenses", verbose_name="Товар")
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Количество")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу")
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата расхода")

    def __str__(self):
        return f"{self.product.name} - {self.quantity} ({self.warehouse.name})"

    class Meta:
        verbose_name = "Расход товара"
        verbose_name_plural = "Расход товаров"
