from django.urls import path
from . import views

urlpatterns = [
    path("",views.manager_dashboard,name="manager_dashboard"),
    path('manager-analytics/', views.manager_analytics, name='manager_analytics'),
    path("manager-predictions/",views.predictions,name="manager_predictions"),
    path("manager-prediction-history/",views.prediction_history,name="manager_prediction_history"),
]
