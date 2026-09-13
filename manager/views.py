from django.shortcuts import render
from admins.models import PredictionHistory, SalesData


from django.db.models import Sum

def manager_dashboard(request):

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
        "manager/dashboard.html",
        context
    )

from django.db.models import Sum
from admins.models import SalesData
import json

def manager_analytics(request):

    total_revenue = SalesData.objects.aggregate(
        total=Sum("weekly_sales")
    )["total"] or 0

    total_quantity = SalesData.objects.count()

    store_sales = (
        SalesData.objects
        .values("store")
        .annotate(total_sales=Sum("weekly_sales"))
        .order_by("store")
    )

    store_labels = [
        str(item["store"])
        for item in store_sales
    ]

    store_values = [
        float(item["total_sales"])
        for item in store_sales
    ]

    context = {
        "total_revenue": total_revenue,
        "total_quantity": total_quantity,
        "store_sales": store_sales,
        "region_labels": json.dumps(store_labels),
        "region_values": json.dumps(store_values),
    }

    return render(
        request,
        "manager/analytics.html",
        context
    )

from .forms import PredictionForm
from .model_predict import predict_sales

def predictions(request):

    prediction = None

    form = PredictionForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():

            input_data = [

                form.cleaned_data["store"],
                form.cleaned_data["holiday_flag"],
                form.cleaned_data["temperature"],
                form.cleaned_data["fuel_price"],
                form.cleaned_data["cpi"],
                form.cleaned_data["unemployment"],
                form.cleaned_data["year"],
                form.cleaned_data["month"],
                form.cleaned_data["week"],
                form.cleaned_data["quarter"]

            ]

            prediction = predict_sales(input_data)
            from admins.models import PredictionHistory

            PredictionHistory.objects.create(
            
                store=form.cleaned_data["store"],

                holiday_flag=form.cleaned_data["holiday_flag"],

                temperature=form.cleaned_data["temperature"],

                fuel_price=form.cleaned_data["fuel_price"],

                cpi=form.cleaned_data["cpi"],

                unemployment=form.cleaned_data["unemployment"],

                year=form.cleaned_data["year"],

                month=form.cleaned_data["month"],

                week=form.cleaned_data["week"],

                quarter=form.cleaned_data["quarter"],

                predicted_sales=prediction

            )

    return render(

        request,

        "manager/predictions.html",

        {

            "form": form,

            "prediction": prediction

        }

    )

from admins.models import PredictionHistory

def prediction_history(request):

    predictions = PredictionHistory.objects.all().order_by('-created_at')

    search = request.GET.get('search')

    if search:
        predictions = predictions.filter(store=search)

    context = {
        'predictions': predictions,
        'search': search
    }

    return render(
        request,
        'manager/prediction_history.html',
        context
    )