from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register,name='register'),
    path('login/',views.login_view,name='login'),
    path('approve-user/<int:profile_id>/',views.approve_user,name='approve_user'),
    path('logout/',views.logout_view,name='logout'),

]