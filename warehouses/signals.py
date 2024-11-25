from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import ProductArrival, ProductStock, ProductExpense


@receiver(pre_save, sender=ProductArrival)
def generate_barcode_if_empty(sender, instance, **kwargs):
    """
    Автоматически генерирует штрих-код, если он отсутствует.
    """
    if not instance.barcode:
        instance.barcode = instance.generate_barcode()


@receiver(post_save, sender=ProductArrival)
def update_stock_on_arrival(sender, instance, created, **kwargs):
    """
    Обновляет остаток товара и переносит штрих-код при добавлении нового прихода.
    """
    if created:
        stock, created = ProductStock.objects.get_or_create(
            warehouse=instance.coming.warehouse,
            product=instance.product
        )
        stock.quantity += instance.quantity
        stock.barcode = instance.barcode  # Переносим штрих-код
        stock.save()


@receiver(post_save, sender=ProductExpense)
def update_stock_on_expense(sender, instance, created, **kwargs):
    """
    Уменьшает остаток товара при добавлении нового расхода.
    """
    if created:
        try:
            stock = ProductStock.objects.get(
                warehouse=instance.warehouse,
                product=instance.product
            )

            if stock.quantity < instance.quantity:
                raise ValueError(f"Недостаточно товара {instance.product.name} на складе {instance.warehouse.name}")

            stock.quantity -= instance.quantity
            stock.save()
        except ProductStock.DoesNotExist:
            raise ValueError(f"Товар {instance.product.name} отсутствует на складе {instance.warehouse.name}")
