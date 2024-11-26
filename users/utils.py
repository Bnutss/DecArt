from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils import timezone


def get_date_range(filter_option):
    """
    Возвращает диапазон дат (start_date, end_date) на основе выбранного фильтра.
    """
    now = timezone.now()

    if filter_option == 'today':
        start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    elif filter_option == 'year':
        start_date = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now
    else:  # По умолчанию - текущий месяц
        start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now

    return start_date, end_date


def calculate_metric(model, date_field, filter_option, metric_field=None, aggregate_func=Sum):
    """
    Универсальная функция для подсчета метрик (например, суммы или количества).
    - model: модель Django, по которой выполняется запрос.
    - date_field: поле даты для фильтрации.
    - filter_option: выбранный фильтр ('today', 'month', 'year').
    - metric_field: поле или вычисляемое выражение для подсчета метрики (например, F('quantity') * F('unit_price')).
    - aggregate_func: агрегатная функция (по умолчанию Sum).
    """
    start_date, end_date = get_date_range(filter_option)

    query = model.objects.filter(**{
        f"{date_field}__gte": start_date,
        f"{date_field}__lte": end_date,
    })

    if metric_field:
        # Если metric_field — это выражение, обернем его в ExpressionWrapper
        if isinstance(metric_field, ExpressionWrapper):
            return query.aggregate(total=aggregate_func(metric_field))['total'] or 0
        else:
            return query.aggregate(total=aggregate_func(F(metric_field)))['total'] or 0
    return query.aggregate(total=aggregate_func('id'))['total'] or 0  # По умолчанию — подсчет записей
