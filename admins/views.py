# Create your views here.
import os

import joblib
import numpy as np
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Max, Min, Sum
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Profile

from .forms import DatasetUploadForm
from .model_training import (
    fit_model as fit_model_helper,
    load_dataset as load_dataset_helper,
    preprocess_data,
    save_model as save_model_helper,
    split_dataset,
    train_model as evaluate_model,
)
from .models import Dataset, PredictionHistory, SalesData

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(
    BASE_DIR,
    'models',
    'sales_prediction_model.pkl'
)

def admin_dashboard(request):
    total_users = User.objects.count()
    total_sales = SalesData.objects.count()

    total_revenue = SalesData.objects.aggregate(
        total=Sum("weekly_sales")
    )["total"] or 0

    context = {
        "total_users": total_users,
        "total_sales": total_sales,
        "total_revenue": total_revenue,
        "accuracy": "96%"   
    }

    return render(request, "admin_dashboard.html", context)


@login_required(login_url='login')
def analyst_dashboard(request):
    return render(request, 'analyst_dashboard.html')



@login_required(login_url='login')
def users(request):

    profiles = Profile.objects.select_related('user').exclude(role__iexact='admin')

    context = {
        'profiles': profiles
    }

    return render(request, 'admin/users.html', context)

@login_required(login_url='login')
def activate_user(request, user_id):
    if request.method != 'POST':
        return redirect('users')

    profile = get_object_or_404(Profile, user__id=user_id)
    # Do not allow activating Admin role from this management table
    if getattr(profile, 'role', '').lower() == 'admin':
        return redirect('users')
    profile.is_approved = True
    profile.user.is_active = True
    profile.user.save()
    profile.save()
    return redirect('users')

@login_required(login_url='login')
def deactivate_user(request, user_id):
    if request.method != 'POST':
        return redirect('users')

    profile = get_object_or_404(Profile, user__id=user_id)
    # Prevent deactivating Admin role from this management table
    if getattr(profile, 'role', '').lower() == 'admin':
        return redirect('users')
    profile.user.is_active = False
    profile.user.save()
    return redirect('users')

@login_required(login_url='login')
def delete_user(request, user_id):
    if request.method != 'POST':
        return redirect('users')

    profile = get_object_or_404(Profile, user__id=user_id)
    # Prevent deleting Admin role from this management table
    if getattr(profile, 'role', '').lower() == 'admin':
        return redirect('users')
    profile.user.delete()
    return redirect('users')
def sales_data(request):

    sales_records = SalesData.objects.all()[:10]

    context = {
        'sales_records': sales_records
    }

    return render(
        request,
        'admin/sales_data.html',
        context
    )

def upload_dataset(request):

    preview = None
    error = None

    if request.method == 'POST':

        form = DatasetUploadForm(
            request.POST,
            request.FILES
        )

        if form.is_valid():

            dataset = form.save()
            dataset_path = dataset.csv_file.path

            request.session['dataset_path'] = dataset_path

            df = pd.read_csv(dataset_path)

            preview = df.head(10).to_html(
                classes='table table-bordered',
                index=False
            )

            try:
                SalesData.objects.all().delete()

                sales_records = []
                integer_fields = {'store', 'holiday_flag', 'year', 'month', 'week', 'quarter'}

                for _, row in df.iterrows():
                    try:
                        record_data = {}

                        for csv_column, field_name in {
                            'Store': 'store',
                            'Weekly_Sales': 'weekly_sales',
                            'Holiday_Flag': 'holiday_flag',
                            'Temperature': 'temperature',
                            'Fuel_Price': 'fuel_price',
                            'CPI': 'cpi',
                            'Unemployment': 'unemployment',
                            'Year': 'year',
                            'Month': 'month',
                            'Week': 'week',
                            'Quarter': 'quarter',
                        }.items():
                            if csv_column in df.columns and pd.notna(row[csv_column]):
                                value = row[csv_column]
                                if field_name in integer_fields:
                                    record_data[field_name] = int(value)
                                else:
                                    record_data[field_name] = float(value)
                            else:
                                record_data[field_name] = 0 if field_name in integer_fields else 0.0

                        sales_records.append(SalesData(**record_data))
                    except Exception as e:
                        raise

                if sales_records:
                    SalesData.objects.bulk_create(sales_records)
                else:
                    error = 'No valid rows were imported from the uploaded CSV.'
            except Exception as exc:
                error = f'CSV import failed: {exc}'

    else:

        form = DatasetUploadForm()

    context = {
        'form': form,
        'preview': preview,
    }

    if error:
        context['error'] = error

    return render(
        request,
        'admin/upload_dataset.html',
        context
    )

