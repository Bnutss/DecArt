from decimal import Decimal, InvalidOperation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from directory.models import Product
from warehouses.models import ProductStock, ProductExpense, Warehouse
from django.views.generic import ListView
from django.db.models import Sum, F
from django.utils.timezone import now
from datetime import date
import openpyxl
from django.http import HttpResponse
import openpyxl
from django.http import JsonResponse
from tempfile import NamedTemporaryFile
import requests

TELEGRAM_BOT_TOKEN = "7867735433:AAEOO4CII3sBDwBfKUWy4FapOsNLgKRl0Vc"
TELEGRAM_CHAT_ID = "-4542685446"


@login_required
def product_management_view(request):
    """
    Управление товаром: поиск по штрих-коду, выбор склада и продажа.
    """
    barcode = request.GET.get('barcode', '').strip() if request.method == 'GET' else None
    context = {}

    if 'total_sales' not in request.session:
        request.session['total_sales'] = 0
    if 'sold_items' not in request.session:
        request.session['sold_items'] = []

    if request.method == 'POST':

        if request.POST.get('action') == 'reset_total':
            request.session['total_sales'] = 0
            request.session['sold_items'] = []
            request.session.modified = True
            messages.success(request, "Общая сумма и список проданных товаров обнулены.")
            return redirect('/sales/manage-product/')

        barcode = request.POST.get('barcode', '').strip()
        quantity = request.POST.get('quantity', 0)
        selling_price = request.POST.get('selling_price', 0)
        warehouse_id = request.POST.get('warehouse', None)

        try:
            quantity = Decimal(quantity)
            selling_price = Decimal(selling_price)
            warehouse = Warehouse.objects.get(id=warehouse_id)
            stock = ProductStock.objects.filter(barcode=barcode, warehouse=warehouse).first()

            if stock and stock.quantity >= quantity:
                expense = ProductExpense.objects.create(
                    warehouse=warehouse,
                    product=stock.product,
                    quantity=quantity,
                    unit_price=selling_price,
                )

                stock.quantity -= quantity
                stock.save()
                request.session['total_sales'] += float(quantity * selling_price)
                request.session['sold_items'].append({
                    'name': stock.product.name,
                    'quantity': int(quantity),
                    'price': float(selling_price),
                    'total': float(quantity * selling_price),
                })
                request.session.modified = True

                messages.success(request, f"Продажа успешно оформлена. Остаток: {stock.quantity}.")
            else:
                messages.error(request, "Недостаточно товара на выбранном складе.")
        except (ValueError, InvalidOperation):
            messages.error(request, "Некорректное количество или цена.")
        except Warehouse.DoesNotExist:
            messages.error(request, "Выбранный склад не найден.")
        return redirect(f'/sales/manage-product/?barcode={barcode}')

    if barcode:
        stocks = ProductStock.objects.filter(barcode=barcode)
        if stocks.exists():
            product = stocks.first().product
            context = {
                'product': product,
                'stocks': stocks,
                'barcode': barcode,
                'total_sales': request.session['total_sales'],
                'sold_items': request.session['sold_items'],
            }
        else:
            context['error'] = "Товар с указанным штрих-кодом не найден."
            context['total_sales'] = request.session['total_sales']
            context['sold_items'] = request.session['sold_items']
    else:
        context['total_sales'] = request.session['total_sales']
        context['sold_items'] = request.session['sold_items']

    return render(request, 'sales/product_management.html', context)


class ProductExpenseReportView(LoginRequiredMixin, ListView):
    """
    Представление для отображения отчета по расходам.
    """
    model = ProductExpense
    template_name = "sales/reporting_list.html"
    context_object_name = "expenses"

    def get_queryset(self):
        """
        Получает отфильтрованный набор данных на основе параметров запроса.
        Если даты не указаны, фильтрует данные за текущий день.
        """
        queryset = ProductExpense.objects.all()
        warehouse_id = self.request.GET.get("warehouse")
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)

        product_id = self.request.GET.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if not start_date and not end_date:
            today = date.today()
            queryset = queryset.filter(date__date=today)
        elif start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавляет дополнительные данные для шаблона.
        """
        context = super().get_context_data(**kwargs)
        total_data = self.get_queryset().aggregate(
            total_quantity=Sum('quantity'),
            total_cost=Sum(F('quantity') * F('unit_price'))
        )

        today = date.today()
        context.update({
            "total_quantity": total_data["total_quantity"] or 0,
            "total_cost": total_data["total_cost"] or 0,
            "warehouses": Warehouse.objects.all(),
            "products": Product.objects.all(),
            "start_date": self.request.GET.get("start_date", today),
            "end_date": self.request.GET.get("end_date", today),
        })

        return context


def send_expense_report_to_telegram(request):
    """
    Генерирует Excel-отчет по расходам и отправляет его через Telegram.
    После успешной отправки перенаправляет пользователя обратно на страницу отчета.
    """
    warehouse_id = request.GET.get("warehouse")
    product_id = request.GET.get("product")
    start_date = request.GET.get("start_date")
    end_date = request.GET.get("end_date")

    queryset = ProductExpense.objects.all()
    if warehouse_id:
        queryset = queryset.filter(warehouse_id=warehouse_id)
    if product_id:
        queryset = queryset.filter(product_id=product_id)
    if start_date and end_date:
        queryset = queryset.filter(date__range=[start_date, end_date])

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Отчет по расходам"
    headers = ["Склад", "Филиал", "Товар", "Количество", "Цена за единицу", "Общая цена", "Дата"]
    sheet.append(headers)

    for expense in queryset:
        sheet.append([
            expense.warehouse.name,
            str(expense.warehouse.branch),
            expense.product.name,
            expense.quantity,
            expense.unit_price,
            expense.quantity * expense.unit_price,
            expense.date.strftime("%d.%m.%Y %H:%M"),
        ])

    total_data = queryset.aggregate(
        total_quantity=Sum('quantity'),
        total_cost=Sum(F('quantity') * F('unit_price'))
    )
    sheet.append([])
    sheet.append(["", "", "Итого:", total_data["total_quantity"], "", total_data["total_cost"], ""])

    file_name = "Отчет.xlsx"
    with NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        workbook.save(tmp_file.name)
        tmp_file_path = tmp_file.name

    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument"
    with open(tmp_file_path, "rb") as file:
        files = {
            "document": (file_name, file),
        }
        data = {
            "chat_id": TELEGRAM_CHAT_ID,
            "caption": "Отчет по расходам",
        }
        response = requests.post(telegram_url, data=data, files=files)

    if response.status_code == 200:
        return redirect('sales:product_expense_report')
    else:
        return redirect('sales:product_expense_report', {'error': response.text})
