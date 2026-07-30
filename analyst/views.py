from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from admins.models import PredictionHistory, SalesData


from django.db.models import Sum

def analyst_dashboard(request):

    total_sales = SalesData.objects.count()

    total_orders = SalesData.objects.count()

    total_revenue = SalesData.objects.aggregate(
        total=Sum("weekly_sales")
    )["total"] or 0

    total_products = SalesData.objects.values(
        "store"
    ).distinct().count()

    context = {
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "total_products": total_products,
    }

    return render(
        request,
        "analyst/dashboard.html",
        context
    )

from django.db.models import Sum, Avg, Max, Min
from admins.models import SalesData
import json


def sales_trends(request):

    total_sales = SalesData.objects.aggregate(
        total=Sum('weekly_sales')
    )['total'] or 0

    average_sales = SalesData.objects.aggregate(
        avg=Avg('weekly_sales')
    )['avg'] or 0

    highest_sales = SalesData.objects.aggregate(
        high=Max('weekly_sales')
    )['high'] or 0

    lowest_sales = SalesData.objects.aggregate(
        low=Min('weekly_sales')
    )['low'] or 0


    monthly_sales = (
        SalesData.objects
        .values('month')
        .annotate(total_sales=Sum('weekly_sales'))
        .order_by('month')
    )

    month_labels = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    month_values = [0]*12

    for item in monthly_sales:
        month = item['month']
        if month:
            month_values[month-1] = float(item['total_sales'])
    top_sales = SalesData.objects.order_by('-weekly_sales')[:10]

    monthly_summary = (
        SalesData.objects
        .values('month')
        .annotate(
            total_sales=Sum('weekly_sales'),
            average_sales=Avg('weekly_sales')
        )
        .order_by('month')
    )

    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }

    for item in monthly_summary:
        item["month_name"] = month_names.get(item["month"], "Unknown")
    context = {

    'total_sales': total_sales,
    'average_sales': average_sales,
    'highest_sales': highest_sales,
    'lowest_sales': lowest_sales,

    'month_labels': json.dumps(month_labels),
    'month_values': json.dumps(month_values),

    'top_sales': top_sales,
    'monthly_summary': monthly_summary,

    }

    return render(
        request,
        'analyst/sales_trends.html',
        context
    )

def growth_analysis(request):
    monthly_sales = (
    SalesData.objects
    .values('month')
    .annotate(total_sales=Sum('weekly_sales'))
    .order_by('month')
    )
    month_names = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
    }
    growth_data = []

    previous_sales = None

    for item in monthly_sales:

        current_sales = item['total_sales']

        if previous_sales is None:

            growth = None

        else:

            growth = (
                (current_sales - previous_sales)
                / previous_sales
            ) * 100

        growth_data.append({

            'month': month_names[item['month']],

            'sales': current_sales,

            'growth': growth

        })

        previous_sales = current_sales
    valid_growth = [
        item for item in growth_data
        if item['growth'] is not None
    ]

    highest_growth = max(
        valid_growth,
        key=lambda x: x['growth']
    )

    lowest_growth = min(
        valid_growth,
        key=lambda x: x['growth']
    )

    average_growth = sum(
        item['growth']
        for item in valid_growth
    ) / len(valid_growth)
    context = {

        'growth_data': growth_data,

        'highest_growth': highest_growth,

        'lowest_growth': lowest_growth,

        'average_growth': average_growth,

    }
    return render(

        request,

        'analyst/growth_analysis.html',

        context

    )

def revenue_analysis(request):
    total_revenue = SalesData.objects.aggregate(
    total=Sum('weekly_sales')
    )['total'] or 0

    average_revenue = SalesData.objects.aggregate(
        avg=Avg('weekly_sales')
    )['avg'] or 0

    highest_revenue = SalesData.objects.aggregate(
        high=Max('weekly_sales')
    )['high'] or 0

    lowest_revenue = SalesData.objects.aggregate(
        low=Min('weekly_sales')
    )['low'] or 0
    monthly_revenue = (
        SalesData.objects
        .values('month')
        .annotate(total_revenue=Sum('weekly_sales'))
        .order_by('month')
    )
    month_names = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    revenue_summary = []

    for item in monthly_revenue:

        revenue_summary.append({

            'month': month_names[item['month']],

            'revenue': item['total_revenue']

        })
    top_revenue = sorted(
        revenue_summary,
        key=lambda x: x['revenue'],
        reverse=True
    )[:5]
    chart_labels = [item['month'] for item in revenue_summary]

    chart_values = [
        float(item['revenue'])
        for item in revenue_summary
    ]
    context = {

        'total_revenue': total_revenue,
        'average_revenue': average_revenue,
        'highest_revenue': highest_revenue,
        'lowest_revenue': lowest_revenue,

        'revenue_summary': revenue_summary,

        'top_revenue': top_revenue,

        'chart_labels': json.dumps(chart_labels),
        'chart_values': json.dumps(chart_values),

    }
    return render(

        request,

        'analyst/revenue_analysis.html',

        context

    )

from django.db.models import Sum, Avg, Count
import json

def store_performance(request):

    store_summary = (
        SalesData.objects
        .values('store')
        .annotate(
            total_sales=Sum('weekly_sales'),
            average_sales=Avg('weekly_sales'),
            total_records=Count('id')
        )
        .order_by('-total_sales')
    )

    best_store = store_summary.first()

    lowest_store = store_summary.last()

    total_stores = store_summary.count()

    average_store_sales = (
        sum(item['total_sales'] for item in store_summary) / total_stores
        if total_stores > 0 else 0
    )

    top_stores = store_summary[:10]

    bottom_stores = store_summary.order_by('total_sales')[:10]

    chart_labels = [
        f"Store {item['store']}"
        for item in top_stores
    ]

    chart_values = [
        float(item['total_sales'])
        for item in top_stores
    ]

    context = {

        'best_store': best_store,

        'lowest_store': lowest_store,

        'total_stores': total_stores,

        'average_store_sales': average_store_sales,

        'top_stores': top_stores,

        'bottom_stores': bottom_stores,

        'store_summary': store_summary,

        'chart_labels': json.dumps(chart_labels),

        'chart_values': json.dumps(chart_values),

    }

    return render(
        request,
        'analyst/store_performance.html',
        context
    )