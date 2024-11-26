from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import logout
from .utils import calculate_metric
from django.db.models import ExpressionWrapper, DecimalField, F

from warehouses.models import ProductExpense, ProductArrival


class LoginView(View):
    def get(self, request):
        form = AuthenticationForm()
        return render(request, 'users/login.html', {'form': form})

    def post(self, request):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('users:dashboard')
            else:
                form.add_error(None, "Неправильное имя пользователя или пароль.")
        return render(request, 'users/login.html', {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('users:login')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'mainmenu/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_option = self.request.GET.get('filter', 'month')
        total_revenue_expression = ExpressionWrapper(
            F('quantity') * F('unit_price'),
            output_field=DecimalField(max_digits=10, decimal_places=2)
        )
        context['total_revenue'] = calculate_metric(
            model=ProductExpense,
            date_field='date',
            filter_option=filter_option,
            metric_field=total_revenue_expression
        )
        context['total_arrivals'] = calculate_metric(
            model=ProductArrival,
            date_field='date',
            filter_option=filter_option,
            metric_field='quantity'
        )
        context['current_filter'] = filter_option
        return context
