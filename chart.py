import jdatetime
from django.db.models import QuerySet
from django.db.models.aggregates import Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear


PERSIAN_MONTHS = [
    '',  # placeholder for index 0
    'فروردین', 'اردیبهشت', 'خرداد',
    'تیر', 'مرداد', 'شهریور',
    'مهر', 'آبان', 'آذر',
    'دی', 'بهمن', 'اسفند'
]


def product_fluctuation_chart(step: str = 'month', queryset: QuerySet=None) -> dict[str, list[str | int]]:
    """
    function: add one step to date. for filling the gap between dates
    normalize: prevent duplication
    """
    step_operations = {
        'day': {
            'trunc': TruncDay,
            'function': lambda d: d + jdatetime.timedelta(days=1),
            'normalize': lambda d: d
        },
        'week': {
            'trunc': TruncWeek,
            'function': lambda d: d + jdatetime.timedelta(weeks=1),
            'normalize': lambda d: d - jdatetime.timedelta(days=d.weekday())
        },
        'month': {
            'trunc': TruncMonth,
            'function': lambda d: d.replace(month=d.month + 1 if d.month < 12 else 1,
                                            year=d.year if d.month < 12 else d.year + 1),
            'normalize': lambda d: jdatetime.date(d.year, d.month, 1)
        },
        'year': {
            'trunc': TruncYear,
            'function': lambda d: d.replace(year=d.year + 1),
            'normalize': lambda d: jdatetime.date(d.year, 1, 1)
        }
    }

    queryset = (
        queryset
        .annotate(step_date=step_operations[step]['trunc']('date'))
        .values('step_date')
        .annotate(total=Sum('price'))
        .order_by('step_date')
    )

    result = {
        'date': [],
        'total': []
    }
    last_date = None

    for entry in queryset:
        if entry['step_date'] is None:
            continue
        gregorian_date = entry['step_date'] # add .date() if step_date format is datetime
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        jalali_date_normalized = step_operations[step]['normalize'](jalali_date)

        # fill the gap
        if not last_date:
            last_date = jalali_date_normalized
        while last_date and jalali_date_normalized > step_operations[step]['function'](last_date):
            last_date = step_operations[step]['function'](last_date)
            if last_date == jalali_date_normalized:
                break

            persian_date_str = f"{last_date.year}-{PERSIAN_MONTHS[last_date.month]}-{last_date.day}"
            result['date'].append(persian_date_str)
            result['total'].append(result['total'][-1])

        last_date = jalali_date_normalized

        persian_date_str = f"{last_date.year}-{PERSIAN_MONTHS[last_date.month]}-{last_date.day}"
        result['date'].append(persian_date_str)
        result['total'].append(entry['total'])

    return result
