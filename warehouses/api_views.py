# api_views.py
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Coming, ProductArrival, ProductStock
from .serializers import ComingSerializer, ProductArrivalSerializer, ProductStockSerializer
from collections import defaultdict
from .models import ProductExpense
from .serializers import ProductExpenseSerializer
from django.utils.dateparse import parse_date


class ComingAPIView(APIView):
    def get(self, request):
        comings = Coming.objects.all()
        serializer = ComingSerializer(comings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ComingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductArrivalAPIView(APIView):
    def get(self, request):
        products = ProductArrival.objects.all()
        serializer = ProductArrivalSerializer(products, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductArrivalSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductExpenseAPIView(APIView):
    """
    API для вывода полного отчета по расходам с фильтрацией по дате.
    """

    def get(self, request):
        start_date = request.query_params.get("start_date")  # Начальная дата
        end_date = request.query_params.get("end_date")  # Конечная дата
        expenses = ProductExpense.objects.all()

        if start_date:
            expenses = expenses.filter(date__gte=parse_date(start_date))
        if end_date:
            expenses = expenses.filter(date__lte=parse_date(end_date))

        serializer = ProductExpenseSerializer(expenses, many=True)
        warehouse_report = defaultdict(lambda: {"warehouse_name": "", "total": 0, "expenses": []})

        for expense in serializer.data:
            warehouse_id = expense["warehouse"]
            warehouse_name = expense["warehouse_name"]
            total = expense["total"]

            warehouse_report[warehouse_id]["warehouse_name"] = warehouse_name
            warehouse_report[warehouse_id]["total"] += total
            warehouse_report[warehouse_id]["expenses"].append(expense)

        overall_total = sum(report["total"] for report in warehouse_report.values())

        return Response({
            "overall_total": overall_total,
            "warehouse_report": list(warehouse_report.values()),
        })


class WarehouseStocksAPIView(APIView):
    """
    API для отображения остатков по складам.
    """

    def get(self, request):
        data = {}
        product_stocks = ProductStock.objects.select_related('warehouse', 'product')

        for stock in product_stocks:
            warehouse_name = stock.warehouse.name
            if warehouse_name not in data:
                data[warehouse_name] = []

            data[warehouse_name].append({
                "product_name": stock.product.name,
                "quantity": float(stock.quantity),
                "barcode": stock.barcode,
            })

        return Response(data)