def analytics(request):

    sales_data = SalesData.objects.all()

    if not sales_data.exists():

        return render(
            request,
            'admin/analytics.html',
            {
                'error': 'No sales data available.'
            }
        )

    context = {

        'total_records': sales_data.count(),

        'total_columns': len(SalesData._meta.fields),

        'columns': [
            field.verbose_name.title()
            for field in SalesData._meta.fields
        ],

        'avg_sales': round(
            sales_data.aggregate(
                Avg('weekly_sales')
            )['weekly_sales__avg'],
            2
        ),

        'max_sales': round(
            sales_data.aggregate(
                Max('weekly_sales')
            )['weekly_sales__max'],
            2
        ),

        'min_sales': round(
            sales_data.aggregate(
                Min('weekly_sales')
            )['weekly_sales__min'],
            2
        )

    }

    return render(
        request,
        'admin/analytics.html',
        context
    )

def train_model(request):
    dataset_path = request.session.get('dataset_path')
    context = {
        'active_tab': 'upload-section'
    }

    if request.method == 'POST':
        action = request.POST.get('action')
        active_tab = {
            'upload': 'upload-section',
            'load': 'loading-section',
            'preprocess': 'preprocessing-section',
            'split': 'splitting-section',
            'fit': 'fitting-section',
            'train': 'train-section',
            'save': 'save-section',
        }.get(action, 'upload-section')

        context['active_tab'] = active_tab

        if action == 'upload':
            form = DatasetUploadForm(request.POST, request.FILES)
            if form.is_valid():
                dataset = form.save()
                dataset_path = dataset.csv_file.path
                request.session['dataset_path'] = dataset_path

                df = pd.read_csv(dataset_path)
                # Delete old SalesData
                SalesData.objects.all().delete()

                # Convert Date column into required fields
                df["Date"] = pd.to_datetime(df["Date"],dayfirst=True)

                df["Year"] = df["Date"].dt.year
                df["Month"] = df["Date"].dt.month
                df["Week"] = df["Date"].dt.isocalendar().week.astype(int)
                df["Quarter"] = df["Date"].dt.quarter

                sales_records = []

                for _, row in df.iterrows():

                    sales_records.append(

                        SalesData(

                            store=int(row["Store"]),
                            weekly_sales=float(row["Weekly_Sales"]),
                            holiday_flag=int(row["Holiday_Flag"]),
                            temperature=float(row["Temperature"]),
                            fuel_price=float(row["Fuel_Price"]),
                            cpi=float(row["CPI"]),
                            unemployment=float(row["Unemployment"]),
                            year=int(row["Year"]),
                            month=int(row["Month"]),
                            week=int(row["Week"]),
                            quarter=int(row["Quarter"])

                        )

                    )

                SalesData.objects.bulk_create(sales_records)
                context.update({
                    'upload_message': 'Dataset uploaded successfully.',
                    'total_records': len(df),
                    'columns': df.columns.tolist(),
                    'dataset_name': dataset.name,
                    'form': form,
                })
            else:
                context['form'] = form

        else:
            if not dataset_path or not os.path.exists(dataset_path):
                context['error'] = 'Please upload a dataset first.'
            else:
                df = load_dataset_helper(dataset_path)
                
                if action == 'load':
                    context.update({
                        'load_message': 'Dataset loaded successfully.',
                        'total_records': len(df),
                        'columns': df.columns.tolist(),
                        'preview': df.head(5).to_html(classes='table table-bordered', index=False),
                    })

                elif action == 'preprocess':
                    X, y = preprocess_data(df)
                    request.session['preprocess_rows'] = int(X.shape[0])
                    request.session['preprocess_features'] = int(X.shape[1])
                    context.update({
                        'preprocess_message': 'Data preprocessing completed.',
                        'num_rows': int(X.shape[0]),
                        'num_features': int(X.shape[1]),
                        'target_name': 'Weekly_Sales',
                    })

                elif action == 'split':
                    X, y = preprocess_data(df)
                    X_train, X_test, y_train, y_test = split_dataset(X, y)
                    request.session['split_train'] = int(X_train.shape[0])
                    request.session['split_test'] = int(X_test.shape[0])
                    request.session['split_features'] = int(X_train.shape[1])
                    context.update({
                        'split_message': 'Dataset split successfully.',
                        'training_records': int(X_train.shape[0]),
                        'testing_records': int(X_test.shape[0]),
                        'feature_count': int(X_train.shape[1]),
                        'split_ratio': '80 : 20',
                    })

                elif action == 'fit':
                    X, y = preprocess_data(df)
                    X_train, X_test, y_train, y_test = split_dataset(X, y)

                    models = fit_model_helper(X_train, y_train)

                    context.update({
                        'fit_message': 'All models fitted successfully.',
                        'model_status': 'Decision Tree, Random Forest and XGBoost trained.'
                    })

                elif action == 'train':
                    X, y = preprocess_data(df)
                    X_train, X_test, y_train, y_test = split_dataset(X, y)

                    models = fit_model_helper(X_train, y_train)

                    results, best_model, best_algorithm = evaluate_model(
                        models,
                        X_train,
                        X_test,
                        y_train,
                        y_test
                    )

                    request.session['best_algorithm'] = best_algorithm

                    context.update({
                        'train_message': 'Model comparison completed.',
                        'model_status': 'All models evaluated.',
                        'results': results,
                        'best_algorithm': best_algorithm
                    })

                elif action == 'save':

                    X, y = preprocess_data(df)
                
                    X_train, X_test, y_train, y_test = split_dataset(X, y)
                
                    models = fit_model_helper(X_train, y_train)
                
                    results, best_model, best_algorithm = evaluate_model(
                        models,
                        X_train,
                        X_test,
                        y_train,
                        y_test
                    )
                
                    save_path = save_model_helper(best_model)
                
                    request.session['model_path'] = save_path
                
                    context.update({
                        'save_message': f'{best_algorithm} model saved successfully.',
                        'model_status': 'Saved Successfully'
                    })
                else:
                    context['error'] = 'Invalid model training action.'

    if 'form' not in context:
        context['form'] = DatasetUploadForm()

    return render(
        request,
        'admin/model_training.html',
        context
    )

