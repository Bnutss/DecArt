from django.urls import path
from .views import LoginView, DashboardView

app_name = 'users'

urlpatterns = [
    path('', LoginView.as_view(), name='login'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
