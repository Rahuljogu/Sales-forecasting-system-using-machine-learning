from django.urls import path
from . import views

urlpatterns = [
    
    path('admin-dashboard/',views.admin_dashboard,name='admin_dashboard'),
    path('users/', views.users, name='users'),
    path('users/activate/<int:user_id>/', views.activate_user, name='activate_user'),
    path('users/deactivate/<int:user_id>/', views.deactivate_user, name='deactivate_user'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),

    path('sales-data/', views.sales_data, name='sales_data'),
    
    path('upload-dataset/', views.upload_dataset, name='upload_dataset'),
    
    
    path('predictions/',views.predictions,name='predictions'),
    
    path('reports/', views.reports, name='reports'),

    path('analytics/',views.analytics,name='analytics'),
    path('model-training/',views.train_model,name='model_training'),
    path('prediction-history/',views.prediction_history,name='prediction_history'),
]