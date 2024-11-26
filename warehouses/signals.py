from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import ProductArrival, ProductStock, ProductExpense, WarehouseTransfer


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


@receiver(post_save, sender=WarehouseTransfer)
def update_stock_on_transfer(sender, instance, created, **kwargs):
    """
    Обновляет остатки и переносит штрих-код при перемещении.
    """
    if created:

        source_stock = ProductStock.objects.filter(
            warehouse=instance.source_warehouse,
            product=instance.product
        ).first()

        if not source_stock or source_stock.quantity < instance.quantity:
            raise ValueError(
                f"Недостаточно товара {instance.product.name} на складе {instance.source_warehouse.name}"
            )

        source_stock.quantity -= instance.quantity
        source_stock.save()

        destination_stock, created = ProductStock.objects.get_or_create(
            warehouse=instance.destination_warehouse,
            product=instance.product,
            defaults={"quantity": 0, "barcode": source_stock.barcode}
        )

        if not created:
            destination_stock.barcode = source_stock.barcode

        destination_stock.quantity += instance.quantity
        destination_stock.save()