def predictions(request):

    prediction = None
    error = None

    if request.method == "POST":

        try:

            model = joblib.load(MODEL_PATH)

            
            store = int(request.POST['store'])
            holiday_flag = int(request.POST['holiday_flag'])
            temperature = float(request.POST['temperature'])
            fuel_price = float(request.POST['fuel_price'])
            cpi = float(request.POST['cpi'])
            unemployment = float(request.POST['unemployment'])
            year = int(request.POST['year'])
            month = int(request.POST['month'])
            week = int(request.POST['week'])
            quarter = int(request.POST['quarter'])

            data = np.array([
                [
                    store,
                    holiday_flag,
                    temperature,
                    fuel_price,
                    cpi,
                    unemployment,
                    year,
                    month,
                    week,
                    quarter
                ]
            ])

            prediction = model.predict(data)[0]

            prediction = round(float(prediction), 2)

            PredictionHistory.objects.create(
                store=store,
                holiday_flag=holiday_flag,
                temperature=temperature,
                fuel_price=fuel_price,
                cpi=cpi,
                unemployment=unemployment,
                year=year,
                month=month,
                week=week,
                quarter=quarter,
                predicted_sales=prediction
            )

        except Exception as e:

            error = str(e)

            

    return render(
        request,
        'admin/predictions.html',
        {
            'prediction': prediction,
            'error': error
        }
    )

from .models import PredictionHistory
def prediction_history(request):

    predictions = PredictionHistory.objects.all().order_by('-created_at')

    return render(
        request,
        'admin/prediction_history.html',
        {
            'predictions': predictions
        }
    )




def reports(request):

    total_users = User.objects.count()

    total_predictions = PredictionHistory.objects.count()

    avg_sales = PredictionHistory.objects.aggregate(
        Avg('predicted_sales')
    )['predicted_sales__avg']

    max_sales = PredictionHistory.objects.aggregate(
        Max('predicted_sales')
    )['predicted_sales__max']

    min_sales = PredictionHistory.objects.aggregate(
        Min('predicted_sales')
    )['predicted_sales__min']

    context = {
        'total_users': total_users,
        'total_predictions': total_predictions,
        'avg_sales': avg_sales,
        'max_sales': max_sales,
        'min_sales': min_sales,
    }

   

    return render(
        request,
        'admin/reports.html',
        context
    )