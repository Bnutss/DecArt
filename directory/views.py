from django.views.generic import ListView, CreateView, DeleteView
from .models import Branch, Product, GroupProduct
from warehouses.models import Warehouse
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import BranchForm, WarehouseForm, ProductForm, ProductGroupForm
from django.urls import reverse_lazy


class BranchListView(LoginRequiredMixin, ListView):
    model = Branch
    template_name = 'directory/branches_list.html'
    context_object_name = 'branches'


class BranchCreateView(CreateView):
    model = Branch
    form_class = BranchForm
    template_name = 'directory/branches_list.html'
    success_url = reverse_lazy('directory:branch-list')


class BranchDeleteView(DeleteView):
    model = Branch
    success_url = reverse_lazy('directory:branch-list')
    template_name = 'directory/branches_list.html'


class WarehousesListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'directory/warehouses_list.html'
    context_object_name = 'warehouses'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['branches'] = Branch.objects.all()
        return context


class WarehousesCreateView(CreateView):
    model = Warehouse
    form_class = WarehouseForm
    template_name = 'directory/warehouses_list.html'
    success_url = reverse_lazy('directory:warehouse-list')


class WarehousesDeleteView(DeleteView):
    model = Warehouse
    success_url = reverse_lazy('directory:warehouse-list')
    template_name = 'directory/warehouses_list.html'


class ProductsListView(LoginRequiredMixin, ListView):
    model = Product
    template_name = 'directory/products_list.html'
    context_object_name = 'products'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_groups'] = GroupProduct.objects.all()
        context['form'] = ProductForm()
        return context


class ProductsCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'directory/products_list.html'
    success_url = reverse_lazy('directory:product-list')


class ProductsDeleteView(DeleteView):
    model = Product
    success_url = reverse_lazy('directory:product-list')
    template_name = 'directory/products_list.html'


class ProductGroupListView(LoginRequiredMixin, ListView):
    model = GroupProduct
    template_name = 'directory/product_group_list.html'
    context_object_name = 'groups'


class ProductGroupCreateView(CreateView):
    model = GroupProduct
    form_class = ProductGroupForm
    template_name = 'directory/product_group_list.html'
    success_url = reverse_lazy('directory:group-list')


class ProductGroupDeleteView(DeleteView):
    model = GroupProduct
    success_url = reverse_lazy('directory:group-list')
    template_name = 'directory/product_group_list.html'
