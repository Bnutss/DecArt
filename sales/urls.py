from django.urls import path
from .views import product_management_view, ProductExpenseReportView, send_expense_report_to_telegram

app_name = 'sales'

urlpatterns = [
    path('manage-product/', product_management_view, name='product_management_view'),
    path('report/', ProductExpenseReportView.as_view(), name='product_expense_report'),
    path('report/send_to_telegram/', send_expense_report_to_telegram, name='send_expense_report_to_telegram'),

]
