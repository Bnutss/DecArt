from django.urls import path
# API VIEWS
from .api_views import ComingAPIView, ProductArrivalAPIView, ProductExpenseAPIView, WarehouseStocksAPIView
# VIEWS
from .views import ComingListView, ComingCreateView, ComingDeleteView, ComingDetailView, ProductArrivalCreateView, \
    ProductArrivalDeleteView, ProductArrivalDownloadPDFView, ProductStockListView, ProductStockExportView, \
    WarehouseTransferListView, WarehouseTransferCreateView, generate_pdf

app_name = 'warehouses'

urlpatterns = [
    path('comings/', ComingListView.as_view(), name='coming-list'),
    path('coming/create/', ComingCreateView.as_view(), name='coming-create'),
    path('coming/<int:pk>/', ComingDetailView.as_view(), name='coming-detail'),
    path('coming/<int:coming_id>/add-product/', ProductArrivalCreateView.as_view(), name='product-arrival-create'),
    path('product/delete/<int:pk>/', ProductArrivalDeleteView.as_view(), name='product-delete'),
    path('coming/delete/<int:pk>/', ComingDeleteView.as_view(), name='coming-delete'),
    path('product/download-pdf/<int:pk>/', ProductArrivalDownloadPDFView.as_view(), name='product-download-pdf'),
    path('stocks/', ProductStockListView.as_view(), name='product_stock_list'),
    path('export/', ProductStockExportView.as_view(), name='product_stock_export'),
    path('transfers/', WarehouseTransferListView.as_view(), name='transfer_list'),
    path('transfer/create/', WarehouseTransferCreateView.as_view(), name='transfer-create'),
    path('coming/<int:coming_id>/pdf/', generate_pdf, name='generate_pdf'),
    path('api/comings/', ComingAPIView.as_view(), name='api-coming-list'),
    path('api/product-arrivals/', ProductArrivalAPIView.as_view(), name='product-arrival-list'),
    path('api/product-expenses/', ProductExpenseAPIView.as_view(), name='product-expense-list'),
    path('api/product-expenses/<int:pk>/', ProductExpenseAPIView.as_view(), name='product-expense-detail'),
    path('api/product-stocks/', WarehouseStocksAPIView.as_view(), name='product_stock_list'),

]
