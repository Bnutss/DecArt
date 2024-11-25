from django.urls import path
from .views import BranchListView, WarehousesListView, ProductsListView, BranchCreateView, BranchDeleteView, \
    WarehousesCreateView, WarehousesDeleteView, ProductsCreateView, ProductsDeleteView, ProductGroupListView, \
    ProductGroupCreateView, ProductGroupDeleteView

app_name = 'directory'

urlpatterns = [
    path('branches/', BranchListView.as_view(), name='branch-list'),
    path('branch/create/', BranchCreateView.as_view(), name='branch-create'),
    path('branch/delete/<int:pk>/', BranchDeleteView.as_view(), name='branch-delete'),
    path('warehouses/', WarehousesListView.as_view(), name='warehouse-list'),
    path('warehouse/create/', WarehousesCreateView.as_view(), name='warehouse-create'),
    path('warehouse/delete/<int:pk>/', WarehousesDeleteView.as_view(), name='warehouse-delete'),
    path('products/', ProductsListView.as_view(), name='product-list'),
    path('product/create/', ProductsCreateView.as_view(), name='product-create'),
    path('product/delete/<int:pk>/', ProductsDeleteView.as_view(), name='product-delete'),
    path('groups/', ProductGroupListView.as_view(), name='group-list'),
    path('group/create/', ProductGroupCreateView.as_view(), name='group-create'),
    path('group/delete/<int:pk>/', ProductGroupDeleteView.as_view(), name='group-delete'),

]
