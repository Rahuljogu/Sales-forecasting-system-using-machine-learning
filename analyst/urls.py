from django.urls import path
from . import views

urlpatterns = [
    path('analyst-dashboard/', views.analyst_dashboard, name='analyst_dashboard'),
    path("sales-trends/",views.sales_trends,name="sales_trends"),
    path('growth-analysis/',views.growth_analysis,name='growth_analysis'),
    path('revenue-analysis/',views.revenue_analysis,name='revenue_analysis'),
    path('store-performance/',views.store_performance,name='store_performance'),
]
