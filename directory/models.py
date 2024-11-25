from django.db import models
from PIL import Image
import os
from io import BytesIO
from django.core.files.base import ContentFile


class Branch(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название филиала")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"


class GroupProduct(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название группы")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группу товаров"
        verbose_name_plural = "Группы товаров"


class Product(models.Model):
    UNIT_CHOICES = [
        ('кг', 'Килограммы'),
        ('шт', 'Штуки'),
        ('мт', 'Метры'),
        ('упак', 'Упаковки'),
    ]

    name = models.CharField(max_length=255, verbose_name="Название товара")
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, verbose_name="Единица измерения")
    product_group = models.ForeignKey(GroupProduct, on_delete=models.CASCADE, related_name='product_group',
                                      verbose_name="Группа товара")
    photo = models.ImageField(upload_to='product_photos/', blank=True, null=True, verbose_name="Фото")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def save(self, *args, **kwargs):
        if self.photo:
            img = Image.open(self.photo)
            img = img.convert("RGB")
            filename, _ = os.path.splitext(self.photo.name)
            webp_filename = f"{filename}.webp"
            temp_buffer = BytesIO()
            img.save(temp_buffer, format="WEBP", quality=85)
            temp_buffer.seek(0)

            self.photo.save(webp_filename, ContentFile(temp_buffer.read()), save=False)
            temp_buffer.close()

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
