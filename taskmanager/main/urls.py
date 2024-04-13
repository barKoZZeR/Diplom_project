from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView


urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.index, name='home'),
    path('my-plan', views.my_plan, name='my_plan'),
    path('create', views.create, name='create'),
    path('employers-plans', views.employers_plans, name='employers_plans'),
    path('profile/', views.profile, name='profile'),
    path('employee-profile/<int:user_id>/', views.employee_profile, name='employee_profile'),
    path('create-plan-for-employee/<int:user_id>/', views.create_plan_for_employee, name='create_plan_for_employee'),
    path('plan/<int:plan_id>/add_action/', views.add_action, name='add_action'),
    path('plan/<int:plan_id>/', views.view_plan, name='view_plan'),
]